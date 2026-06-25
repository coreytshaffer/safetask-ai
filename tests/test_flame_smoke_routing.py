import os
import json
import unittest
from jsonschema.exceptions import ValidationError
from safetask.flame_smoke import route_flame_smoke_claim

class TestFlameSmokeRouting(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.fixtures_dir = os.path.join(self.base_dir, 'tests', 'fixtures', 'flame_smoke')
        
    def _load_json(self, filename):
        with open(os.path.join(self.fixtures_dir, filename), 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_valid_smoke_claim_routes_successfully(self):
        claim = self._load_json('valid_smoke_claim_with_bystander.json')
        targets = [{"target_type": "human_figure", "region": {"bbox": [10, 10, 50, 50]}}]
        result = route_flame_smoke_claim(claim, redaction_targets=targets, export_format="image")
        
        self.assertTrue(result['export_allowed'])
        self.assertEqual(result['redaction_status'], 'redaction_applied')

    def test_ambiguous_smoke_claim_requires_review(self):
        claim = self._load_json('ambiguous_smoke_claim.json')
        # Ensure it requires review
        self.assertTrue(claim.get('review_required'))
        result = route_flame_smoke_claim(claim, redaction_targets=[])
        
        # Should not produce an export record yet
        self.assertEqual(result['status'], 'review_required_no_export')

    def test_unsupported_redaction_target_fails_closed(self):
        claim = self._load_json('valid_flame_claim_with_plate_region.json')
        # Engine doesn't support 'address_or_signage' yet
        targets = [{"target_type": "address_or_signage", "region": {"bbox": [10, 10, 50, 50]}}]
        result = route_flame_smoke_claim(claim, redaction_targets=targets, export_format="image")
        
        self.assertFalse(result['export_allowed'])
        self.assertEqual(result['redaction_status'], 'redaction_failed_export_blocked')

    def test_invalid_claim_fails_before_redaction(self):
        claim = self._load_json('invalid_flame_smoke_geometry.json')
        with self.assertRaises(ValidationError):
            route_flame_smoke_claim(claim, redaction_targets=[])

    def test_prohibited_identity_field_fails_validation(self):
        claim = self._load_json('invalid_claim_with_identity_field.json')
        with self.assertRaises(ValidationError):
            route_flame_smoke_claim(claim, redaction_targets=[])

    def test_video_export_attempt_fails_closed(self):
        claim = self._load_json('valid_smoke_claim_with_bystander.json')
        result = route_flame_smoke_claim(claim, redaction_targets=[], export_format="video")
        
        self.assertFalse(result['export_allowed'])
        self.assertEqual(result['redaction_status'], 'redaction_failed_export_blocked')
        self.assertIn("video", result.get('failure_reason', '').lower())

    def test_claim_cannot_set_export_allowed_true_before_redaction(self):
        claim = self._load_json('invalid_claim_export_allowed_true.json')
        with self.assertRaises(ValueError) as ctx:
            route_flame_smoke_claim(claim, redaction_targets=[])
        self.assertIn("export_allowed=True before redaction", str(ctx.exception))

if __name__ == '__main__':
    unittest.main()
