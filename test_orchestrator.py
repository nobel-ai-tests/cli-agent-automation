import unittest
import os
import json
import shutil
from controller import atomic_write, extract_step, check_rate_limit
from generate_manifest import generate_manifest

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_atomic.txt"
        self.test_dir = "test_projects"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_atomic_write(self):
        content = "hello atomic"
        atomic_write(self.test_file, content)
        with open(self.test_file, "r") as f:
            self.assertEqual(f.read(), content)

    def test_extract_step(self):
        self.assertEqual(extract_step("I will create a file."), "I will create a file.")
        self.assertEqual(extract_step("Creating index.html..."), "Creating index.html...")
        self.assertIsNone(extract_step("Just some random text."))

    def test_check_rate_limit(self):
        self.assertTrue(check_rate_limit("Resource exhausted"))
        self.assertTrue(check_rate_limit("429 Too Many Requests"))
        self.assertFalse(check_rate_limit("Success"))

    def test_generate_manifest(self):
        # Setup mock projects
        p1 = os.path.join(self.test_dir, "proj1")
        os.makedirs(p1)
        with open(os.path.join(p1, "file1.txt"), "w") as f: f.write("test")
        
        # Override PROJECTS_DIR for test
        import generate_manifest
        original_dir = generate_manifest.PROJECTS_DIR
        generate_manifest.PROJECTS_DIR = self.test_dir
        generate_manifest.MANIFEST_FILE = "test_manifest.json"
        
        try:
            generate_manifest.generate_manifest()
            with open("test_manifest.json", "r") as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]["name"], "proj1")
                self.assertIn("file1.txt", data[0]["files"])
        finally:
            generate_manifest.PROJECTS_DIR = original_dir
            if os.path.exists("test_manifest.json"):
                os.remove("test_manifest.json")

if __name__ == "__main__":
    unittest.main()
