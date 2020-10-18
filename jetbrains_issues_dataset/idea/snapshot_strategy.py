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

    def process_issue_created(self, issue, final_issue_state):
        if issue['id'] not in self.issues:
            self.issues[issue['id']] = issue.copy()

        snapshot_issue = self._get_snapshot_issue_to_process(issue['id'])
        if snapshot_issue is None:
            return

        for key, value in issue.items():
            snapshot_issue[key] = value

        self.process(issue, final_issue_state)

    def process_added_field(self, id, field, value, final_issue_state, timestamp):
        self.process({'id': id, field: value, 'timestamp': timestamp}, final_issue_state)
        snapshot_issue = self._get_snapshot_issue_to_process(id)
        if snapshot_issue is None:
            return

        if field not in snapshot_issue:
            snapshot_issue[field] = value
        else:
            if isinstance(value, list):
                snapshot_issue[field].extend(value)
            else:
                snapshot_issue[field] = value

    def process_removed_field(self, id, field, removed_value, final_issue_state):
        self.process({'id': id, field: removed_value}, final_issue_state)
        self.process_previous_attribute_values({'id': id, field: removed_value})

        snapshot_issue = self._get_snapshot_issue_to_process(id)
        if snapshot_issue is None:
            return

        if field in snapshot_issue:
            if isinstance(removed_value, list):
                for rv in removed_value:
                    if rv in snapshot_issue[field]:
                        snapshot_issue[field].remove(rv)
            else:
                snapshot_issue[field] = None

    def process_added_comment(self, comment):
        snapshot_issue = self._get_snapshot_issue_to_process(comment['issue_id'])
        if snapshot_issue is None:
            return
        snapshot_issue['comments'][comment['id']] = comment['text']

    def process(self, issue, final_issue_state):
        pass

    def _get_snapshot_issue_to_process(self, issue_id):
        if issue_id not in self.issues:
            return None
        snapshot_issue = self.issues[issue_id]
        if self.is_snapshot_taken(snapshot_issue):
            return None
        return snapshot_issue
