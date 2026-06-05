import time
import sys
from datetime import datetime

# Import Epic 17 Modules (Security Integration)
from safetask.domains.security.acs_mock import BadgeReadEvent
from safetask.domains.security.acs_scc_integration import acs_handoff_to_scc
from safetask.domains.security.pip_trigger import trigger_camera_spawn

# Import Epic 16 Modules (Dispatch & Tracking)
from safetask.domains.security.dispatch_log import create_dispatch_entry

# Import Epic 13 Modules (Field Safety)
from safetask.domains.field.safety_schema import FieldSafetyEvent
from safetask.domains.field.jha_draft import draft_jha

# Import Epic 10 & 11 Modules (Emergency & Accountability)
from safetask.domains.emergency.gap_check import check_gap
from safetask.domains.emergency.accountability import get_missing_personnel

def print_step(title):
    print(f"\n{'='*60}")
    print(f"=== {title.upper()}")
    print(f"{'='*60}")
    time.sleep(1)

def print_action(action):
    print(f"[*] {action}")
    time.sleep(0.5)

def main():
    print("Initializing SafeTask AI Grand Integration Demo...\n")
    time.sleep(1)

    # 1. Simulate ACS Badge Swipe (Epic 17)
    print_step("Phase 1: Physical Security Alert")
    location = "Executive Offices"
    badge_id = "B_EXEC_REVOKED"
    
    print_action(f"Incoming ACS Badge Swipe detected at: {location}")
    print_action(f"Badge ID: {badge_id}")
    
    # Deterministic event creation
    acs_event = BadgeReadEvent(
        badge_id=badge_id,
        door_id="DOOR_EXEC_01",
        timestamp=time.time(),
        status="denied"
    )
    print_action(f"ACS Controller returned status: {acs_event.status.upper()}")

    # 2. SCC Routing (Epic 17)
    print_step("Phase 2: SCC Routing & Automation")
    scc_alert = acs_handoff_to_scc(acs_event)
    
    if scc_alert:
        print_action(f"SCC Hand-off triggered. Alert Type: {scc_alert['alert_type']}")
        
        # Trigger Camera (Epic 17)
        pip_action = trigger_camera_spawn(asset_id=badge_id, location=location)
        print_action(f"Automated UI Command: {pip_action['action']} -> {pip_action['camera_feed']}")
        
        # Radio Traffic Comms (User Request)
        print_action("RADIO TRAFFIC (Dispatch to Surveillance): 'We have a denied read at the Executive Offices. Pulling up PiP now. Send an officer.'")
        
        # 3. Dispatch (Epic 16)
        print_step("Phase 3: Security Dispatch")
        dispatch_ticket = create_dispatch_entry(
            officer_id="OFC_TAYLOR_U992",
            location=location,
            task=f"Investigate denied badge read at {location}"
        )
        print_action(f"Dispatch Ticket Created: Officer {dispatch_ticket['officer_id']} responding to {dispatch_ticket['location']}")
        print_action(f"Task: {dispatch_ticket['task']} (Status: {dispatch_ticket['status']})")
        print_action("RADIO TRAFFIC (Officer U992): 'Copy dispatch, I'm en route to Executive Offices.'")
        
        time.sleep(2)
        print_action("RADIO TRAFFIC (Officer U992): 'Dispatch, be advised. The denied badge was dropped on the floor. There is a massive unidentified chemical spill right in front of the executive doors. Strong odor. Elevating severity.'")

        # 4. Field Safety Event (Epic 13)
        print_step("Phase 4: Field Safety Escalation")
        safety_event = FieldSafetyEvent(
            event_id="EVT_CHEM_001",
            timestamp=datetime.now(),
            location=location,
            hazard_type="Chemical Spill",
            reporter_id="OFC_TAYLOR_U992",
            severity="high"
        )
        print_action(f"Upgrading incident to FieldSafetyEvent: {safety_event.hazard_type} (Severity: {safety_event.severity.upper()})")

        # 5. JHA Drafting (Epic 13)
        print_step("Phase 5: Automated Hazard Analysis")
        print_action("Generating immediate Job Hazard Analysis (JHA)...")
        jha = draft_jha(safety_event)
        print(f"    -> Hazards: {jha['hazards_identified']}")
        print(f"    -> Recommended Controls: {jha['controls_recommended']}")

        # 6. Emergency Gap Check (Epic 10)
        print_step("Phase 6: Emergency Plan Gap Check")
        print_action("Cross-referencing site Emergency Action Plan (EAP) for Chemical Spill...")
        base_plan = {"evacuate_zone": True, "hazmat_call": True, "containment": True}
        annex = {"evacuate_zone": True, "hazmat_call": True} # Missing containment!
        gaps = check_gap(base_plan, annex)
        print(f"    -> WARNING GAPS: Missing steps in current active plan: {', '.join(gaps)}")

        # 7. Evacuation Accountability (Epic 11)
        print_step("Phase 7: Evacuation Accountability")
        print_action(f"Initiating Evacuation Accountability Board for zone: Executive Offices")
        roster = [
            {"employee_id": "Exec_CEO", "name": "CEO"},
            {"employee_id": "Exec_CFO", "name": "CFO"},
            {"employee_id": "Admin_Assistant", "name": "Assistant"},
            {"employee_id": "Janitorial_Staff", "name": "Janitor"}
        ]
        
        print_action(f"Board initialized with {len(roster)} personnel.")
        
        print_action("RADIO TRAFFIC: 'We have the CEO and CFO safely relocated to the lobby.'")
        check_ins = ["Exec_CEO", "Exec_CFO"]
        
        unaccounted = get_missing_personnel(roster, check_ins)
        print_action(f"UNACCOUNTED PERSONNEL REMAINING: {[p['name'] for p in unaccounted]}")
        print_action("RADIO TRAFFIC (Officer U992): 'I will sweep the offices for the admin and janitor.'")
        
        print_step("Demo Scenario Completed Successfully")
        print("All SafeTask modules successfully engaged and escalated.")
    else:
        print_action("Badge was granted. No further escalation needed.")

if __name__ == "__main__":
    main()
