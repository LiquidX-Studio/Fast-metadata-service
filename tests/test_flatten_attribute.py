import unittest

from pydantic import ValidationError

from module.utils import _flatten_attributes


class TestFlattenAttribute(unittest.TestCase):
    attributes = [
        {"trait_type": "trait name1",
         "value": "trait value1"
         },
        {"trait_type": "trait name2",
         "value": "trait value2",
         "display_type": "number"
         }
    ]

    def test_flatten_attribute(self):
        attributes = _flatten_attributes(self.attributes)
        expected_result = {
            "trait name1": {"trait_type": "trait name1",
                            "value": "trait value1"
                           },
            "trait name2": {"trait_type": "trait name2",
                            "value": "trait value2",
                            "display_type": "number"
                           }
        }

        self.assertDictEqual(attributes, expected_result)

    def test_flatten_attribute_with_empty_attributes(self):
        attributes = _flatten_attributes([])
        expected_result = {}

        self.assertDictEqual(attributes, expected_result)

    def test_flatten_attribute_with_invalid_attributes(self):
        invalid_attributes = [{"hello": "world"}]
        with self.assertRaises(ValidationError):
            _flatten_attributes(invalid_attributes)
