import unittest
from http import HTTPStatus

from pydantic import ValidationError

from module.utils import update_attributes


class TestUpdateAttribute(unittest.TestCase):
    attributes = [
        {
            "trait_type": "Background",
            "value": "Blue"
        },
        {
            "trait_type": "Stamina",
            "value": 46,
            "display_type": "number"
        }
    ]

    def test_overwrite_existing_attribute(self):
        new_attributes = [
            {
                "trait_type": "Background",
                "value": "Red"
            }
        ]

        response, status = update_attributes(self.attributes, new_attributes)
        expected_result = [
            {
                "trait_type": "Background",
                "value": "Red"
            },
            {
                "trait_type": "Stamina",
                "value": 46,
                "display_type": "number"
            }
        ]

        self.assertEqual(response, expected_result)
        self.assertEqual(status, HTTPStatus.OK)

    def test_add_new_attribute(self):
        new_attributes = [
            {
                "trait_type": "New Trait",
                "value": "new value"
            }
        ]

        response, status = update_attributes(self.attributes, new_attributes, overwrite=False)
        expected_result = [
            {
                "trait_type": "Background",
                "value": "Blue"
            },
            {
                "trait_type": "Stamina",
                "value": 46,
                "display_type": "number"
            },
            {
                "trait_type": "New Trait",
                "value": "new value"
            }
        ]

        self.assertEqual(response, expected_result)
        self.assertEqual(status, HTTPStatus.OK)

    def test_overwrite_nonexist_attribute(self):
        new_attributes = [
            {
                "trait_type": "New Type",
                "value": "new value"
            }
        ]

        response, status = update_attributes(self.attributes, new_attributes, overwrite=True)
        expected_result = {"detail": "Trait type(s) 'New Type' not found in metadata"}
        self.assertDictEqual(response, expected_result)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)

    def test_add_existing_attribute(self):
        new_attributes = [
            {
                "trait_type": "Background",
                "value": "Red"
            }
        ]

        response, status = update_attributes(self.attributes, new_attributes, overwrite=False)
        expected_result = {"detail": "Trait type(s) 'Background' already exists in metadata"}
        self.assertDictEqual(response, expected_result)
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)

    def test_update_empty_attribute(self):
        new_attributes = []
        response, status = update_attributes(self.attributes, new_attributes, overwrite=False)
        expected_result = {"detail": "No attributes to update"}
        self.assertDictEqual(response, expected_result)

        response, status = update_attributes(new_attributes, self.attributes, overwrite=True)
        expected_result = {"detail": "No attributes to update"}
        self.assertDictEqual(response, expected_result)

    def test_invalid_attribute(self):
        new_attributes = [1, 2, 3]

        with self.assertRaises(ValidationError):
            update_attributes(self.attributes, new_attributes)

        with self.assertRaises(ValidationError):
            update_attributes(new_attributes, self.attributes)
