from jetbrains_issues_dataset.idea.issue_created_snapshot_strategy import IssueCreatedSnapshotStrategy


class FirstAssigneeSnapshotStrategy(IssueCreatedSnapshotStrategy):
    def is_snapshot_taken(self, issue):
        return 'first_assignee' in issue
