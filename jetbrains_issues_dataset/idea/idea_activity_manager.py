from jetbrains_issues_dataset.idea.activity_manager import ActivityManager


class IdeaActivityManager(ActivityManager):
    def __init__(self, snapshot_strategy):
        super().__init__(snapshot_strategy,
                         custom_field_mapping={'__CUSTOM_FIELD__State_25': {'name': 'state', 'field': 'name', 'multivalue': False},
                                               '__CUSTOM_FIELD__Assignee_30': {'name': 'assignee', 'field': 'login', 'multivalue': False},
                                               '__CUSTOM_FIELD__Subsystem_26': {'name': 'subsystem', 'field': 'name', 'multivalue': False}})
