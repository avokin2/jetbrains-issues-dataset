jetbrains-issues-dataset is a library to retrieve dataset of JetBrains issues

To download activities and restore issues to defined state use the method
`jetbrains_issues_dataset/idea/idea_data_set.py#idea_2019_03_20_to_idea_2020_03_20(snapshot_strategy)`.

Example:
```
from jetbrains_issues_dataset.idea.first_assignee_snapshot_strategy import FirstAssigneeSnapshotStrategy
from jetbrains_issues_dataset.idea.idea_data_set import idea_2019_03_20_to_idea_2020_03_20
issues = idea_2019_03_20_to_idea_2020_03_20(FirstAssigneeSnapshotStrategy())
```

Or just check the file "examples/first_assignee.py"

To create your custom dataset just tune the file "jetbrains_issues_dataset/idea/download_activities.py"
It could be useful to read Youtrack API Reference: https://www.jetbrains.com/help/youtrack/standalone/youtrack-rest-api-reference.html
Also do not run downloader on production server.

At the moment there are 2 snapshot strategy defined:
 * SnapshotStrategy - restores actual issue states
 * FirstAssigneeSnapshotStrategy - restores state of the issue to the moment when it first time assigned
