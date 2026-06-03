from typing import List, Dict
from safetask.models.incident import IncidentDraft
from safetask.models.chemical_inventory import ChemicalInventoryRecord
from safetask.models.contacts import ContactRecord

def build_response_packet(
    incident: IncidentDraft,
    relevant_excerpts: List[Dict],
    inventory: ChemicalInventoryRecord,
    contacts: List[ContactRecord]
) -> str:
    md = []
    md.append("# SafeTask Response Packet\n")
    md.append("Human review required.\n")
    md.append("SafeTask retrieves and organizes source-linked information for authorized human review. It does not make legal, medical, regulatory, engineering, emergency-response, or compliance determinations.\n")
    
    md.append("## Incident Summary\n")
    md.append(f"Original report:\n“{incident.original_text}”\n")
    md.append("Parsed fields:")
    md.append(f"- Possible incident type: {incident.incident_type or 'unknown'}")
    md.append(f"- Substance: {incident.parsed_substance or 'unknown'}")
    md.append(f"- Location: {incident.parsed_location or 'unknown'}")
    md.append(f"- Asset hint: {incident.parsed_asset or 'unknown'}\n")
    
    if inventory:
        md.append("## Chemical Inventory Context\n")
        md.append(f"- Chemical: {inventory.chemical_name}")
        if inventory.product_name: md.append(f"- Product: {inventory.product_name}")
        if inventory.cas_number: md.append(f"- CAS: {inventory.cas_number}")
        md.append(f"- Location: {inventory.location}")
        if inventory.asset_id: md.append(f"- Asset ID: {inventory.asset_id}")
        if inventory.last_reported_amount: 
            md.append(f"- Last reported amount: {inventory.last_reported_amount} {inventory.amount_units or ''}")
        if inventory.last_verified_at:
            md.append(f"- Last verified: {inventory.last_verified_at}")
        if inventory.chemical_age_days:
            md.append(f"- Chemical age: {inventory.chemical_age_days} days")
        if inventory.responsible_person:
            md.append(f"- Responsible person: {inventory.responsible_person}")
            
        md.append("\nInventory note:")
        md.append("This is the last reported amount from the configured inventory source. It is not guaranteed current unless confirmed by an authorized live source or responsible personnel.\n")

    md.append("## Relevant Source Excerpts\n")
    if relevant_excerpts:
        for exc in relevant_excerpts:
            md.append(f"### {exc.get('file_name', 'Unknown Document')}")
            md.append(f"- Page: {exc.get('page', 'Unknown')}")
            if exc.get('section'): md.append(f"- Section: {exc.get('section')}")
            md.append(f"- Excerpt: {exc.get('text', '')}\n")
    else:
        md.append("No specific policies found for this incident type.\n")

    md.append("## Contact Workflow\n")
    if contacts:
        for contact in contacts:
            md.append(f"{contact.escalation_order or '-'}. {contact.role}: {contact.name}")
    else:
        md.append("No configured contacts.\n")
        
    md.append("\n## Missing Information Checklist\n")
    md.append("- Has the area been evacuated according to the site plan?")
    md.append("- Has the safety officer been notified?")
    md.append("- Is anyone exposed or symptomatic?")
    md.append("- Is the leak confirmed or suspected?")
    md.append("- Is the source confirmed?")
    md.append("- Is the incident active, contained, or unknown?")
    md.append("- Are trained responders on scene?")
    md.append("- Has the incident log been started?\n")

    md.append("## Limitations\n")
    md.append("- SafeTask did not determine reportability, compliance status, root cause, or required response actions.")
    md.append("- All response actions must follow site procedures and authorized human direction.")

    return "\n".join(md)
