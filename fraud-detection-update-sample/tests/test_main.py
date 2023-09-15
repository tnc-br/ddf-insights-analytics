import unittest
import os
import sys
from json_test_data import *

# Allows import of ../../main.py
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir)
from main import *

class TestMain(unittest.TestCase):
    def test_parse_path_parts(self):
        firestore_payload_name = "projects/river-sky-386919/databases/(default)/documents/untrusted_samples/fd1239d5488215a23440"
        actual_collection_path, actual_document_path = parse_path_parts(firestore_payload_name)
        self.assertEqual(actual_collection_path, "untrusted_samples")
        self.assertEqual(actual_document_path, "fd1239d5488215a23440")

    def test_is_document_creation_or_update_with_new_inputs___document_creation(self):
        old_value = None
        new_value = {
            "test": "test"
        }
        result = is_document_creation_or_update_with_new_inputs(old_value, new_value)
        self.assertTrue(result)

    def test_is_document_creation_or_update_with_new_inputs___document_update_with_only_outputs_changed(self):
        old_value = {
            "test": "test"
        }
        new_value = {
            "test": "test",
            "validity_details": "test"
        }
        result = is_document_creation_or_update_with_new_inputs(old_value, new_value)
        self.assertFalse(result)

    def test_is_document_creation_or_update_with_new_inputs___document_update_with_new_inputs(self):
        old_value = {
            "test": "test",
            "validity_details": "test"
        }
        new_value = {
            "test": "testy",
            "validity_details": "test"
        }
        result = is_document_creation_or_update_with_new_inputs(old_value, new_value)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()