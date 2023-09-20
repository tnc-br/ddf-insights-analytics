import unittest
import os
import sys
from json_test_data import *

# Allows import of ../../main.py
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir)
from main import *
# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")


class TestMain(unittest.TestCase):
    def test_parse_path_parts(self):
        firestore_payload_name = "projects/{GCP_PROJECT_ID}/databases/(default)/documents/untrusted_samples/fd1239d5488215a23440"
        actual_collection_path, actual_document_path = parse_path_parts(firestore_payload_name)
        self.assertEqual(actual_collection_path, "untrusted_samples")
        self.assertEqual(actual_document_path, "fd1239d5488215a23440")

if __name__ == '__main__':
    unittest.main()