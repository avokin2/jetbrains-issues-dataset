from jetbrains_issues_dataset.idea.snapshot_strategy import SnapshotStrategy


class IssueCreatedSnapshotStrategy(SnapshotStrategy):
    def is_snapshot_taken(self, issue):
        return True

    def process(self, issue):
        super().process(issue)

        snapshot_issue = self.issues[issue['id']]
        if 'assignee' in issue:
            if 'first_assignee' not in snapshot_issue:
                snapshot_issue['first_assignee'] = issue['assignee']
            snapshot_issue['last_assignee'] = issue['assignee']

        if 'fixed_by' not in snapshot_issue:
            if 'state' in issue and issue['state'] == 'Fixed':
                if 'assignee' in snapshot_issue:
                    snapshot_issue['fixed_by'] = snapshot_issue['last_assignee']

