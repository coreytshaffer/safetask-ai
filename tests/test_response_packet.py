import pytest
from safetask.response_mode.packet_builder import build_response_packet
from safetask.models.incident import IncidentDraft
from safetask.models.chemical_inventory import ChemicalInventoryRecord
from safetask.models.contacts import ContactRecord

def test_response_packet_contains_required_sections():
    draft = IncidentDraft(
        incident_id="123",
        original_text="Test incident",
        incident_type="chemical_release",
        created_at="2026-06-01T12:00:00Z"
    )
    inventory = ChemicalInventoryRecord(
        chemical_name="TestChem",
        location="Lab 1",
        last_reported_amount=50,
        amount_units="gallons"
    )
    contact = ContactRecord(
        role="Safety Officer",
        name="Jane"
    )
    
    packet = build_response_packet(draft, [{"file_name": "test.pdf", "page": 1, "text": "excerpt"}], inventory, [contact])
    
    assert "Human review required" in packet
    assert "Original report" in packet
    assert "TestChem" in packet
    assert "last reported amount" in packet
    assert "Safety Officer: Jane" in packet
    assert "Missing Information Checklist" in packet
    assert "SafeTask did not determine reportability" in packet
