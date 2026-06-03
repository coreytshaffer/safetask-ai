import json
from datetime import datetime, timezone

import requests

from .schema import FieldNote


class DictationParser:
    def __init__(self, api_url: str = None):
        import os
        self.api_url = api_url or os.environ.get("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")

    def parse(self, dictation_text: str) -> FieldNote:
        prompt = f"""
Extract the following information from the field dictation into a JSON object.
Use "Unknown" if not mentioned.

Fields required:
- site_id: The location or site name
- timestamp: The time of observation (or current time if not mentioned)
- observer: The person observing
- notes: The main observation details
- coordinates: Any coordinates mentioned
- confidence_level: High/Medium/Low based on the speaker's tone
- evidence_type: Visual/Sensor/Lab/Audio etc.

Dictation: "{dictation_text}"

Return ONLY valid JSON.
"""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that parses field dictations into strict JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 500,
        }

        try:
            # We use a very short timeout so it fails quickly if LM Studio is not running (e.g., during tests)
            response = requests.post(self.api_url, json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Extract JSON from the markdown block if it exists
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            parsed = json.loads(content)

            return FieldNote(
                site_id=parsed.get("site_id", "Unknown"),
                timestamp=parsed.get(
                    "timestamp", datetime.now(timezone.utc).isoformat()
                ),
                notes=parsed.get("notes", dictation_text),
                observer=parsed.get("observer", "Unknown"),
                coordinates=parsed.get("coordinates", "Unknown"),
                confidence_level=parsed.get("confidence_level", "Unknown"),
                evidence_type=parsed.get("evidence_type", "Unknown"),
            )

        except Exception as e:
            print(f"LM Studio parsing failed: {e}. Falling back to raw text.")
            return FieldNote(
                site_id="Unknown",
                timestamp=datetime.now(timezone.utc).isoformat(),
                notes=dictation_text,
            )
