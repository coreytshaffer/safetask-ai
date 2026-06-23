# Upstream Source Assessment

This document evaluates potential upstream video management systems (VMS), network video recorders (NVR), and other event sources against the SafeTask adapter contract and local-first governance boundaries.

## Governance Reminder

Regardless of the upstream source, **all incoming data must pass the SafeTask AdapterPayload validation**. SafeTask explicitly prohibits the ingestion of:
- Face recognition data
- Automated license plate recognition (ALPR) data
- Biometric identification
- Weapon detection
- Law-enforcement routing workflows
- Automated escalation triggers
- Public surveillance metadata

Any adapter claiming these capabilities or failing to provide the required "no" attestations will be automatically rejected by the local airlock.

## Candidate Scoring Table

*Scores: 1 = Poor Fit | 2 = Risky/Awkward | 3 = Workable | 4 = Strong Fit | 5 = Excellent Fit*

| Candidate | Open Source | Local-First | Export Path | Object/Motion | Hardware Accel | Governance Risk | SafeTask Fit | Total Score |
|---|---|---|---|---|---|---|---|---|
| **Generic Drop-Folder** | Yes | Yes (Filesystem) | JSON Drop | Adapter-Dependent | N/A | Lowest | 5 | 5.0 |
| **Frigate** | Yes | Yes | MQTT / API | Yes | Yes (Coral/OpenVINO) | Low | 4 | 4.0 |
| **Viseron** | Yes | Yes | MQTT / API | Yes | Yes (CUDA/Coral) | Medium (Has LPR/Face support) | 3 | 3.5 |
| **ZoneMinder** | Yes | Yes | API / Webhook | Yes | Partial | Low | 3 | 3.0 |
| **Shinobi** | Yes | Yes | Webhook / API | Yes | Yes | Low | 3 | 3.0 |
| **Kerberos Agent** | Yes | Yes | Webhook / MQTT | Yes | Yes | Low | 3 | 3.0 |
| **Scrypted** | Core (Plugins closed) | Yes | Webhook / Plugins | Yes | Yes (CoreML/OpenVINO) | Medium (Licensing) | 2 | 2.5 |
| **Agent DVR / iSpy** | No (Freemium) | Yes | Webhook / API | Yes | Yes | High (Closed Source) | 1 | 1.5 |
| **VicoHome** | No | No (Cloud) | Closed API | Yes | N/A | Very High (Cloud) | 1 | 1.0 |

## Candidate Details

### 1. Generic Drop-Folder (Highest Recommendation)
- **Status:** Architecture pattern, not a specific product.
- **Why it fits:** The ultimate ethical airlock. Any external script can scrape, poll, or digest a camera feed, write a compliant JSON file to the folder, and rely on SafeTask to accept or reject it deterministically.
- **Governance Risk:** Lowest. The script author must explicitly map fields to the SafeTask contract.

### 2. Frigate (Recommended First VMS)
- **Status:** Open Source, Local-First.
- **Why it fits:** Highly mature object detection using Google Coral or OpenVINO. It focuses heavily on bounding boxes (person, car, dog) rather than identity resolution. It emits clean MQTT events that are relatively easy to map to the SafeTask envelope.
- **Governance Risk:** Low. Frigate intentionally avoids built-in face recognition, aligning well with SafeTask's mission.
- **Integration Path:** A companion script subscribing to Frigate's MQTT topics, translating messages, and writing to the Drop-Folder.

### 3. Viseron (Best Advanced-Vision Exploration)
- **Status:** Open Source, Local-First.
- **Why it fits:** Powerful processing pipeline supporting deep neural networks across multiple accelerators.
- **Governance Risk:** Medium. Viseron *does* support face recognition and license plate recognition plugins. An adapter bridging Viseron to SafeTask must strictly filter these out and explicitly deny those capabilities in the payload attestations.
- **Integration Path:** Webhook or MQTT translation script into the Drop-Folder.

### 4. ZoneMinder & Shinobi
- **Status:** Open Source, Local-First.
- **Why they fit:** Legacy heavyweights. Excellent archival capabilities.
- **Governance Risk:** Low. Both are largely agnostic to the content of the video without heavy plugin configuration.
- **Integration Path:** Webhook catchers translating to Drop-Folder.

### 5. Scrypted & Agent DVR
- **Status:** Mixed Licensing / Closed Source.
- **Governance Risk:** Medium to High. While local, their lack of full open-source licensing makes them awkward bedfellows for a fully verifiable, private safety workbench. Defer integration.

### 6. VicoHome & Cloud Cameras
- **Status:** Closed Source, Cloud-Dependent.
- **Governance Risk:** Extreme. SafeTask explicitly prohibits cloud dependencies. Defer entirely.

## Final Recommendations

1. **Safest First Adapter Path:** Implement the **Generic Drop-Folder Explicit Import Plan**. This hardens the airlock boundary before any network traffic is digested.
2. **Best First VMS Target:** **Frigate**. Its MQTT event stream is robust, and its lack of built-in biometric identification makes it the most ethically aligned open-source NVR.
3. **Best Advanced-Vision Exploration Path:** **Viseron**, provided the adapter enforces aggressive filtering against its LPR/Face plugins.
4. **Highest-Risk Path to Defer:** **VicoHome** and any cloud-based API integrations.
