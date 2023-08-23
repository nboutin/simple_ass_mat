"""
:date 2023-08
:author Nicolas Boutin
"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=wrong-import-position
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from simple_ass_mat.model.yaml_schema_validator import YamlSchemaValidator  # nopep8 # noqa: E402


class TestValidateContrat(unittest.TestCase):

    def test_001(self):
        """001"""
        data = {"contrat": {
            'description': 'some description'
        }}

        yaml_validator = YamlSchemaValidator()
        yaml_validator.validate(data)


if __name__ == '__main__':
    import logging
    # from pathlib import Path

    logging.basicConfig(level=logging.DEBUG, handlers=[
        logging.StreamHandler(sys.stdout),
        # logging.FileHandler(Path(__file__).parent / Path(__file__ + '.log'), mode='w')
    ])

    unittest.main()
