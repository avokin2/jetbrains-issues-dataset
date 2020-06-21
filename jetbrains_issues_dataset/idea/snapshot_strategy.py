class SnapshotStrategy:
    def __init__(self):
        self.issues = {}

    def is_snapshot_taken(self, issue):
        return False

    def process_previous_attribute_values(self, issue):
        if issue['id'] not in self.issues:
            return
        snapshot_issue = self.issues[issue['id']]
        for key, value in issue.items():
            if key not in snapshot_issue:
                snapshot_issue[key] = value

    def process(self, issue):
        if issue['id'] not in self.issues:
            self.issues[issue['id']] = issue.copy()

        snapshot_issue = self._get_snapshot_issue_to_process(issue['id'])
        if snapshot_issue is None:
            return

        for key, value in issue.items():
            snapshot_issue[key] = value

    def process_added_comment(self, comment):
        snapshot_issue = self._get_snapshot_issue_to_process(comment['issue_id'])
        if snapshot_issue is None:
            return
        snapshot_issue['comments'][comment['id']] = comment['text']

    def _get_snapshot_issue_to_process(self, issue_id):
        if issue_id not in self.issues:
            return None
        snapshot_issue = self.issues[issue_id]
        if self.is_snapshot_taken(snapshot_issue):
            return None
        return snapshot_issue
