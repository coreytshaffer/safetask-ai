# Future Feature Evaluation Rubric

This rubric must be applied to any proposed SafeTask feature or integration to ensure it aligns with the Hazard-First Doctrine.

## Evaluation Questions

1. **Hazard vs. Identity**: Does this feature detect a hazard or an identity?
2. **Condition vs. Behavior**: Does it detect an unsafe condition or ordinary behavior?
3. **Abuse Potential**: Could it be abused for social control?
4. **Chilling Effect**: Does it create a chilling effect on legitimate autonomy?
5. **Human Review**: Is human review required, or does it attempt autonomous enforcement?
6. **Retention Needs**: What evidence retention is actually necessary for safety?
7. **Alternative Means**: Could the same safety goal be achieved with less surveillance?
8. **Local-First**: Is the feature local-first, or does it leak data to the cloud?
9. **Escalation Risk**: Does it create law enforcement or emergency escalation risk?
10. **Mission Creep**: Does it risk mission creep beyond objective physical safety?
11. **Data Sensitivity**: Does it require new sensitive data classes (e.g., biometrics)?
12. **Bystander Exposure**: Could exported evidence expose bystanders?
13. **Redaction Focus**: Can the hazard be shown without showing people? What must be masked before export?
14. **Retention vs Export**: Is the original retained locally, and for how long? Does redaction require any prohibited identity features?

## Decision Outcomes

Based on the evaluation, classify the proposed feature into one of the following outcomes:

* `reject`: Fundamentally violates the doctrine. Do not build.
* `defer`: Needs more refinement or technical maturity before evaluation.
* `allow_docs_only`: Approved for operational documentation without code changes.
* `allow_review_gated_pilot`: Allowed, provided all detections are routed to human review without automatic escalation.
* `allow_internal_only`: Allowed only for internal system integrity or telemetry, isolated from surveillance functionality.
