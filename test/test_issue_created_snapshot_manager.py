import datetime
from unittest import TestCase

from jetbrains_issues_dataset.idea.idea_activity_manager import IdeaActivityManager
from jetbrains_issues_dataset.idea.issue_created_snapshot_strategy import IssueCreatedSnapshotStrategy


class TestIssueCreatedSnapshotStrategy(TestCase):
    def test_fields_missed_in_activities(self):
        snapshot_strategy = IssueCreatedSnapshotStrategy()
        activity_manager = IdeaActivityManager(snapshot_strategy)
        activity_manager.load_issues_from_activities_file('data/missed_activities.json')

        issue = list(snapshot_strategy.issues.values())[0]
        self.assertEqual(issue['fixed_by'], 'assignee_developer')
        self.assertEqual(issue['fixed_at'], datetime.datetime(2020, 10, 6, 21, 45, 26))

    def test_all_main_field_presence(self):
        snapshot_strategy = IssueCreatedSnapshotStrategy()
        activity_manager = IdeaActivityManager(snapshot_strategy)
        activity_manager.load_issues_from_activities_file('data/missed_activities.json')

        issue = list(snapshot_strategy.issues.values())[0]
        self.assertTrue('summary' in issue)
        self.assertTrue('description' in issue)
        self.assertTrue('state' in issue)
        self.assertTrue('reporter' in issue)

    def test_read_all(self):
        snapshot_strategy = IssueCreatedSnapshotStrategy()
        activity_manager = IdeaActivityManager(snapshot_strategy)
        activity_manager.load_issues_from_activities_file('data/snapshot.json')

        self.assertEqual(145, len(snapshot_strategy.issues.values()))

