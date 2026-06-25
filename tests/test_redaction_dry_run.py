import os
import unittest
import json
from jsonschema import ValidationError
from safetask.redaction import simulate_redaction_request

class TestRedactionDryRun(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'redaction')
        
    def _load_fixture(self, filename):
        with open(os.path.join(self.fixtures_dir, filename), 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_valid_request(self):
        request = self._load_fixture('valid_redaction_export_request.json')
        result = simulate_redaction_request(request)
        
        self.assertEqual(result['schema_version'], '1.0')
        self.assertEqual(result['redaction_status'], 'redaction_applied')
        self.assertTrue(result['export_allowed'])
        self.assertTrue(result['redacted_frame_reference'].startswith('simulated://'))

    def test_invalid_schema_fails(self):
        # Missing required fields like schema_version
        request = {"target_type": "face_region"} 
        with self.assertRaises(ValidationError):
            simulate_redaction_request(request)

    def test_impossible_geometry_fails(self):
        request = self._load_fixture('valid_redaction_export_request.json')
        # Introduce semantic error (xmin > xmax)
        request['redaction_targets'][0]['region']['bbox'] = [500, 100, 200, 200]
        with self.assertRaises(ValidationError):
            simulate_redaction_request(request)

    def test_unsupported_target_blocked(self):
        request = self._load_fixture('valid_redaction_export_request.json')
        # Change target to something unsupported by the stub (e.g. 'address_or_signage' might be unsupported if we only support humans/faces/plates)
        # Let's say 'address_or_signage' is unsupported for now.
        request['redaction_targets'][0]['target_type'] = 'address_or_signage'
        
        result = simulate_redaction_request(request)
        
        self.assertEqual(result['redaction_status'], 'redaction_failed_export_blocked')
        self.assertFalse(result['export_allowed'])
        self.assertIn('Unsupported redaction target', result['failure_reason'])

    def test_video_export_blocked(self):
        request = self._load_fixture('valid_redaction_export_request.json')
        request['export_format'] = 'video'
        
        result = simulate_redaction_request(request)
        
        self.assertEqual(result['redaction_status'], 'redaction_failed_export_blocked')
        self.assertFalse(result['export_allowed'])
        self.assertIn('Video export is currently unsupported', result['failure_reason'])

    def test_prohibited_identity_field_fails_validation(self):
        request = self._load_fixture('valid_redaction_export_request.json')
        request['plate_text'] = 'ABC-123'  # banned by schema `not` construct
        
        with self.assertRaises(ValidationError):
            simulate_redaction_request(request)
