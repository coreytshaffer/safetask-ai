import os
from PIL import Image, ImageDraw

def apply_redaction_masks(image_path: str, output_path: str, redaction_targets: list) -> bool:
    """
    Renders opaque masks on a static image based on provided validated redaction target regions.
    Returns True if successful. Raises exceptions if rendering fails or inputs are invalid.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Source image not found: {image_path}")

    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)
            width, height = img.size

            for target in redaction_targets:
                region = target.get("region", {})
                if "bbox" not in region:
                    # Ignore non-bbox geometry for now, or raise if we strictly require bbox
                    # According to the prompt, we only handle valid bbox for now.
                    continue
                
                xmin, ymin, xmax, ymax = region["bbox"]

                # Fail closed on out-of-bounds geometry
                if xmin < 0 or ymin < 0 or xmax > width or ymax > height:
                    raise ValueError(f"Out-of-bounds bbox geometry: {[xmin, ymin, xmax, ymax]} for image size {width}x{height}")

                # Render opaque mask (black rectangle)
                draw.rectangle([xmin, ymin, xmax, ymax], fill="black")

            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path, format="JPEG")
            
        return True
    except Exception as e:
        raise ValueError(f"Rendering failed: {e}")
