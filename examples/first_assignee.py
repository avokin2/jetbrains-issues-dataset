from jetbrains_issues_dataset.idea.first_assignee_snapshot_strategy import FirstAssigneeSnapshotStrategy
from jetbrains_issues_dataset.idea.idea_data_set import idea_2019_03_20_to_idea_2020_03_20

issues = idea_2019_03_20_to_idea_2020_03_20(FirstAssigneeSnapshotStrategy())
print("Successfully retrieved {} issues".format(len(issues)))
