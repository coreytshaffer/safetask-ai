import os
import json
import jsonschema
from jsonschema.exceptions import ValidationError

def get_schema_path(schema_name):
    return os.path.join(os.path.dirname(__file__), '..', 'schemas', schema_name)

def load_schema(schema_name):
    with open(get_schema_path(schema_name), 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_geometry(instance):
    """Recursively enforce that x_min < x_max and y_min < y_max for any bbox."""
    if isinstance(instance, dict):
        if 'bbox' in instance and isinstance(instance['bbox'], list) and len(instance['bbox']) == 4:
            xmin, ymin, xmax, ymax = instance['bbox']
            if xmin >= xmax or ymin >= ymax:
                raise ValidationError(f"Invalid bbox geometry: xmin({xmin}) must be < xmax({xmax}) and ymin({ymin}) must be < ymax({ymax})")
        for k, v in instance.items():
            validate_geometry(v)
    elif isinstance(instance, list):
        for item in instance:
            validate_geometry(item)

def validate_payload(payload, schema_name):
    """Validates payload against JSON schema and applies semantic geometry checks."""
    schema = load_schema(schema_name)
    jsonschema.validate(instance=payload, schema=schema)
    validate_geometry(payload)
