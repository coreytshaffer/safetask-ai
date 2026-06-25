import os
import json
import unittest
from jsonschema.exceptions import ValidationError
from safetask.schema_validation import validate_payload

class TestSchemaValidation(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.fixtures_dir = os.path.join(self.base_dir, 'tests', 'fixtures')
        
    def _load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_valid_payload_passes(self):
        payload = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'valid_flame_smoke_claim.json'))
        # Should not raise
        validate_payload(payload, 'flame_smoke_claim.schema.json')

    def test_bad_schema_version_fails(self):
        payload = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'valid_flame_smoke_claim.json'))
        payload['schema_version'] = "2.0"
        with self.assertRaises(ValidationError) as ctx:
            validate_payload(payload, 'flame_smoke_claim.schema.json')
        self.assertIn("1.0", str(ctx.exception))

    def test_prohibited_identity_field_fails(self):
        payload = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'invalid_redaction_contains_plate_text.json'))
        with self.assertRaises(ValidationError):
            validate_payload(payload, 'redaction_export_record.schema.json')

    def test_impossible_bbox_fails(self):
        payload = self._load_json(os.path.join(self.fixtures_dir, 'redaction', 'invalid_redaction_geometry.json'))
        with self.assertRaises(ValidationError) as ctx:
            validate_payload(payload, 'redaction_export_record.schema.json')
        self.assertIn("must be < xmax", str(ctx.exception))

    def test_malformed_bbox_fails(self):
        payload = self._load_json(os.path.join(self.fixtures_dir, 'flame_smoke', 'invalid_flame_smoke_geometry.json'))
        with self.assertRaises(ValidationError):
            validate_payload(payload, 'flame_smoke_claim.schema.json')

if __name__ == '__main__':
    unittest.main()
