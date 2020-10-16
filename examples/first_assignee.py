from jetbrains_issues_dataset.idea.idea_data_set import idea_2018_10_15_to_idea_2020_10_15
from jetbrains_issues_dataset.idea.first_assignee_snapshot_strategy import FirstAssigneeSnapshotStrategy

issues = idea_2018_10_15_to_idea_2020_10_15(FirstAssigneeSnapshotStrategy())
print("Successfully retrieved {} issues".format(len(issues)))
