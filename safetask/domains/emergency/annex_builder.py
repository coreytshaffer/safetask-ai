def build_annex(incident_type: str, location: str, severity: str) -> dict:
    annex_template = {
        "Incident Type": incident_type,
        "Location": location,
        "Severity": severity,
        "Emergency Contacts": {
            "Local Police": "110",
            "Fire Department": "119",
            "Ambulance": "120"
        },
        "Evacuation Plan": {
            "Immediate Evacuation Areas": [],
            "Shelter Locations": []
        },
        "First Aid Kit": {
            "Items": [
                "Bandages",
                "Antiseptic Wipes",
                "Pain Relievers",
                "Cuts and Scrapes Kit"
            ]
        },
        "Communication Plan": {
            "Primary Contact": "",
            "Secondary Contact": ""
        },
        "Notes": ""
    }
    return annex_template