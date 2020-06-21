import os
from os import path

import requests
from tqdm import tqdm
import zipfile

from jetbrains_issues_dataset.idea.idea_activity_manager import IdeaActivityManager
from jetbrains_issues_dataset.idea.snapshot_strategy import SnapshotStrategy


def idea_2019_03_20_to_idea_2020_03_20(snapshot_manager=None):
    activities_file_path = "data/idea_activities_2019_03_20_to_2020_03_20.json"
    zip_file_path = activities_file_path + ".zip"
    if not path.exists('data'):
        os.mkdir('data')
    if not path.exists(activities_file_path):
        _download_file('https://github.com/avokin2/datasets/raw/master/youtrack/idea_activities_2019_03_20_to_2020_03_20.json.zip', zip_file_path)
    if not path.exists(zip_file_path):
        raise Exception("Can't download issue activities")

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall("data")

    if not path.exists(activities_file_path):
        raise Exception("Failed to unzip activities file")

    if snapshot_manager is None:
        snapshot_manager = SnapshotStrategy()
    activity_manager = IdeaActivityManager(snapshot_manager)
    activity_manager.load_issues_from_activities_file('data/idea_activities_2019_03_20_to_2020_03_20.json')
    return snapshot_manager.issues


def _download_file(url, destination_path):
    request = requests.get(url, stream=True)
    total_size = int(request.headers.get('content-length', 0))
    progress_indicator = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(destination_path, 'wb') as file:
        for data in request.iter_content(1024):
            progress_indicator.update(len(data))
            file.write(data)
    progress_indicator.close()
    if total_size != 0 and progress_indicator.n != total_size:
        print("error during downloading file {}".format(url))
