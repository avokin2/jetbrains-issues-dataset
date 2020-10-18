from jetbrains_issues_dataset.idea.snapshot_strategy import SnapshotStrategy


class IssueCreatedSnapshotStrategy(SnapshotStrategy):
    def is_snapshot_taken(self, issue):
        return True

    def process(self, issue, final_issue_state):
        super().process(issue, final_issue_state)

        snapshot_issue = self.issues[issue['id']]
        if 'assignee' in issue:
            if 'first_assignee' not in snapshot_issue:
                snapshot_issue['first_assignee'] = issue['assignee']
            snapshot_issue['last_assignee'] = issue['assignee']

        if 'fixed_by' not in snapshot_issue:
            if 'state' in issue and issue['state'] == 'Fixed':
                assignee = None
                if 'assignee' in snapshot_issue:
                    assignee = snapshot_issue['last_assignee']
                elif 'assignee' in final_issue_state:
                    assignee = final_issue_state['assignee']
                if assignee is not None:
                    if 'timestamp' in issue:
                        snapshot_issue['fixed_at'] = issue['timestamp']
                    snapshot_issue['fixed_by'] = assignee
