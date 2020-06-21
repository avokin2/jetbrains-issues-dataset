import json


class ActivityManager:
    def __init__(self, snapshot_strategy, custom_field_mapping=None):
        self.snapshot_strategy = snapshot_strategy

        self.issues = {}
        self.simple_value_activity_target_members = []
        self.text_markup_activity_target_members = []
        self.custom_field_activity_target_members = []
        self.activity_types = []

        if custom_field_mapping is None:
            custom_field_mapping = {}
        self.custom_field_mapping = custom_field_mapping

    def load_issues_from_activities_file(self, file_path):
        with open('%s' % file_path, 'r', encoding='utf-8') as reader:
            while True:
                line = reader.readline()
                if line is None or len(line) == 0:
                    break
                activity = json.loads(line)
                self._apply_activity(activity)

        for issue in self.issues.values():
            self.snapshot_strategy.process_previous_attribute_values(issue)

        return self.issues

    @staticmethod
    def _retrieve_field_value(obj, name):
        if obj is not None and len(obj) > 0:
            return obj[0][name]
        else:
            return None

    def _apply_activity(self, activity):
        activity_type = activity['$type']
        if activity_type == 'IssueCreatedActivityItem':
            issue_id = activity['target']['id']

            if issue_id not in self.issues:
                target_issue = activity['target']
                issue = {'id': issue_id, 'id_readable': target_issue['idReadable'], 'summary': target_issue['summary'],
                         'description': target_issue['description'], 'reporter': target_issue['reporter']['login'],
                         'comments': {}}

                for custom_field in target_issue['customFields']:
                    for allowed_custom_field_name, allowed_custom_field_params in self.custom_field_mapping.items():
                        if allowed_custom_field_params['name'] == custom_field['name'].lower():
                            custom_field_value = custom_field['value'][allowed_custom_field_params['field']] \
                                if custom_field['value'] is not None else None
                            issue[custom_field['name'].lower()] = custom_field_value

                self.issues[issue_id] = issue

                if issue is not None:
                    self.snapshot_strategy.process(
                        {'id': issue_id, 'id_readable': target_issue['idReadable'], 'comments': {}})
            else:
                print("Duplicated IssueCreatedActivityItem for issue: {}".format(issue_id))
        else:
            if activity_type == 'SimpleValueActivityItem' or activity_type == 'TextMarkupActivityItem' \
                    or activity_type == 'CustomFieldActivityItem':
                issue_id = activity['target']['id']
                if issue_id not in self.issues:
                    # issue was moved to current project
                    return
                target_member = activity['targetMember']

                removed = activity['removed'] if 'removed' in activity else None
                added = activity['added'] if 'added' in activity else None

                if activity_type == 'CustomFieldActivityItem':
                    if target_member in self.custom_field_mapping:
                        original_target_member = target_member
                        target_member = self.custom_field_mapping[target_member]['name']
                    else:
                        return

                    removed = self._retrieve_field_value(removed,
                                                         self.custom_field_mapping[original_target_member]['field'])
                    added = self._retrieve_field_value(added,
                                                       self.custom_field_mapping[original_target_member]['field'])
                else:
                    if removed is not None and len(removed) == 0:
                        removed = None
                    if added is not None and len(added) == 0:
                        added = None

                if removed is not None:
                    self.snapshot_strategy.process_previous_attribute_values({'id': issue_id, target_member: removed})
                    self.snapshot_strategy.process({'id': issue_id, target_member: None})
                if added is not None:
                    self.snapshot_strategy.process({'id': issue_id, target_member: added})

            elif activity_type == 'CommentActivityItem':
                if len(activity['removed']) > 0:
                    raise NotImplementedError
                comment = activity['target']
                issue_id = comment['issue']['id']
                if issue_id not in self.issues:
                    # issue was moved to current project
                    return

                self.snapshot_strategy.process_added_comment(
                    {'issue_id': issue_id, 'id': comment['id'], 'text': comment['text']})
