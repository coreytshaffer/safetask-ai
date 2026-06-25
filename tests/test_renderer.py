import os
import tempfile
import unittest
from PIL import Image
from safetask.renderer import apply_redaction_masks

class TestRenderer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_image_path = os.path.join(self.temp_dir.name, "input.jpg")
        self.output_image_path = os.path.join(self.temp_dir.name, "output.jpg")
        
        # Create a synthetic 200x200 image
        img = Image.new('RGB', (200, 200), color='white')
        img.save(self.input_image_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_image_and_bbox_creates_output(self):
        targets = [{"region": {"bbox": [50, 50, 100, 100]}}]
        result = apply_redaction_masks(self.input_image_path, self.output_image_path, targets)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image_path))

    def test_missing_image_fails_closed(self):
        targets = [{"region": {"bbox": [50, 50, 100, 100]}}]
        with self.assertRaises(FileNotFoundError):
            apply_redaction_masks("nonexistent.jpg", self.output_image_path, targets)

    def test_out_of_bounds_bbox_fails_closed(self):
        # xmax = 250 is out of bounds for 200x200 image
        targets = [{"region": {"bbox": [50, 50, 250, 100]}}]
        with self.assertRaises(ValueError) as ctx:
            apply_redaction_masks(self.input_image_path, self.output_image_path, targets)
        self.assertIn("Out-of-bounds", str(ctx.exception))

    def test_negative_out_of_bounds_bbox_fails_closed(self):
        # xmin = -10 is out of bounds
        targets = [{"region": {"bbox": [-10, 50, 100, 100]}}]
        with self.assertRaises(ValueError) as ctx:
            apply_redaction_masks(self.input_image_path, self.output_image_path, targets)
        self.assertIn("Out-of-bounds", str(ctx.exception))

if __name__ == '__main__':
    unittest.main()
