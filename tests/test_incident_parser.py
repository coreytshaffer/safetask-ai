import pytest
from safetask.response_mode.parser import parse_incident_text

def test_incident_parser():
    text = "Methyl isocyanate leak in Building 3, first floor. Tank on northwest corner."
    draft = parse_incident_text(text)
    
    assert draft.incident_type == "chemical_release"
    assert draft.parsed_substance == "Methyl isocyanate"
    assert "Building 3" in draft.parsed_location
    assert draft.parsed_asset == "tank"
