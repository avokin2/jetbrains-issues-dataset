import os
from os import path

import requests
from tqdm import tqdm
import zipfile

from jetbrains_issues_dataset.idea.idea_activity_manager import IdeaActivityManager
from jetbrains_issues_dataset.idea.snapshot_strategy import SnapshotStrategy


def idea_2019_03_20_to_idea_2020_03_20(snapshot_strategy=None):
    if snapshot_strategy is None:
        snapshot_strategy = SnapshotStrategy()
    activity_manager = IdeaActivityManager(snapshot_strategy)
    return load_activities_from_file('idea_activities_2019_03_20_to_2020_03_20.json', activity_manager)


def idea_2018_10_15_to_idea_2020_10_15(snapshot_strategy=None):
    if snapshot_strategy is None:
        snapshot_strategy = SnapshotStrategy()
    activity_manager = IdeaActivityManager(snapshot_strategy)
    return load_activities_from_file('idea_activities_2018_10_15_to_2020_10_15.json', activity_manager)


def load_activities_from_file(file_name: str, activity_manager):
    activities_file_path = "data/" + file_name
    if not path.exists('data'):
        os.mkdir('data')
    if not path.exists(activities_file_path):
        zip_file_path = activities_file_path + ".zip"
        _download_file(
            'https://github.com/avokin2/datasets/raw/master/youtrack/' + file_name + '.zip',
            zip_file_path)
        if not path.exists(zip_file_path):
            raise Exception("Can't download issue activities")

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall("data")

    if not path.exists(activities_file_path):
        raise Exception("Failed to unzip activities file")

    activity_manager.load_issues_from_activities_file(activities_file_path)
    return activity_manager.snapshot_strategy.issues


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
