# jetbrains-issues-dataset

It's a library to retrieve dataset of JetBrains issues

## Sample dataset retrieval
To retrieve activities and restore issues to defined state use on of the methods: 
* `jetbrains_issues_dataset/idea/idea_data_set.py#idea_2019_03_20_to_idea_2020_03_20(snapshot_strategy)`.
* `jetbrains_issues_dataset.idea.idea_data_set.idea_2018_10_15_to_idea_2020_10_15(snapshot_strategy)`.

Example:
```python
from jetbrains_issues_dataset.idea.issue_created_snapshot_strategy import IssueCreatedSnapshotStrategy
from jetbrains_issues_dataset.idea.idea_data_set import idea_2018_10_15_to_idea_2020_10_15
issues = idea_2018_10_15_to_idea_2020_10_15(IssueCreatedSnapshotStrategy())
```

Or just check the file [examples/first_assignee.py](examples/first_assignee.py)

## Create your custom dataset

For simple adjustments, you can use the provided command line interface by calling `youtrack_downloader`. E.g., to collect only current states of very annoying Rider issues for the year 2020, use the following:
```shell
youtrack_downloader --start 2020-01-01 --end 2021-01-01 --server-address YOUR_SERVER_ADDRESS --access-token YOUR_ACCESS_TOKEN --query project: Rider User priority: \{Very annoying\}
```
See all CLI options in `youtrack_downloader --help`.

For more complicated adjustments (e.g., adding or removing field information, selecting specific types of activity items), tune the downloader script [jetbrains_issues_dataset/youtrack_loader/download_activities.py](jetbrains_issues_dataset/youtrack_loader/download_activities.py) and YouTrack client [jetbrains_issues_dataset/youtrack_loader/youtrack.py](jetbrains_issues_dataset/youtrack_loader/youtrack.py). 
It could be useful to read [Youtrack API Reference](https://www.jetbrains.com/help/youtrack/standalone/youtrack-rest-api-reference.html)
Also do not run downloader on production server.

## Restore issues for another project (not for #IDEA)
The class `ActivityManager` is responsible for handling project specific (custom) fields. See example implementation for IDEA: `IdeaActivityManager`
Then use `jetbrains_issues_dataset.idea.idea_data_set.load_activities_from_file` and provide file path and `activity manager` for your project.
See the code sample below:
```python
activity_manager = YouProjectActivityManager(snapshot_strategy)
issues = load_activities_from_file('your_project_activity_path.json', activity_manager)
```

## Issue snapshot strategies
At the moment there are 3 snapshot strategy defined:
 * SnapshotStrategy - restores the actual issue states
 * IssueCreatedSnapshotStrategy - restores issue for the moment it was created
 * FirstAssigneeSnapshotStrategy - restores state of the issue to the moment when it first time assigned
 
