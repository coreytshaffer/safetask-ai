def check_gap(base_plan: dict, annex: dict) -> list[str]:
    missing_steps = []
    
    # Iterate through each step in the base plan
    for step_id, step_details in base_plan.items():
        # Check if the step is present in the annex
        if step_id not in annex:
            missing_steps.append(step_id)
    
    return missing_steps