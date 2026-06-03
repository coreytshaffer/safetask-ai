from datetime import datetime, timedelta
from typing import List, Dict

from safetask.models.forms import AVAILABLE_FORMS, FormDraft, FormRequirement

class FormPacketBuilder:
    @staticmethod
    def evaluate_incident(incident_draft) -> List[FormDraft]:
        """
        Evaluates an IncidentDraft to determine which forms are required
        and pre-fills them with context-aware suggestions.
        """
        required_drafts = []
        
        # Simple heuristic for MVP: assume every reported incident might need OSHA 301/300
        # In reality, this would be an LLM-driven or strict rule-based check
        triggered_forms = [f for f in AVAILABLE_FORMS if f.form_id in ["OSHA_301", "OSHA_300"]]
        
        # Create drafts for triggered forms
        for form in triggered_forms:
            draft = FormDraft(
                form_id=form.form_id,
                incident_id="TEMP_ID", # In a real app, this would be the actual ID
                due_date=datetime.now() + timedelta(days=form.deadline_days)
            )
            
            # Context-aware predictive suggestions
            prefilled = {}
            missing = []
            
            for field in form.required_fields:
                if field == "what_happened" and incident_draft.incident_type:
                    prefilled[field] = f"[Suggested based on notes] Incident type: {incident_draft.incident_type}. Notes: {incident_draft.original_text}"
                elif field == "time_of_event":
                    prefilled[field] = f"[Suggested] Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                else:
                    prefilled[field] = "" # Leave blank for human to fill
                    missing.append(field)
            
            draft.prefilled_data = prefilled
            draft.missing_fields = missing
            required_drafts.append(draft)
            
        return required_drafts
