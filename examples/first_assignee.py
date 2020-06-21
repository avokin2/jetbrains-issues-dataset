from idea import FirstAssigneeSnapshotStrategy
from idea import idea_2019_03_20_to_idea_2020_03_20

issues = idea_2019_03_20_to_idea_2020_03_20(FirstAssigneeSnapshotStrategy())
print("Successfully retrieved {} issues".format(len(issues)))
