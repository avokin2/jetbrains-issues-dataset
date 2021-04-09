import datetime
import sys
from urllib import parse

import urllib3
from dateutil.relativedelta import relativedelta

from jetbrains_issues_dataset.youtrack_loader.youtrack import YouTrack

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_data(youtrack: YouTrack, snapshot_start_time: datetime.datetime, snapshot_end_time: datetime.datetime,
                  issues_snapshot_file: str, activities_snapshot_file: str, query: str, load_issues=True,
                  load_activities=True):
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

    total_issues = 0
    total_activities = 0
    processing_start_time = datetime.datetime.now()
    current_end_date = snapshot_start_time
    while snapshot_start_time < snapshot_end_time:
        current_end_date += relativedelta(weeks=1)
        if current_end_date > snapshot_end_time:
            current_end_date = snapshot_end_time

        start = snapshot_start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end = current_end_date.strftime('%Y-%m-%dT%H:%M:%S')

        print(f"Processing from: {start} to: {end}")
        timed_query = f"{query} created: {start} .. {end}"

        if load_issues:
            n_issues = youtrack.download_issues(parse.quote_plus(timed_query), issues_snapshot_file)
            print(f'Loaded {n_issues} issues')
            total_issues += n_issues

        if load_activities:
            n_activities = youtrack.download_activities(parse.quote_plus(timed_query), activities_snapshot_file)
            print(f'Loaded {n_activities} activities')
            total_activities += n_activities
        snapshot_start_time = current_end_date

    print(f'Loaded {total_issues} issues and {total_activities} activity items '
          f'in {datetime.datetime.now() - processing_start_time:.2f}s')


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
                  query=query, load_issues=not args.no_issues, load_activities=not args.no_activities)


if __name__ == '__main__':
    main()
