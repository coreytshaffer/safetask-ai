from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class FormRequirement:
    form_id: str
    name: str
    deadline_days: int
    trigger_conditions: List[str]
    required_fields: List[str]

@dataclass
class FormDraft:
    form_id: str
    incident_id: str
    prefilled_data: Dict[str, str] = field(default_factory=dict)
    missing_fields: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None

# Static definitions for OSHA forms
OSHA_301 = FormRequirement(
    form_id="OSHA_301",
    name="OSHA 301 (Injury and Illness Incident Report)",
    deadline_days=7,
    trigger_conditions=["injury", "illness"],
    required_fields=["employee_name", "date_of_birth", "date_of_hire", "time_of_event", "what_happened", "what_was_injury"]
)

OSHA_300 = FormRequirement(
    form_id="OSHA_300",
    name="OSHA 300 (Log of Work-Related Injuries and Illnesses)",
    deadline_days=7,
    trigger_conditions=["injury", "illness", "death", "loss_of_consciousness"],
    required_fields=["case_number", "employee_name", "job_title", "date_of_injury", "where_event_occurred", "describe_injury", "classification"]
)

OSHA_300A = FormRequirement(
    form_id="OSHA_300A",
    name="OSHA 300A (Summary of Work-Related Injuries and Illnesses)",
    deadline_days=365, # Usually end of year, simplified for MVP
    trigger_conditions=["annual_summary"],
    required_fields=["total_deaths", "total_cases_with_days_away", "total_cases_with_transfer", "total_other_cases"]
)

AVAILABLE_FORMS = [OSHA_301, OSHA_300, OSHA_300A]
