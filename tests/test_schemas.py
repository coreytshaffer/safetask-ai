import unittest
import json
import os
import jsonschema
from jsonschema.exceptions import ValidationError
from safetask.redaction import validate_geometry

class TestSchemas(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.schemas_dir = os.path.join(self.base_dir, 'schemas')
        self.fixtures_dir = os.path.join(self.base_dir, 'tests', 'fixtures')
        
    def _load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _validate(self, instance, schema):
        jsonschema.validate(instance=instance, schema=schema)
        validate_geometry(instance)

    def test_flame_smoke_claim(self):
        schema = self._load_json(os.path.join(self.schemas_dir, 'flame_smoke_claim.schema.json'))
        
        # Valid
        valid_data = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'valid_flame_smoke_claim.json'))
        self._validate(valid_data, schema)
        
        # Ambiguous but valid schema-wise
        ambig_data = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'ambiguous_smoke_claim.json'))
        self._validate(ambig_data, schema)
        
        # Invalid (general)
        invalid_data = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'invalid_flame_smoke_claim.json'))
        with self.assertRaises(ValidationError):
            self._validate(invalid_data, schema)
            
        # Invalid (geometry missing y_max)
        invalid_geom = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'invalid_flame_smoke_geometry.json'))
        with self.assertRaises(ValidationError):
            self._validate(invalid_geom, schema)

    def test_redaction_export_request(self):
        schema = self._load_json(os.path.join(self.schemas_dir, 'redaction_export_request.schema.json'))
        
        # Valid
        valid_data = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'valid_redaction_export_request.json'))
        self._validate(valid_data, schema)

    def test_redaction_export_record(self):
        schema = self._load_json(os.path.join(self.schemas_dir, 'redaction_export_record.schema.json'))
        
        # Valid
        valid_data = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'valid_redacted_export_record.json'))
        self._validate(valid_data, schema)
        self.assertTrue(valid_data['export_allowed'])
        
        # Invalid containing plate text
        invalid_plate = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'invalid_redaction_contains_plate_text.json'))
        with self.assertRaises(ValidationError):
            self._validate(invalid_plate, schema)

        # Invalid containing face embedding
        invalid_face = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'invalid_redaction_contains_face_embedding.json'))
        with self.assertRaises(ValidationError):
            self._validate(invalid_face, schema)
            
        # Invalid geometry (semantic error x_min > x_max)
        invalid_geom = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'invalid_redaction_geometry.json'))
        with self.assertRaises(ValidationError):
            self._validate(invalid_geom, schema)

    def test_redaction_failure_event(self):
        schema = self._load_json(os.path.join(self.schemas_dir, 'redaction_failure_event.schema.json'))
        
        # Valid fail-closed event
        valid_fail = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'redaction_failed_export_blocked.json'))
        self._validate(valid_fail, schema)
        
        # Ensure export_allowed is strictly false in this schema via the fixture
        self.assertFalse(valid_fail['export_allowed'])

if __name__ == '__main__':
    unittest.main()
