import datetime
import os
from os import path

import urllib3
from dateutil.relativedelta import relativedelta

from jetbrains_issues_dataset.idea.youtrack import YouTrack

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Do not use production server here!
YOUTRACK_SERVER_URL = "https://youtrack-staging.labs.intellij.net/"

snapshot_start_time = datetime.datetime.strptime("2018-10-07 00:00:00", '%Y-%m-%d %H:%M:%S')
snapshot_end_time = datetime.datetime.now()

processing_start_time = datetime.datetime.now()

youtrack = YouTrack(YOUTRACK_SERVER_URL, None)

if not path.exists('data'):
    os.mkdir('data')

snapshot_file = 'data/snapshot.json'
with open('%s' % snapshot_file, 'w', encoding='utf-8') as writer:
    pass

current_end_date = snapshot_start_time
while snapshot_start_time < snapshot_end_time:
    current_end_date += relativedelta(weeks=1)
    if current_end_date > snapshot_end_time:
        current_end_date = snapshot_end_time

    start = snapshot_start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end = current_end_date.strftime('%Y-%m-%dT%H:%M:%S')

    print("Processing from: {} to: {}".format(start, end))
    query = "%23IDEA%20created:%20{}%20..%20{}".format(start, end)
    youtrack.download_issues(query, snapshot_file)
    youtrack.download_activities(query, snapshot_file)
    snapshot_start_time = current_end_date

print("Duration: {}".format((datetime.datetime.now() - processing_start_time)))
