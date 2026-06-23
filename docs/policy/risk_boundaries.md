# Risk Boundaries

SafeTask-AI is designed as a **private, local-first household safety workbench for situational awareness, local evidence review, and human-reviewed alerts.**

To maintain clear ethical, privacy, and technical boundaries, the following features are explicitly **quarantined** and considered permanently out of scope:

* **Face recognition:** No identification of individuals by facial features.
* **License plate recognition (ALPR):** No automated reading or tracking of vehicle plates.
* **Biometric identification:** No tracking of gait, voiceprints, or other biometrics.
* **Automated law-enforcement escalation:** SafeTask will not automatically dispatch or notify police or emergency services.
* **Weapon detection:** Out of scope for this household system.
* **Public surveillance use:** SafeTask is for private household/property use only, not for monitoring public spaces or commercial surveillance.

## Technical Boundaries

* **No bypassing vendor restrictions:** We will not attempt to reverse engineer cloud camera services (e.g., VicoHome, VisionWell) or bypass vendor restrictions to force local streaming.
* **Local-first/private-use framing only:** SafeTask operates locally.
* **No cloud dependency claims:** The core architecture must not require cloud processing.
* **Human-reviewed alerts only:** All alerts and escalations require a human in the loop.
* **No runtime claims unless implemented and tested:** SafeTask will only claim capabilities that are actively tested and functioning.
