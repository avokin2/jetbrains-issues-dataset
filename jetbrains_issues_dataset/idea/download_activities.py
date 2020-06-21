import datetime
import os
from os import path

import urllib3
from dateutil.relativedelta import relativedelta

from jetbrains_issues_dataset.idea.youtrack import YouTrack

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


YOUTRACK_SERVER_URL = "http://youtrack-staging.labs.intellij.net/"

start_date = datetime.datetime.strptime("2019-03-20 00:00:00", '%Y-%m-%d %H:%M:%S')
end_date = datetime.datetime.strptime("2020-03-20 00:00:00", '%Y-%m-%d %H:%M:%S')

start_time = datetime.datetime.now()

youtrack = YouTrack(YOUTRACK_SERVER_URL, None)

if not path.exists('data'):
    os.mkdir('data')

activities_file = 'data/activities.json'
with open('%s' % activities_file, 'w', encoding='utf-8') as writer:
    pass

current_end_date = start_date
while start_date < end_date:
    current_end_date += relativedelta(weeks=1)
    if current_end_date > end_date:
        current_end_date = end_date

    start = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end = current_end_date.strftime('%Y-%m-%dT%H:%M:%S')

    print("Processing from: {} to: {}".format(start, end))
    query = "%23IDEA%20created:%20{}%20..%20{}".format(start, end)
    youtrack.download_activities(query, activities_file)
    start_date = current_end_date

print("Duration: {}".format((datetime.datetime.now() - start_time)))
