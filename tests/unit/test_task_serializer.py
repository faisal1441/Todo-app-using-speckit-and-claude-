"""
Unit tests for TaskSerializer and datetime conversion functions.

Tests cover:
- DateTime conversion helpers (to/from ISO 8601)
- Task serialization (Task object to dictionary)
- Task deserialization (dictionary to Task object)
- Validation of task dictionaries
- Round-trip serialization and deserialization
"""

import unittest
from datetime import datetime

from src.models.task import Task
from src.services.task_persistence import (
    TaskSerializer,
    datetime_to_str,
    str_to_datetime,
)


class TestDateTimeConversion(unittest.TestCase):
    """Tests for datetime conversion helper functions."""

    def test_datetime_to_str_with_datetime(self):
        """Test converting datetime object to ISO 8601 string."""
        dt = datetime(2026, 1, 1, 10, 30, 45, 123456)
        result = datetime_to_str(dt)
        self.assertEqual(result, "2026-01-01T10:30:45.123456")

    def test_datetime_to_str_with_none(self):
        """Test converting None returns None."""
        result = datetime_to_str(None)
        self.assertIsNone(result)

    def test_str_to_datetime_with_valid_string(self):
        """Test converting ISO 8601 string to datetime object."""
        s = "2026-01-01T10:30:45.123456"
        result = str_to_datetime(s)
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 45)

    def test_str_to_datetime_with_none(self):
        """Test converting None returns None."""
        result = str_to_datetime(None)
        self.assertIsNone(result)

    def test_str_to_datetime_with_invalid_string(self):
        """Test converting invalid string returns None."""
        result = str_to_datetime("not a datetime")
        self.assertIsNone(result)

    def test_str_to_datetime_with_empty_string(self):
        """Test converting empty string returns None."""
        result = str_to_datetime("")
        self.assertIsNone(result)

    def test_datetime_round_trip(self):
        """Test datetime conversion round-trip preserves value."""
        original = datetime(2026, 1, 15, 14, 45, 30, 999999)
        string = datetime_to_str(original)
        restored = str_to_datetime(string)
        self.assertEqual(original, restored)


class TestTaskToDict(unittest.TestCase):
    """Tests for Task serialization (Task object to dictionary)."""

    def setUp(self):
        """Create a serializer for each test."""
        self.serializer = TaskSerializer()

    def test_serialize_pending_task_without_description(self):
        """Test serializing a pending task without description."""
        task = Task("Buy groceries")
        result = self.serializer.task_to_dict(task)

        self.assertEqual(result['id'], task.id)
        self.assertEqual(result['title'], "Buy groceries")
        self.assertEqual(result['description'], "")
        self.assertEqual(result['status'], "pending")
        self.assertIsNotNone(result['created_at'])
        self.assertIsNone(result['completed_at'])

    def test_serialize_pending_task_with_description(self):
        """Test serializing a pending task with description."""
        task = Task("Buy groceries", "For Sunday dinner")
        result = self.serializer.task_to_dict(task)

        self.assertEqual(result['title'], "Buy groceries")
        self.assertEqual(result['description'], "For Sunday dinner")
        self.assertEqual(result['status'], "pending")

    def test_serialize_complete_task(self):
        """Test serializing a complete task with completion timestamp."""
        task = Task("Buy groceries", "For dinner")
        task.mark_complete()
        result = self.serializer.task_to_dict(task)

        self.assertEqual(result['status'], "complete")
        self.assertIsNotNone(result['completed_at'])

    def test_serialize_task_with_special_characters(self):
        """Test serializing task with special characters in title/description."""
        task = Task("Buy 🛒 items", "For Sunday's dinner: pasta & meat")
        result = self.serializer.task_to_dict(task)

        self.assertEqual(result['title'], "Buy 🛒 items")
        self.assertEqual(result['description'], "For Sunday's dinner: pasta & meat")

    def test_serialize_task_with_quotes_and_newlines(self):
        """Test serializing task with quotes and newlines."""
        title = 'Task with "quotes"'
        description = "Line 1\nLine 2\nLine 3"
        task = Task(title, description)
        result = self.serializer.task_to_dict(task)

        self.assertEqual(result['title'], title)
        self.assertEqual(result['description'], description)

    def test_serialized_dict_is_json_serializable(self):
        """Test that serialized task can be converted to JSON string."""
        import json
        task = Task("Buy groceries", "For dinner")
        result = self.serializer.task_to_dict(task)

        # Should not raise exception
        json_str = json.dumps(result, default=str)
        self.assertIsInstance(json_str, str)
        self.assertIn("Buy groceries", json_str)

    def test_serialize_multiple_tasks(self):
        """Test serializing multiple tasks."""
        tasks = [
            Task("Task 1", "Description 1"),
            Task("Task 2", "Description 2"),
            Task("Task 3"),
        ]

        results = [self.serializer.task_to_dict(t) for t in tasks]

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], "Task 1")
        self.assertEqual(results[1]['title'], "Task 2")
        self.assertEqual(results[2]['title'], "Task 3")


class TestDictToTask(unittest.TestCase):
    """Tests for Task deserialization (dictionary to Task object)."""

    def setUp(self):
        """Create a serializer for each test."""
        self.serializer = TaskSerializer()

    def test_deserialize_valid_pending_task(self):
        """Test deserializing a valid pending task dictionary."""
        data = {
            'id': 1,
            'title': 'Buy groceries',
            'description': 'For dinner',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.title, 'Buy groceries')
        self.assertEqual(result.description, 'For dinner')
        self.assertEqual(result.status, 'pending')
        self.assertIsNotNone(result.created_at)
        self.assertIsNone(result.completed_at)

    def test_deserialize_valid_complete_task(self):
        """Test deserializing a valid complete task dictionary."""
        data = {
            'id': 2,
            'title': 'Buy groceries',
            'description': '',
            'status': 'complete',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': '2026-01-01T10:30:00',
        }
        result = self.serializer.dict_to_task(data)

        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'complete')
        self.assertIsNotNone(result.completed_at)

    def test_deserialize_task_without_description(self):
        """Test deserializing task without description field."""
        data = {
            'id': 1,
            'title': 'Buy groceries',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)

        self.assertIsNotNone(result)
        self.assertEqual(result.description, '')

    def test_deserialize_invalid_missing_id(self):
        """Test deserializing with missing id returns None."""
        data = {
            'title': 'Buy groceries',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_missing_title(self):
        """Test deserializing with missing title returns None."""
        data = {
            'id': 1,
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_wrong_id_type(self):
        """Test deserializing with non-integer id returns None."""
        data = {
            'id': "1",  # String instead of int
            'title': 'Buy groceries',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_wrong_title_type(self):
        """Test deserializing with non-string title returns None."""
        data = {
            'id': 1,
            'title': 123,  # Number instead of string
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_empty_title(self):
        """Test deserializing with empty title returns None."""
        data = {
            'id': 1,
            'title': '',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_whitespace_title(self):
        """Test deserializing with whitespace-only title returns None."""
        data = {
            'id': 1,
            'title': '   ',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_status(self):
        """Test deserializing with invalid status returns None."""
        data = {
            'id': 1,
            'title': 'Buy groceries',
            'description': '',
            'status': 'invalid_status',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)
        self.assertIsNone(result)

    def test_deserialize_invalid_not_dict(self):
        """Test deserializing with non-dict input returns None."""
        result = self.serializer.dict_to_task("not a dict")
        self.assertIsNone(result)

    def test_deserialize_task_with_special_characters(self):
        """Test deserializing task with special characters."""
        data = {
            'id': 1,
            'title': 'Buy 🛒 items',
            'description': "For Sunday's dinner: pasta & meat",
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        result = self.serializer.dict_to_task(data)

        self.assertIsNotNone(result)
        self.assertEqual(result.title, 'Buy 🛒 items')
        self.assertEqual(result.description, "For Sunday's dinner: pasta & meat")


class TestValidateTaskDict(unittest.TestCase):
    """Tests for task dictionary validation."""

    def setUp(self):
        """Create a serializer for each test."""
        self.serializer = TaskSerializer()

    def test_validate_valid_task_dict(self):
        """Test validation passes for valid task dictionary."""
        data = {
            'id': 1,
            'title': 'Buy groceries',
            'description': 'For dinner',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertTrue(self.serializer.validate_task_dict(data))

    def test_validate_missing_id(self):
        """Test validation fails when id is missing."""
        data = {
            'title': 'Buy groceries',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertFalse(self.serializer.validate_task_dict(data))

    def test_validate_missing_title(self):
        """Test validation fails when title is missing."""
        data = {
            'id': 1,
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertFalse(self.serializer.validate_task_dict(data))

    def test_validate_wrong_id_type(self):
        """Test validation fails when id is not an integer."""
        data = {
            'id': '1',
            'title': 'Buy groceries',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertFalse(self.serializer.validate_task_dict(data))

    def test_validate_wrong_title_type(self):
        """Test validation fails when title is not a string."""
        data = {
            'id': 1,
            'title': 123,
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertFalse(self.serializer.validate_task_dict(data))

    def test_validate_empty_title(self):
        """Test validation fails when title is empty string."""
        data = {
            'id': 1,
            'title': '',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertFalse(self.serializer.validate_task_dict(data))

    def test_validate_invalid_status(self):
        """Test validation fails when status is invalid."""
        data = {
            'id': 1,
            'title': 'Buy groceries',
            'description': '',
            'status': 'invalid',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
        }
        self.assertFalse(self.serializer.validate_task_dict(data))

    def test_validate_not_dict(self):
        """Test validation fails when input is not a dictionary."""
        self.assertFalse(self.serializer.validate_task_dict("not a dict"))
        self.assertFalse(self.serializer.validate_task_dict([]))
        self.assertFalse(self.serializer.validate_task_dict(None))

    def test_validate_with_extra_fields(self):
        """Test validation passes when dict has extra fields."""
        data = {
            'id': 1,
            'title': 'Buy groceries',
            'description': '',
            'status': 'pending',
            'created_at': '2026-01-01T10:00:00',
            'completed_at': None,
            'extra_field': 'should be ignored',
        }
        self.assertTrue(self.serializer.validate_task_dict(data))


class TestSerializationRoundTrip(unittest.TestCase):
    """Tests for round-trip serialization and deserialization."""

    def setUp(self):
        """Create a serializer and sample tasks for each test."""
        self.serializer = TaskSerializer()

    def test_round_trip_pending_task(self):
        """Test round-trip serialization of pending task preserves data."""
        original = Task("Buy groceries", "For Sunday dinner")
        original.id = 1  # Set ID (normally done by TaskManager)

        # Serialize
        task_dict = self.serializer.task_to_dict(original)

        # Deserialize
        restored = self.serializer.dict_to_task(task_dict)

        # Verify
        self.assertIsNotNone(restored)
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.title, restored.title)
        self.assertEqual(original.description, restored.description)
        self.assertEqual(original.status, restored.status)
        self.assertEqual(original.created_at, restored.created_at)
        self.assertIsNone(restored.completed_at)

    def test_round_trip_complete_task(self):
        """Test round-trip serialization of complete task preserves data."""
        original = Task("Buy groceries", "For dinner")
        original.id = 2  # Set ID (normally done by TaskManager)
        original.mark_complete()

        # Serialize
        task_dict = self.serializer.task_to_dict(original)

        # Deserialize
        restored = self.serializer.dict_to_task(task_dict)

        # Verify
        self.assertIsNotNone(restored)
        self.assertEqual(original.title, restored.title)
        self.assertEqual(original.status, restored.status)
        self.assertEqual(original.completed_at, restored.completed_at)

    def test_round_trip_multiple_tasks(self):
        """Test round-trip with multiple tasks maintains all data."""
        originals = [
            Task("Task 1", "Description 1"),
            Task("Task 2", "Description 2"),
            Task("Task 3"),
        ]
        originals[0].id = 1
        originals[1].id = 2
        originals[2].id = 3
        originals[0].mark_complete()

        # Serialize all
        dicts = [self.serializer.task_to_dict(t) for t in originals]

        # Deserialize all
        restored = [self.serializer.dict_to_task(d) for d in dicts]

        # Verify
        for original, restored_task in zip(originals, restored):
            self.assertEqual(original.title, restored_task.title)
            self.assertEqual(original.status, restored_task.status)
            self.assertEqual(original.id, restored_task.id)


if __name__ == '__main__':
    unittest.main()
