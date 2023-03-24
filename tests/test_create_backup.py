import asyncio
import os
import shutil
import unittest
from datetime import datetime

from module.utils import create_backup
from tests.constant import METADATA_DIR

class TestCreateBackup(unittest.TestCase):
    file = os.path.join(METADATA_DIR, '1.json')
    def test_create_backup(self):
        with open(self.file, 'rb') as file:
            original_content = file.read()
            asyncio.run(create_backup(self.file, original_content))
            backup_dir = os.path.join(METADATA_DIR, "backup")
            self.assertTrue(os.path.isdir(backup_dir)) # Is backup directory created
            for sub_dir in os.listdir(backup_dir):
                self.assertEqual(datetime.now().date().isoformat(),
                                 sub_dir) # Directory should be named with current date
                sub_dir_path = os.path.join(backup_dir, sub_dir)
                for backup_file in os.listdir(os.path.join(backup_dir,sub_dir)):
                    with open(os.path.join(sub_dir_path, backup_file), 'rb') as file:
                        self.assertEqual(file.read(), original_content) # Should contain the original content
            shutil.rmtree(backup_dir)
