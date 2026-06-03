import streamlit as st
import os
import tempfile
import json
from datetime import datetime

# Assuming these exist in the python path
from safetask.ingest.inventory_csv import load_inventory_csv
from safetask.ingest.contacts_csv import load_contacts_csv
from review_engine.documents.ingest_pdf import extract_text_from_pdf
from safetask.response_mode.parser import parse_incident_text
from safetask.response_mode.packet_builder import build_response_packet
from safetask.response_mode.form_builder import FormPacketBuilder

st.set_page_config(page_title="SafeTask Response Navigator", layout="wide")

# -- Session State Init --
if "documents" not in st.session_state:
    st.session_state["documents"] = []
if "inventory" not in st.session_state:
    st.session_state["inventory"] = []
if "contacts" not in st.session_state:
    st.session_state["contacts"] = []
if "packets" not in st.session_state:
    st.session_state["packets"] = []
if "form_drafts" not in st.session_state:
    st.session_state["form_drafts"] = []

# -- Sidebar --
with st.sidebar:
    st.title("SafeTask Navigator")
    st.write("Upload sources to populate the engine.")
    
    uploaded_pdfs = st.file_uploader("Upload Safety PDFs", type=["pdf"], accept_multiple_files=True)
    if st.button("Ingest PDFs"):
        for pdf in uploaded_pdfs:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf.read())
                tmp_path = tmp.name
            
            try:
                checksum, pages = extract_text_from_pdf(tmp_path)
                st.session_state["documents"].append({
                    "file_name": pdf.name,
                    "checksum": checksum,
                    "pages": pages
                })
            finally:
                os.remove(tmp_path)
        st.success(f"Ingested {len(uploaded_pdfs)} documents.")

    uploaded_inv = st.file_uploader("Upload Inventory CSV", type=["csv"])
    if st.button("Load Inventory"):
        if uploaded_inv:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_inv.read())
                tmp_path = tmp.name
            try:
                records = load_inventory_csv(tmp_path)
                st.session_state["inventory"] = records
                st.success(f"Loaded {len(records)} inventory records.")
            finally:
                os.remove(tmp_path)
                
    uploaded_cont = st.file_uploader("Upload Contacts CSV", type=["csv"])
    if st.button("Load Contacts"):
        if uploaded_cont:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_cont.read())
                tmp_path = tmp.name
            try:
                records = load_contacts_csv(tmp_path)
                st.session_state["contacts"] = records
                st.success(f"Loaded {len(records)} contacts.")
            finally:
                os.remove(tmp_path)

# -- Main Tabs --
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Document Search", "Response Mode", "Inventory", "Contacts", "Exports", "Form Prep"
])

with tab1:
    st.header("Document Search")
    query = st.text_input("Search safety documents (e.g., 'methyl isocyanate hazards')")
    if query:
        st.write("Human review required. Displaying most relevant pages based on keyword search.")
        query_lower = query.lower()
        results = []
        for doc in st.session_state["documents"]:
            for page in doc["pages"]:
                if query_lower in page["text"].lower():
                    results.append({
                        "file": doc["file_name"],
                        "page": page["page_number"],
                        "text": page["text"][:500] + "..."
                    })
        
        if results:
            for res in results:
                st.markdown(f"**{res['file']} (Page {res['page']})**")
                st.write(res["text"])
                st.divider()
        else:
            st.write("No matching documents found.")

with tab2:
    st.header("Response Mode Lite")
    st.warning("Human review required. SafeTask retrieves and organizes information but does not make safety, legal, medical, regulatory, engineering, or emergency-response decisions.")
    
    incident_text = st.text_area(
        "Describe the incident",
        value="Sodium hypochlorite spill in Maintenance Closet A.",
        height=100
    )
    
    if st.button("Generate Response Packet"):
        draft = parse_incident_text(incident_text)
        
        # Simple match for inventory
        matched_inventory = None
        for inv in st.session_state["inventory"]:
            if draft.parsed_substance and draft.parsed_substance.lower() in inv.chemical_name.lower():
                matched_inventory = inv
                break
                
        # Simple match for contacts
        matched_contacts = []
        for c in st.session_state["contacts"]:
            if c.incident_type == draft.incident_type or c.incident_type == "emergency" or c.location_scope == "all":
                matched_contacts.append(c)
        # Sort by escalation order
        matched_contacts = sorted(matched_contacts, key=lambda x: x.escalation_order or 999)

        # Simple match for documents (SDS)
        relevant_excerpts = []
        if draft.parsed_substance:
            for doc in st.session_state["documents"]:
                for page in doc["pages"]:
                    if draft.parsed_substance.lower() in page["text"].lower():
                        relevant_excerpts.append({
                            "file_name": doc["file_name"],
                            "page": page["page_number"],
                            "text": page["text"][:500] + "..."
                        })
                        break # Just grab one relevant page per doc for MVP

        packet_md = build_response_packet(draft, relevant_excerpts, matched_inventory, matched_contacts)
        
        # Generate Form Drafts
        form_drafts = FormPacketBuilder.evaluate_incident(draft)
        if form_drafts:
            st.session_state["form_drafts"].extend(form_drafts)
            st.success(f"Generated {len(form_drafts)} compliance form drafts in the 'Form Prep' tab.")

        # Save to state
        st.session_state["packets"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": packet_md
        })
        
        st.markdown(packet_md)

with tab3:
    st.header("Chemical Inventory")
    if not st.session_state["inventory"]:
        st.write("No inventory loaded.")
    else:
        for inv in st.session_state["inventory"]:
            st.write(f"**{inv.chemical_name}** ({inv.location}) - {inv.last_reported_amount} {inv.amount_units}")

with tab4:
    st.header("Contacts")
    if not st.session_state["contacts"]:
        st.write("No contacts loaded.")
    else:
        for c in st.session_state["contacts"]:
            st.write(f"[{c.escalation_order}] **{c.role}** - {c.name} ({c.phone})")

with tab5:
    st.header("Exports")
    if not st.session_state["packets"]:
        st.write("No packets generated yet.")
    else:
        for i, pkt in enumerate(st.session_state["packets"]):
            with st.expander(f"Packet {pkt['timestamp']}"):
                st.code(pkt["content"], language="markdown")
                st.download_button(
                    "Download Markdown",
                    data=pkt["content"],
                    file_name=f"safetask_packet_{i}.md",
                    mime="text/markdown"
                )

with tab6:
    st.header("OSHA Form Preparation")
    st.info("The SafeTask Form Packet Builder prepares compliance form data for SME review. It does not automate submissions.")
    if not st.session_state["form_drafts"]:
        st.write("No forms have been drafted yet. Generate a response packet in the 'Response Mode' tab.")
    else:
        for i, draft in enumerate(st.session_state["form_drafts"]):
            with st.expander(f"{draft.form_id} - Due: {draft.due_date.strftime('%Y-%m-%d') if draft.due_date else 'Unknown'}"):
                st.write(f"**Incident ID:** {draft.incident_id}")
                
                st.subheader("Prefilled Context Suggestions")
                for field, value in draft.prefilled_data.items():
                    st.text_input(f"{field.replace('_', ' ').title()}", value=value, key=f"draft_{i}_{field}")
                
                if draft.missing_fields:
                    st.warning(f"Missing required fields: {', '.join(draft.missing_fields)}")
                
                st.button("Mark as Reviewed", key=f"review_{i}")
