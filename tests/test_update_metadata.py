import unittest
from http import HTTPStatus

from module.utils import update_metadata


class TestUpdateMetadata(unittest.TestCase):
    metadata = {
        "name": "test metadata",
        "image_url": "https://example.url/image.png",
        "description": "this is a test metadata"
    }

    def test_overwrite_metadata(self):
        new_metadata = {
            "image_url": "https://new-image.url/image.png",
            "description": "this is a new test metadata"
        }

        expected_result = {
            "name": "test metadata",
            "image_url": "https://new-image.url/image.png",
            "description": "this is a new test metadata"
        }

        metadata, status = update_metadata(self.metadata, new_metadata)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.OK)


    def test_add_new_metadata(self):
        new_metadata = {
            "animation_url": "https://new-animation.url/image.gif",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Neptune"
                }
            ]
        }

        expected_result = {
            "name": "test metadata",
            "image_url": "https://example.url/image.png",
            "description": "this is a test metadata",
            "animation_url": "https://new-animation.url/image.gif",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Neptune"
                }
            ]
        }

        metadata, status = update_metadata(self.metadata, new_metadata, overwrite=False)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.OK)

    def test_add_new_existing_key(self):
        new_metadata = {
            "name": "new name",
        }

        expected_result = {
            "detail": "Key(s) 'name' already exists in metadata"
        }

        metadata, status = update_metadata(self.metadata, new_metadata, overwrite=False)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)

    def test_overwrite_nonexist_key(self):
        new_metadata = {
            "animation_url": "https://new-animation.url/image.gif",
        }

        expected_result = {
            "detail": "Key(s) 'animation_url' not found in metadata"
        }

        metadata, status = update_metadata(self.metadata, new_metadata, overwrite=True)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)

    def test_overwrite_nonexist_attribute_key(self):
        new_metadata = {
            "animation_url": "https://new-animation.url/image.gif",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Neptune"
                }
            ]
        }

        expected_result = {
            "detail": "No attributes to update"
        }

        metadata, status = update_metadata(self.metadata, new_metadata, overwrite=True)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)

    def test_update_attribute(self):
        metadata = {
            "name": "test metadata",
            "image_url": "https://example.url/image.png",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Neptune"
                }
            ]
        }

        new_metadata = {
            "name": "Creature",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Jupiter"
                }
            ]
        }

        expected_result = {
            "name": "Creature",
            "image_url": "https://example.url/image.png",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Jupiter"
                }
            ]
        }

        metadata, status = update_metadata(metadata, new_metadata)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.OK)

    def test_update_nonexist_attribute(self):
        metadata = {
            "name": "test metadata",
            "image_url": "https://example.url/image.png",
            "attributes": [
                {
                    "trait_type": "Planet",
                    "value": "Neptune"
                }
            ]
        }

        new_metadata = {
            "name": "Creature",
            "attributes": [
                {
                    "trait_type": "Blood Type",
                    "value": "B"
                }
            ]
        }

        expected_result = {
            "detail": "Trait type(s) 'Blood Type' not found in metadata"
        }

        metadata, status = update_metadata(metadata, new_metadata)
        self.assertDictEqual(metadata, expected_result)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
