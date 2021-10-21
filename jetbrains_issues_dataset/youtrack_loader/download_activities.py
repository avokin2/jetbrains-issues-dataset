import datetime
import sys
from urllib import parse

import urllib3
from dateutil.relativedelta import relativedelta
import logging

from jetbrains_issues_dataset.youtrack_loader.youtrack import YouTrack

logging.basicConfig(format='%(asctime)s %(message)s', filename='download.log', level=getattr(logging, 'DEBUG'))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_data(youtrack: YouTrack, snapshot_start_time: datetime.datetime, snapshot_end_time: datetime.datetime,
                  issues_snapshot_file: str, activities_snapshot_file: str, query: str, load_issues=True,
                  load_activities=True, direction='asc'):
    """
    Most parameters have reasonable defaults set below in the CLI argument parser. Minimum working command from CLI if
    working from source:
    PYTHONPATH="$PYTHONPATH:." python ./jetbrains_issues_dataset/idea/download_activities.py --start 2021-01-01 --access-token YOUR_TOKEN
    :param youtrack: instance of the YouTrack client
    :param snapshot_start_time: earliest possible issue creation timestamp
    :param snapshot_end_time: latest possible issue creation timestamp
    :param issues_snapshot_file: where to write issues; can be the same as `activities_snapshot_file`
    :param activities_snapshot_file: where to write activity items; can be the same as `issues_snapshot_file`
    :param query: query to filter issues; e.g., use `#IDEA` to obtain all IDEA issues
    :param load_issues: whether to load current issue states
    :param load_activities: whether to load activities
    """
    with open(issues_snapshot_file, 'w', encoding='utf-8') as writer:
        pass
    with open(activities_snapshot_file, 'w', encoding='utf-8') as writer:
        pass

    assert snapshot_start_time < snapshot_end_time, f'No issues created after {snapshot_start_time} and before {snapshot_end_time}'
    if direction == 'asc':
        direction_flag = 1
    elif direction == 'desc':
        direction_flag = -1
        snapshot_start_time, snapshot_end_time = snapshot_end_time, snapshot_start_time
    else:
        raise ValueError(f'direction must be either `asc` or `desc`; `{direction}` not recognized')

    total_issues = 0
    total_activities = 0
    processing_start_time = datetime.datetime.now()
    current_end_date = snapshot_start_time
    while (direction_flag > 0 and snapshot_start_time < snapshot_end_time) or ((direction_flag < 0 and snapshot_start_time > snapshot_end_time)):
        current_end_date += relativedelta(weeks=1 * direction_flag)
        if (direction_flag > 0 and current_end_date > snapshot_end_time) or (direction_flag < 0 and current_end_date < snapshot_end_time):
            current_end_date = snapshot_end_time

        start = snapshot_start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end = current_end_date.strftime('%Y-%m-%dT%H:%M:%S')

        timed_query = f"{query} updated: {start} .. {end}"
        logging.info(f"Processing from: {start} to: {end}, query: {timed_query}")

        if load_issues:
            issues = youtrack.download_issues(parse.quote_plus(timed_query), issues_snapshot_file, return_ids=True)
            logging.info(f'Loaded {len(issues)} issues')
            total_issues += len(issues)
        else:
            n_issues = 1

        if load_activities and len(issues) > 0:
            # n_activities = youtrack.download_activities(parse.quote_plus(timed_query), activities_snapshot_file)
            n_activities = youtrack.download_activities_per_issue(issues, activities_snapshot_file)
            logging.info(f'Loaded {n_activities} activities')
            total_activities += n_activities
        snapshot_start_time = current_end_date

    logging.info(f'Loaded {total_issues} issues and {total_activities} activity items '
          f'in {str(datetime.datetime.now() - processing_start_time)}')


def cur_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def main():
    import argparse
    import os
    import re

    parser = argparse.ArgumentParser()

    def youtrack_date(value):
        if isinstance(value, datetime.datetime):
            return value
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'value "{value}" cannot be parsed as YouTrack date')

    parser.add_argument('--start',
                        help="earliest issue creation date in format 1970-01-01T10:00:00 "
                             "(YouTrack search query date format; note the T between date and time)",
                        required=True,
                        type=youtrack_date
                        )
    parser.add_argument('--end',
                        help="latest issue creation date in format 1970-01-01T10:00:00 "
                             "(YouTrack search query date format; note the T between date and time); "
                             "current time by default",
                        required=False,
                        type=youtrack_date,
                        default=datetime.datetime.now()
                        )
    parser.add_argument('--filename',
                        help='name of the file where to store downloaded data; '
                             'filename.issues.json and filename.activities.json will be created; '
                             'by default, generated from ascii symbols of the query'
                        )
    parser.add_argument('--no-issues', help='if specified, current issue states will not be loaded',
                        action='store_true')
    parser.add_argument('--no-activities', help='if specified, activities related to the issue will not be loaded',
                        action='store_true')
    parser.add_argument('--direction', help='download order: asc (from oldest to newest, default) or desc (from newest to oldest)',
                        choices=['asc', 'desc'], default='asc')
    parser.add_argument('--server-address',
                        help='where to download issues from',
                        default='https://youtrack-staging.labs.intellij.net/'
                        )
    parser.add_argument('--access-token',
                        help='access token to the server, either string or path to file with token',
                        required=True
                        )
    parser.add_argument('--query',
                        help='query to filter issues; default is #IDEA',
                        nargs='*',
                        default=['#IDEA']
                        )

    args = parser.parse_args()
    print(args)

    if os.path.exists(args.access_token):
        access_token = open(args.access_token, 'r').read().strip()
    else:
        access_token = args.access_token
    youtrack = YouTrack(args.server_address, access_token)

    query = ' '.join(args.query)

    if args.filename:
        filename = args.filename
    else:
        filename = re.sub(r'[^A-Za-z]+', '_', query).strip('_')
        filename = f'{filename}_{args.start.strftime("%Y%m%d")}_{args.end.strftime("%Y%m%d")}'
    root, ext = os.path.splitext(filename)
    if not ext:
        ext = '.json'
    issues_snapshot_file = f'{root}.issues{ext}'
    activities_snapshot_file = f'{root}.activities{ext}'

    download_data(youtrack=youtrack, snapshot_start_time=args.start, snapshot_end_time=args.end,
                  issues_snapshot_file=issues_snapshot_file, activities_snapshot_file=activities_snapshot_file,
                  query=query, load_issues=not args.no_issues, load_activities=not args.no_activities, direction=args.direction)


if __name__ == '__main__':
    main()
