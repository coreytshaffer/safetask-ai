def get_missing_personnel(roster: list[dict], check_ins: list[str]) -> list[dict]:
    missing_personnel = [person for person in roster if person['employee_id'] not in check_ins]
    return missing_personnel