def evaluate_improvement(incident_report: dict, base_plan: dict) -> list[str]:
    # Extract lessons learned from the incident report
    lessons_learned = incident_report.get('lessons_learned', [])
    
    # Initialize a list to store new steps for the base plan
    new_steps = []
    
    # Iterate through each lesson learned and suggest new steps
    for lesson in lessons_learned:
        if 'improvement' in lesson:
            new_steps.extend(lesson['improvement'])
    
    return new_steps