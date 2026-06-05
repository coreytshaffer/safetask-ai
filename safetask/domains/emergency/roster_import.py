import csv
from io import StringIO

def import_roster(csv_content: str) -> list[dict]:
    roster = []
    csv_file = StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        roster.append({
            'employee_id': row['employee_id'],
            'name': row['name'],
            'department': row['department'],
            'status': row['status']
        })
    
    return roster