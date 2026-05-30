
// Security Remediation: XSS Sanitizer
window.sanitizeHTML = function(html) {
  if (typeof html !== 'string') return html;
  return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
             .replace(/on\w+="[^"]*"/gi, '')
             .replace(/on\w+='[^']*'/gi, '')
             .replace(/javascript:/gi, 'safe:');
};

// Security Remediation: Safe Object Access
window.safeProp = function(obj, key) {
  if (key === '__proto__' || key === 'constructor' || key === 'prototype') return undefined;
  return obj ? obj[key] : undefined;
};

/* -------------------------------------------------------------
 * SafeTask AI Casino Surveillance Compliance Platform Logic Engine
 * 100% Offline execution, Graph RAG searching, and LM Studio bridge
 * ------------------------------------------------------------- */

// Register Service Worker for PWA
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js")
      .then(reg => console.log("SafeTask AI: Service Worker active on scope", reg.scope))
      .catch(err => console.error("SafeTask AI: Service Worker activation failed", err));
  });
}

// Global State
let regulationsDatabase = [];
let matchedRegulations = [];
let currentJhaDoc = null;
let currentIncidentDoc = null;
let documentHistory = [];
let researchChatHistory = [];
let activeObservations = [];
let PREFERRED_LANGUAGE = navigator.language || "en-US";
let protectedLiveShots = [];
let activeReviewPanes = [];

// API Configuration defaults
let API_URL = "/api";
let MODEL_NAME = "nvidia/nemotron-3-nano-omni-30b-a3b";
let INFERENCE_TEMP = 0.10;

// Helper to repair common LLM JSON formatting errors
function safeJSONParse(str) {
  try {
    return JSON.parse(str);
  } catch (e) {
    console.warn("Initial JSON parse failed. Attempting basic repair...", e.message);
    try {
      let repaired = str
        .replace(/\}\s*\{/g, '},{')
        .replace(/\]\s*\[/g, '],[')
        .replace(/"\s*\{/g, '",{')
        .replace(/\}\s*"/g, '},"')
        .replace(/\]\s*\{/g, '],{')
        .replace(/\}\s*\[/g, '},[')
        .replace(/(?<=")\s+(?=")/g, '","') 
        .replace(/,\s*([\]}])/g, '$1'); 
      return JSON.parse(repaired);
    } catch (e2) {
      throw new Error(e.message + " | Note: Try generating again.");
    }
  }
}

// Casino Manual Presets 
const JHA_PRESETS = [
  { text: "Subject in a red hat at Blackjack Pit 4 was screaming at the dealer about losing a hand. Subject knocked over a chair, appeared highly intoxicated, and refused to leave when asked by the Pit Boss. Security arrived at 22:15 and detained subject without further incident." },
  { text: "Slot Machine #4092 on the main floor experienced a bill validator error at 01:10 AM. The patron claimed the machine took a $100 bill without registering credits. Slot tech opened the machine to verify the drop box." },
  { text: "Elderly patron fell near the East Entrance escalators at 14:00. Patron claimed the floor was slippery. No spills were located by Security. Paramedics called as a precaution; patron refused transport." },
  { text: "Suspicious subject observed loitering near the cage area for 45 minutes without gambling. Subject wearing sunglasses indoors and taking notes on a mobile device. Monitored via PTZ 89." }
];

const CAMERA_CATALOG = {
  "Camera 18": { location: "North Entrances" },
  "Camera 42": { location: "Table Games Pits" },
  "Camera 09": { location: "Secure Corridors & Cage" }
};

// 1. INITIALIZATION & SETUP
let constellation;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("settingsApiUrl").addEventListener("input", (e) => { API_URL = e.target.value.trim(); });
  document.getElementById("settingsModel").addEventListener("input", (e) => { MODEL_NAME = e.target.value.trim(); });
  document.getElementById("settingsTemperature").addEventListener("input", (e) => {
    INFERENCE_TEMP = parseFloat(e.target.value);
    document.getElementById("tempDisplay").textContent = INFERENCE_TEMP.toFixed(2);
  });

  loadRegulations();
  loadHistoryFromStorage();
  checkLMStudioConnection();
  renderProtectedLiveRail();
  initActiveDutyStack();

  // Initialize Constellation UI
  const canvas = document.getElementById('constellationCanvas');
  if (canvas) {
    constellation = new ConstellationEventGraph(canvas);
  }

  // PiP Dragging is now bound dynamically when panes are spawned
});

function getCameraLocation(cameraId) {
  return CAMERA_CATALOG[cameraId]?.location || "Unmapped Zone";
}

function protectLiveShot(cameraId, location = getCameraLocation(cameraId)) {
  const existing = protectedLiveShots.find(shot => shot.camera_id === cameraId);
  const now = new Date();

  if (existing) {
    existing.location = location;
    existing.last_interaction = now.toLocaleTimeString();
  } else {
    protectedLiveShots.push({
      camera_id: cameraId,
      location: location,
      status: "LIVE | PROTECTED",
      protected_since: now.toLocaleTimeString(),
      last_interaction: now.toLocaleTimeString()
    });
  }

  renderProtectedLiveRail();
}

function releaseProtectedLiveShot(cameraId) {
  protectedLiveShots = protectedLiveShots.filter(shot => shot.camera_id !== cameraId);
  renderProtectedLiveRail();
}

function requestProtectedLiveReplacement(currentCameraId, replacementCameraId) {
  const currentShot = protectedLiveShots.find(shot => shot.camera_id === currentCameraId);
  if (!currentShot) {
    protectLiveShot(replacementCameraId);
    return true;
  }

  const okToReplace = confirm(
    `${currentCameraId} is protected live coverage. Replace it with ${replacementCameraId}?`
  );
  if (!okToReplace) return false;

  releaseProtectedLiveShot(currentCameraId);
  protectLiveShot(replacementCameraId);
  return true;
}

function openPipFeed(cameraId, timestamp, mode = "review") {
  spawnPipPane(cameraId, timestamp, mode);
}

function spawnPipPane(cameraId, timestamp, mode = "review") {
  const container = document.getElementById("pipDeckContainer");
  if (!container) return;

  const paneId = "pip_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
  
  const camNum = parseInt(cameraId.replace(/[^\d]/g, ''), 10);
  const adjacentCameras = Number.isFinite(camNum)
    ? [`Camera ${camNum + 1}`, `Camera ${camNum - 1}`]
    : ["Adjacent +1", "Adjacent -1"];

  const displayTime = timestamp || new Date().toLocaleTimeString();
  const liveBadgeText = mode === "live" ? "LIVE | PROTECTED" : "REVIEW CLIP";
  const liveBadgeClass = mode === "live" ? "pip-live-badge protected" : "pip-live-badge review";
  const reviewLabelText = mode === "live" ? "LIVE FIXED" : "REVIEW CLIP";
  
  // Calculate offset for stacking new panes
  const offsetCount = activeReviewPanes.length;
  const initBottom = 20 + (offsetCount * 30);
  const initRight = 20 + (offsetCount * 30);

  const pipHtml = `
    <div id="${paneId}" class="pip-window pip-active" style="position: absolute; bottom: ${initBottom}px; right: ${initRight}px; pointer-events: auto;">
      <div class="pip-header" id="${paneId}_header">
        <span class="pip-title">${mode === "live" ? "Protected Live" : "Review Clip"}: ${cameraId}</span>
        <button class="pip-close" onclick="closePipPane('${paneId}')">✕</button>
      </div>
      <div class="pip-body">
        <div class="pip-main-feed">
          <div class="pip-video-sim" tabindex="0" id="${paneId}_sim">
            <div class="ptz-bg" id="${paneId}_bg"></div>
            <div class="ptz-crosshair">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(0, 242, 254, 0.7)" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="2" x2="12" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line></svg>
            </div>
            <div class="ptz-active-badge" id="${paneId}_ptz_badge">PTZ ENGAGED (WASD)</div>
            <span class="${liveBadgeClass}">${liveBadgeText}</span>
            <div class="pip-rec-dot"></div>
            <span class="pip-timestamp">2026-05-30 ${displayTime}</span>
            <div class="ptz-controls">
              <div class="ptz-row"><button class="ptz-btn">▲</button></div>
              <div class="ptz-row">
                <button class="ptz-btn">◀</button>
                <button class="ptz-btn ptz-center">⊙</button>
                <button class="ptz-btn">▶</button>
              </div>
              <div class="ptz-row"><button class="ptz-btn">▼</button></div>
              <div class="ptz-zoom">
                <button class="ptz-btn">+</button>
                <button class="ptz-btn">-</button>
              </div>
            </div>
          </div>
        </div>
        <div class="pip-offset-controls">
          <button onclick="offsetReviewTimestamp('${paneId}', -10)">-10s</button>
          <div class="pip-scrubber">
            <div class="pip-scrubber-fill"></div>
          </div>
          <button onclick="offsetReviewTimestamp('${paneId}', 10)">+10s</button>
          <button onclick="syncPipToLive('${paneId}')">Sync</button>
        </div>
        <div class="pip-adjacent-container">
          <div class="pip-adjacent-feed">
            <div class="pip-video-sim sub-feed">
               <div class="pip-scanline"></div>
               <span class="pip-cam-label" style="background: rgba(185, 28, 28, 0.8);">${reviewLabelText}</span>
            </div>
          </div>
          <div class="pip-adjacent-feed">
            <div class="pip-video-sim sub-feed">
               <span class="pip-live-badge" style="top: 4px; left: 6px; font-size: 8px;">LIVE FIXED</span>
               <span class="pip-cam-label" style="bottom: 4px; left: 6px; top: auto;">${adjacentCameras[1]}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  // Remove active from others
  document.querySelectorAll('.pip-window').forEach(w => w.classList.remove('pip-active'));

  // Append new pane
  container.insertAdjacentHTML('beforeend', pipHtml);

  // Bind dragging and PTZ
  const pipWindow = document.getElementById(paneId);
  const pipHeader = document.getElementById(`${paneId}_header`);
  bindPiPDrag(pipWindow, pipHeader);
  bindPTZFlightControls(paneId);

  // Track state
  if (mode === "review") {
    activeReviewPanes.push({
      id: paneId,
      camera_id: cameraId,
      timestamp: displayTime,
      opened_at: new Date().toLocaleTimeString()
    });
  } else {
    const protectedShot = protectedLiveShots.find(shot => shot.camera_id === cameraId);
    if (protectedShot) {
      protectedShot.last_interaction = new Date().toLocaleTimeString();
      renderProtectedLiveRail();
    }
  }

  renderCoverageLoadWarning();
}

function closePipPane(paneId) {
  const pane = document.getElementById(paneId);
  if (pane) pane.remove();
  activeReviewPanes = activeReviewPanes.filter(p => p.id !== paneId);
  renderCoverageLoadWarning();
}

function bindPiPDrag(pipWindow, pipHeader) {
  let isDragging = false;
  let offsetX, offsetY;

  pipHeader.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - pipWindow.getBoundingClientRect().left;
    offsetY = e.clientY - pipWindow.getBoundingClientRect().top;
    pipWindow.style.transition = 'none';
    focusPipPane(pipWindow.id);
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    pipWindow.style.left = `${e.clientX - offsetX}px`;
    pipWindow.style.top = `${e.clientY - offsetY}px`;
    pipWindow.style.right = 'auto';
    pipWindow.style.bottom = 'auto';
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
  });

  pipWindow.addEventListener("mousedown", () => {
    focusPipPane(pipWindow.id);
  });
}

function focusPipPane(paneId) {
  document.querySelectorAll('.pip-window').forEach(w => w.classList.remove('pip-active'));
  const pane = document.getElementById(paneId);
  if (pane) pane.classList.add('pip-active');
}

function offsetReviewTimestamp(paneId, seconds) {
  const tsEl = document.querySelector(`#\${paneId} .pip-timestamp`);
  if (!tsEl) return;
  const parts = tsEl.textContent.split(' ');
  if (parts.length === 2) {
    const d = new Date(`${parts[0]}T\${parts[1]}`);
    d.setSeconds(d.getSeconds() + seconds);
    tsEl.textContent = `${d.toISOString().split('T')[0]} \${d.toTimeString().split(' ')[0]}`;
  }
}

function syncPipToLive(paneId) {
  const tsEl = document.querySelector(`#\${paneId} .pip-timestamp`);
  if (!tsEl) return;
  const now = new Date();
  tsEl.textContent = `${now.toISOString().split('T')[0]} \${now.toTimeString().split(' ')[0]}`;
}


function restoreProtectedLiveShot(cameraId) {
  const shot = protectedLiveShots.find(item => item.camera_id === cameraId);
  if (!shot) return;
  shot.last_interaction = new Date().toLocaleTimeString();
  renderProtectedLiveRail();
  openPipFeed(cameraId, shot.last_interaction, "live");
}

function renderProtectedLiveRail() {
  const rail = document.getElementById("protectedLiveRail");
  const count = document.getElementById("protectedLiveCount");
  if (!rail) return;

  if (count) count.textContent = `${protectedLiveShots.length} Protected`;

  if (protectedLiveShots.length === 0) {
    rail.innerHTML = '<div class="empty-live-rail">No protected live shots.</div>';
    renderCoverageLoadWarning();
    return;
  }

  rail.innerHTML = ""
  protectedLiveShots.forEach(shot => {
    const item = document.createElement("div");
    item.className = "live-rail-item";
    item.innerHTML = `
      <div class=");live-rail-main">
        <span class="live-status-dot"></span>
        <div>
          <div class="live-camera">${shot.camera_id}</div>
          <div class="live-location">${shot.location}</div>
        </div>
      </div>
      <div class="live-rail-meta">
        <span>${shot.status}</span>
        <span>Last touch ${shot.last_interaction}</span>
      </div>
      <div class="live-rail-actions">
        <button class="btn btn-small btn-secondary" onclick="restoreProtectedLiveShot('${shot.camera_id}')">Focus</button>
        <button class="btn btn-small btn-secondary" onclick="releaseProtectedLiveShot('${shot.camera_id}')">Release</button>
      </div>
    `;
    rail.appendChild(item);
  });

  renderCoverageLoadWarning();
}

function renderCoverageLoadWarning() {
  const warning = document.getElementById("coverageLoadWarning");
  const warningText = document.getElementById("coverageLoadText");
  if (!warning || !warningText) return;

  const reviewCount = activeReviewPanes.length;
  const protectedCount = protectedLiveShots.length;
  const shouldWarn = reviewCount > 0 && protectedCount > 0;

  warning.classList.toggle("hidden", !shouldWarn);
  if (!shouldWarn) {
    warningText.textContent = "";
    return;
  }

  warningText.textContent = `${protectedCount} protected live shot(s) and ${reviewCount} active review clip(s). Keep review work in PiP or request coverage support if live activity increases.`;
}

// Previous static PiP Drag logic removed. Replaced by bindPiPDrag for dynamic panes.

// Load Presets
function loadPreset(type, index) {
  if (type === "jha") {
    const preset = JHA_PRESETS[index];
    document.getElementById("jhaTaskInput").value = preset.text;
    onInputTextChange("jha");
  }
}

// Switch UI Navigation Tabs
function switchTab(tabName) {
  document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

  if (tabName === "dashboard") {
    document.getElementById("btnTabDashboard").classList.add("active");
    document.getElementById("tabDashboard").classList.add("active");
    document.getElementById("currentTabTitle").textContent = "Command Center Dashboard";
    document.getElementById("currentTabSubtitle").textContent = "Agent Console: Active Shift & Live Feed";
  } else if (tabName === "jha") {
    document.getElementById("btnTabJha").classList.add("active");
    document.getElementById("tabJha").classList.add("active");
    document.getElementById("currentTabTitle").textContent = "Generative Incident Reports";
    document.getElementById("currentTabSubtitle").textContent = "Generative Reporting & MICS Compliance";
  } else if (tabName === "research") {
    document.getElementById("btnTabResearch").classList.add("active");
    document.getElementById("tabResearch").classList.add("active");
    document.getElementById("currentTabTitle").textContent = "Investigative Research Hub";
    document.getElementById("currentTabSubtitle").textContent = "AI-Assisted MICS/TICS Policy Search";
  } else if (tabName === "admin") {
    document.getElementById("btnTabAdmin").classList.add("active");
    document.getElementById("tabAdmin").classList.add("active");
    document.getElementById("currentTabTitle").textContent = "Admin Policy Deployment";
    document.getElementById("currentTabSubtitle").textContent = "Upload and Deploy Deterministic Regulations";
  } else if (tabName === "settings") {
    document.getElementById("btnTabSettings").classList.add("active");
    document.getElementById("tabSettings").classList.add("active");
    document.getElementById("currentTabTitle").textContent = "Integration Settings";
    document.getElementById("currentTabSubtitle").textContent = "LM Studio Server Connection & Diagnostic Logs";
  }
}

// 2. OFFLINE RAG REFERENCE ENGINE
function pickLocalizedText(textMap) {
  if (!textMap || typeof textMap !== "object") return "";
  return textMap[PREFERRED_LANGUAGE] || textMap["en-US"] || Object.values(textMap)[0] || "";
}

function normalizeRegulationEntries(payload) {
  const entries = Array.isArray(payload) ? payload : (payload.entries || []);

  return entries.map(entry => {
    const operationalText = pickLocalizedText(entry.operational_interpretation);
    const literalText = pickLocalizedText(entry.literal_translation);

    return {
      ...entry,
      code: entry.code || entry.citation || "Uncoded Source",
      title: entry.title || entry.citation || "Untitled Source",
      summary: entry.summary || operationalText || literalText || entry.source_text || "",
      keywords: entry.keywords || entry.topic_tags || [],
      jurisdiction: entry.jurisdiction || payload.jurisdiction || "",
      source_language: entry.source_language || payload.default_language || "",
      confidence: entry.confidence || payload.review_status || "legacy"
    };
  });
}

async function loadRegulations() {
  try {
    const response = await fetch("/policy-packs/gaming/regulations.json");
    if (!response.ok) throw new Error("Could not load regulations database");
    const payload = await response.json();
    regulationsDatabase = normalizeRegulationEntries(payload);
    console.log("Casino MICS/SICS database loaded:", regulationsDatabase.length);
  } catch (error) {
    console.error("Error loading regulations database:", error);
  }
}

function onInputTextChange(type) {
  let text = document.getElementById("jhaTaskInput").value;
  scanRegulations(text, type);
}

function scanRegulations(inputText, type) {
  if (!inputText || inputText.trim().length < 5) {
    updateRegulationsSidebar([], type);
    return [];
  }

  const cleanedText = inputText.toLowerCase();
  const matched = [];

  regulationsDatabase.forEach(reg => {
    let matchScore = 0;
    reg.keywords.forEach(keyword => {
      if (cleanedText.includes(keyword)) {
        matchScore++;
      }
    });

    if (matchScore > 0) {
      matched.push({ ...reg, score: matchScore });
    }
  });

  matched.sort((a, b) => b.score - a.score);
  matchedRegulations = matched;
  updateRegulationsSidebar(matched, type);
  return matched;
}

function updateRegulationsSidebar(matched, type) {
  const sidebarContainer = type === "jha" 
    ? document.getElementById("jhaMatchedRegs") 
    : document.getElementById("incidentMatchedRegs");
  
  const badge = type === "jha" 
    ? document.getElementById("ragBadge") 
    : document.getElementById("incRagBadge");

  if (!sidebarContainer) return;

  badge.textContent = `${matched.length} Regulations Matched`;

  if (matched.length === 0) {
    sidebarContainer.innerHTML = window.sanitizeHTML(`
      <div class=");empty-regs-state">
        <svg viewBox="0 0 24 24" width="36" height="36" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        <p>Type details to trigger matched regulatory sections in real time.</p>
      </div>
    `;
    return;
  }

  let html = "";
  matched.forEach(reg => {
    html += `
      <div class="reg-card">
        <div class="reg-card-header">
          <span class="reg-card-code">${reg.code}</span>
          <span class="history-type-badge badge-jha" style="background-color: var(--accent-gold); color: black;">Score ${reg.score}</span>
        </div>
        <div class="reg-card-title">${reg.title}</div>
        <div class="reg-card-desc">${reg.summary}</div>
      </div>
    `;
  });

  sidebarContainer.innerHTML = html;
}

// 3. LM STUDIO INTEGRATION DIAGNOSTICS
async function checkLMStudioConnection() {
  const connDot = document.getElementById("connDot");
  const connText = document.getElementById("connText");
  const btn = document.getElementById("btnTestConn");
  const settingsBtn = document.getElementById("settingsTestBtn");
  const diagStatus = document.getElementById("diagnosticStatus");
  const diagLatency = document.getElementById("diagnosticLatency");
  const diagActiveModel = document.getElementById("diagnosticActiveModel");

  if (btn) btn.textContent = "Testing...";
  if (settingsBtn) settingsBtn.textContent = "Testing...";

  const startTime = Date.now();

  try {
    const response = await fetch(`${API_URL}/models`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });

    if (response.ok) {
      const data = await response.json();
      const latency = Date.now() - startTime;
      
      const loadedModels = data.data || [];
      const loadedModelName = loadedModels.length > 0 ? loadedModels[0].id : MODEL_NAME;

      connDot.className = "connection-status-dot online";
      connText.textContent = "LM Studio Online";
      
      diagStatus.className = "badge badge-low";
      diagStatus.textContent = "CONNECTED";
      diagLatency.textContent = `${latency} ms`;
      diagActiveModel.textContent = loadedModelName;
      
      if (loadedModels.length > 0) {
        document.getElementById("settingsModel").value = loadedModelName;
        MODEL_NAME = loadedModelName;
      }

      console.log("LM Studio integration active. Found model:", loadedModelName);
      if (btn) btn.textContent = "Online";
      if (settingsBtn) settingsBtn.textContent = "Connected";
      return true;
    } else {
      throw new Error(`Server returned status code ${response.status}`);
    }
  } catch (error) {
    console.warn("Connection to LM Studio failed:", error.message);
    
    connDot.className = "connection-status-dot offline";
    connText.textContent = "LM Studio Offline";

    diagStatus.className = "badge badge-high";
    diagStatus.textContent = "CONNECTION FAULT";
    diagLatency.textContent = "N/A";
    diagActiveModel.textContent = "N/A (Ensure Local Server is running)";
    
    if (btn) btn.textContent = "Offline";
    if (settingsBtn) settingsBtn.textContent = "Retry Ping";
    return false;
  }
}

// 4. GENERATIVE INCIDENT REPORTING BLOCK
async function triggerJhaGeneration() {
  const taskDesc = document.getElementById("jhaTaskInput").value.trim();
  
  if (!taskDesc) {
    alert("Please enter incident raw notes first.");
    return;
  }

  const isOnline = await checkLMStudioConnection();
  if (!isOnline) {
    if (!confirm("LM Studio appears to be offline. Would you like to attempt generation anyway?")) {
      return;
    }
  }

  const loader = document.getElementById("jhaLoader");
  const loaderState = document.getElementById("jhaLoaderState");
  const progressFill = document.getElementById("jhaProgressFill");
  
  loader.classList.remove("hidden");
  loaderState.textContent = "Compiling regulatory context references...";
  progressFill.style.width = "20%";

  let contextInjection = "";
  if (matchedRegulations.length > 0) {
    contextInjection = "\nMANDATORY MICS/SICS RULES TO CITE IN NARRATIVE:\n";
    matchedRegulations.forEach(reg => {
      contextInjection += `- Code: ${reg.code}\n  Title: ${reg.title}\n  Mandate: ${reg.summary}\n`;
    });
  }

  let observationsInjection = "";
  if (activeObservations.length > 0) {
    observationsInjection = "\nSTRUCTURED EVENT OBSERVATIONS:\n";
    activeObservations.forEach(obs => {
      observationsInjection += `[${obs.timestamp}] Cam ${obs.camera_id} (${obs.location}): ${obs.text} (Quality: ${obs.evidence_quality})\n`;
    });
  }

  const systemPrompt = `You are a Casino Surveillance AI assistant. Your function is to evaluate raw agent notes and generate a formatted, MICS-compliant Incident Report, a short Radio Script, and an Escalation Contact Slate.
WARNING: You are an AI. Maintain a highly professional, objective, and cautious tone. Do not fabricate facts that are not present in the user notes.

RULES:
1. Generate a "formatted_narrative" that rewrites the raw notes and structured observations into a professional, legally defensible security report.
2. If mandatory fields like Timestamps or PTZ Camera numbers are missing from the raw notes, note that in the report body (e.g. "[PENDING TIMESTAMP ENTRY]").
3. Draft a 10-second "radio_script" that distills the incident for radio dispatch.
4. Draft a "contact_slate" array of roles that must be notified based on the severity and context (e.g. "Shift Manager", "TGRA Agent on Duty", "Slot Floor Supervisor").
5. You must directly incorporate and cite any matched MICS codes provided in the user context.
6. You MUST conduct your step-by-step analysis inside <think>...</think> tags.
7. After the closing </think> tag, you must output ONLY raw, valid JSON.
8. Output JSON with "category" (e.g. "Security", "Table Games", "Slots", "Facilities") and "severity" (e.g. "Low", "Medium", "High").

JSON SCHEMA:
{
  "category": "String",
  "severity": "String",
  "formatted_narrative": "String (Professional, multi-paragraph incident report)",
  "radio_script": "String (Short, punchy dispatch script)",
  "contact_slate": ["Array of Strings (roles to notify)"]
}`;

  const userPrompt = `Agent Raw Notes: ${taskDesc}\n${observationsInjection}\n${contextInjection}`;

  loaderState.textContent = "Connecting to local LLM... (Drafting Incident Package)";
  progressFill.style.width = "40%";

  try {
    const response = await fetch(`${API_URL}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL_NAME,
        temperature: INFERENCE_TEMP,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ]
      })
    });

    if (!response.ok) throw new Error(`Model request failed with status: ${response.status}`);
    
    loaderState.textContent = "Model complete. Parsing reasoning traces...";
    progressFill.style.width = "75%";

    const data = await response.json();
    const rawOutput = data.(response.choices[0].message.refusal ? 'Error: Model refused' : response.choices[0].message.content);

    let reasoning = "No thought trace captured.";
    let jsonString = rawOutput;

    const thinkMatch = rawOutput.match(/<think>([\s\S]*?)<\/think>/i);
    if (thinkMatch) {
      reasoning = thinkMatch[1].trim();
      jsonString = rawOutput.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
    }

    const firstBrace = jsonString.indexOf('{');
    const lastBrace = jsonString.lastIndexOf('}');
    if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
      jsonString = jsonString.substring(firstBrace, lastBrace + 1);
    }

    loaderState.textContent = "Validating Schema...";
    progressFill.style.width = "90%";

    const jhaData = safeJSONParse(jsonString);

    currentJhaDoc = {
      id: "jha_" + Date.now(),
      type: "jha",
      date: new Date().toLocaleString(),
      task_desc: taskDesc,
      category: jhaData.category || "Unclassified",
      severity: jhaData.severity || "Unassessed",
      formatted_narrative: jhaData.formatted_narrative || "Error generating narrative.",
      radio_script: jhaData.radio_script || "No radio script generated.",
      contact_slate: jhaData.contact_slate || ["Shift Manager"],
      reasoning: reasoning,
      observations: [...activeObservations]
    };

    saveDocument(currentJhaDoc);
    renderJhaOutput();

    loader.classList.add("hidden");
  } catch (error) {
    console.error("Compilation failed:", error);
    loader.classList.add("hidden");
    alert(`Generation failed: ${error.message}. Ensure your local LM Studio server is running.`);
  }
}

function renderJhaOutput() {
  if (!currentJhaDoc) return;

  const outputSection = document.getElementById("jhaOutputSection");
  outputSection.classList.remove("hidden");

  document.getElementById("summaryJhaCategory").textContent = currentJhaDoc.category;
  document.getElementById("summaryJhaSeverity").textContent = currentJhaDoc.severity;
  document.getElementById("jhaNarrativeOutput").value = currentJhaDoc.formatted_narrative;
  document.getElementById("jhaRadioScript").value = currentJhaDoc.radio_script;
  
  const slateUl = document.getElementById("jhaContactSlate");
  slateUl.innerHTML = ""
  currentJhaDoc.contact_slate.forEach(role => {
    const li = document.createElement("li");
    li.textContent = role;
    slateUl.appendChild(li);
  });

  document.getElementById("jhaThoughtContent").textContent = currentJhaDoc.reasoning;
  document.getElementById("jhaThoughtDrawer").open = false;
}

// 5. EDGE AI VISION DASHBOARD BLOCK
async function triggerEdgeAnomaly(title, desc, camera, timestamp) {
  scanRegulations(title + " " + desc, "incident");
  openPipFeed(camera, timestamp, "review");

  const isOnline = await checkLMStudioConnection();
  if (!isOnline) {
    if (!confirm("LM Studio is offline. Proceed anyway?")) {
      return;
    }
  }

  const loader = document.getElementById("incidentLoader");
  const loaderState = document.getElementById("incidentLoaderState");
  const progressFill = document.getElementById("incidentProgressFill");

  loader.classList.remove("hidden");
  loaderState.textContent = "Retrieving VMS Video Stream via API...";
  progressFill.style.width = "10%";

  // Simulate video retrieval delay
  await new Promise(r => setTimeout(r, 1200));

  loaderState.textContent = "Calculating Cryptographic Hash (SHA-256)...";
  progressFill.style.width = "30%";
  
  const mockHash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
  
  await new Promise(r => setTimeout(r, 1000));

  loaderState.textContent = "Compiling Incident Package with Local LLM...";
  progressFill.style.width = "50%";

  let contextInjection = "";
  if (matchedRegulations.length > 0) {
    contextInjection = "\nMANDATORY MICS/SICS RULES TO CITE IN NARRATIVE:\n";
    matchedRegulations.forEach(reg => {
      contextInjection += `- Code: ${reg.code}\n  Title: ${reg.title}\n  Mandate: ${reg.summary}\n`;
    });
  }

  // Mock adjacent spatial camera mapping
  const adjacentCameras = ["Camera " + (parseInt(camera.replace(/[^\d]/g, '')) + 1), "Camera " + (parseInt(camera.replace(/[^\d]/g, '')) - 1)];
  contextInjection += `\nADJACENT CAMERAS (SPATIAL PROXIMITY): ${adjacentCameras.join(', ')}. Recommend checking for cross-angles.\n`;

  const systemPrompt = `You are an AI orchestrator for Casino Surveillance. You have received an automated Edge Node Anomaly.
Draft the incident report based on the anomaly metadata and the regulatory context.

RULES:
1. Explain what the Edge node detected.
2. Directly cite the specific MICS/SICS rule that was violated, or note if liability is negated due to fraudulent intent (like a staged fall).
3. Conduct reasoning in <think>...</think> tags.
4. Output JSON with "narrative", "radio_script", and "contact_slate".

JSON SCHEMA:
{
  "narrative": "String",
  "radio_script": "String",
  "contact_slate": ["String"]
}`;

  const userPrompt = `Edge Anomaly Title: ${title}
Details: ${desc}
Camera: ${camera}
Timestamp: ${timestamp}
Hash: ${mockHash}
${contextInjection}`;

  try {
    const response = await fetch(`${API_URL}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL_NAME,
        temperature: INFERENCE_TEMP,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ]
      })
    });

    if (!response.ok) throw new Error(`Model request failed`);
    
    loaderState.textContent = "Finalizing Package...";
    progressFill.style.width = "90%";

    const data = await response.json();
    const rawOutput = data.(response.choices[0].message.refusal ? 'Error: Model refused' : response.choices[0].message.content);

    let reasoning = "No thought trace captured.";
    let jsonString = rawOutput;

    const thinkMatch = rawOutput.match(/<think>([\s\S]*?)<\/think>/i);
    if (thinkMatch) {
      reasoning = thinkMatch[1].trim();
      jsonString = rawOutput.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
    }

    const firstBrace = jsonString.indexOf('{');
    const lastBrace = jsonString.lastIndexOf('}');
    if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
      jsonString = jsonString.substring(firstBrace, lastBrace + 1);
    }

    const incData = safeJSONParse(jsonString);

    currentIncidentDoc = {
      id: "inc_" + Date.now(),
      type: "incident",
      date: new Date().toLocaleString(),
      inc_date: timestamp,
      location: camera,
      hash: mockHash,
      incident_title: title,
      narrative: incData.narrative || "Error",
      radio_script: incData.radio_script || "Error",
      contact_slate: incData.contact_slate || ["Shift Manager"],
      reasoning: reasoning
    };

    saveDocument(currentIncidentDoc);
    renderIncidentOutput();

    loader.classList.add("hidden");
  } catch (error) {
    console.error("Analysis failed:", error);
    loader.classList.add("hidden");
    alert(`Analysis failed: ${error.message}`);
  }
}

function renderIncidentOutput() {
  if (!currentIncidentDoc) return;

  const outputSection = document.getElementById("incidentOutputSection");
  outputSection.classList.remove("hidden");

  document.getElementById("summaryIncDate").textContent = currentIncidentDoc.inc_date;
  document.getElementById("summaryIncLocation").textContent = currentIncidentDoc.hash;
  document.getElementById("summaryIncSeverity").textContent = "High (Automated)";
  document.getElementById("summaryIncPersonnel").textContent = currentIncidentDoc.incident_title;

  document.getElementById("incGeneratedNarrative").textContent = currentIncidentDoc.narrative;
  document.getElementById("incRadioScript").textContent = currentIncidentDoc.radio_script;
  
  const slateUl = document.getElementById("incContactSlate");
  slateUl.innerHTML = ""
  currentIncidentDoc.contact_slate.forEach(role => {
    const li = document.createElement("li");
    li.textContent = role;
    slateUl.appendChild(li);
  });

  document.getElementById("incThoughtContent").textContent = currentIncidentDoc.reasoning;
  document.getElementById("incidentThoughtDrawer").open = false;
}

// Map simulation helper
function simulateAnomaly(beaconId, statusClass) {
  // Reset all
  document.querySelectorAll('.map-beacon').forEach(b => {
    b.style.display = 'none';
    b.className = 'map-beacon';
  });
  
  const beacon = document.getElementById(beaconId);
  if(beacon) {
    beacon.style.display = 'block';
    beacon.classList.add(statusClass);
  }
}

// 6. INVESTIGATIVE RESEARCH HUB
async function sendResearchQuery() {
  const inputEl = document.getElementById("researchInput");
  const query = inputEl.value.trim();
  if (!query) return;

  inputEl.value = "";
  appendChatMessage("You", query, "user-msg");

  // RAG Search
  const matches = scanRegulations(query, "jha"); // reuse logic to get matches
  let contextInjection = "";
  if (matches && matches.length > 0) {
    contextInjection = "\nRELEVANT CASINO MICS/TICS CODES FOUND IN DATABASE:\n";
    matches.forEach(reg => {
      contextInjection += `- Code: ${reg.code}\n  Title: ${reg.title}\n  Mandate: ${reg.summary}\n`;
    });
  }

  const systemPrompt = `You are the Casino Surveillance AI Assistant. Answer the agent's questions accurately based ONLY on the provided MICS/TICS/SICS database context. If the answer is not in the context, tell the agent to refer to physical manuals.
Be concise, professional, and directly answer the question. Cite the regulation Code.`;

  const userPrompt = `Agent Query: ${query}\n${contextInjection}`;

  // Temporary processing message
  const chatHistory = document.getElementById("chatHistory");
  const tempMsg = document.createElement("div");
  tempMsg.className = "chat-msg ai-msg processing-msg";
  tempMsg.style = "align-self: flex-start; background: rgba(0, 242, 254, 0.05); border: 1px solid var(--accent-cyan); padding: 12px; border-radius: var(--border-radius-sm); max-width: 80%; opacity: 0.5;";
  tempMsg.innerHTML = "<em>Analyzing regulations database...</em>"
  chatHistory.appendChild(tempMsg);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    const response = await fetch(`${API_URL}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL_NAME,
        temperature: 0.2, // slightly higher temp for chat
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ]
      })
    });

    chatHistory.removeChild(tempMsg);

    if (!response.ok) throw new Error("Model request failed.");
    
    const data = await response.json();
    let rawOutput = data.(response.choices[0].message.refusal ? 'Error: Model refused' : response.choices[0].message.content);

    // Filter out think tags from chat response if present
    rawOutput = rawOutput.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();

    appendChatMessage("System", rawOutput, "ai-msg");

  } catch (error) {
    if(chatHistory.contains(tempMsg)) chatHistory.removeChild(tempMsg);
    appendChatMessage("System", `Error querying AI: ${error.message}`, "ai-msg", true);
  }
}

function appendChatMessage(sender, text, cssClass, isError = false) {
  const chatHistory = document.getElementById("chatHistory");
  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-msg ${cssClass}`;
  
  if (cssClass === "user-msg") {
      msgDiv.style = "align-self: flex-end; background: rgba(255, 255, 255, 0.1); border: 1px solid var(--glass-border); padding: 12px; border-radius: var(--border-radius-sm); max-width: 80%; margin-left: auto;";
  } else {
      msgDiv.style = `align-self: flex-start; background: rgba(0, 242, 254, 0.05); border: 1px solid ${isError ? 'var(--accent-red)' : 'var(--accent-cyan)'}; padding: 12px; border-radius: var(--border-radius-sm); max-width: 80%;`;
  }
  
  // Basic markdown formatting
  let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  formattedText = formattedText.replace(/\n/g, '<br>');

  msgDiv.innerHTML = `<strong>${sender}:</strong> ${formattedText}`
  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}


// 7. STORAGE & HISTORY
async function saveDocument(docData) {
  let existingIndex = documentHistory.findIndex(d => d.id === docData.id);
  if (existingIndex >= 0) {
    documentHistory[existingIndex] = docData;
  } else {
    documentHistory.unshift(docData); // Add to top
  }
  
  try {
    await fetch("/api/incidents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(docData)
    });
  } catch (e) {
    console.warn("Could not save to backend database:", e);
  }
  
  renderHistoryList();
}

async function loadHistoryFromStorage() {
  try {
    const response = await fetch("/api/incidents");
    if (response.ok) {
      documentHistory = await response.json();
      renderHistoryList();
    }
  } catch (e) {
    console.warn("Could not load history from backend database:", e);
  }
}

function exportPdf(incidentId) {
  window.open(`/api/export/pdf/${incidentId}`, "_blank");
}

// 8. ADMIN POLICY DEPLOYMENT
let selectedAdminFile = null;

function handleAdminFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    selectedAdminFile = file;
    document.getElementById("adminFileName").textContent = "Selected: " + file.name;
  }
}

async function uploadPolicy() {
  const code = document.getElementById("adminCodeInput").value.trim();
  const title = document.getElementById("adminTitleInput").value.trim();
  const statusEl = document.getElementById("adminUploadStatus");

  if (!code || !title || !selectedAdminFile) {
    statusEl.textContent = "Error: Please provide Code, Title, and a PDF file.";
    statusEl.style.color = "var(--accent-red)";
    return;
  }

  statusEl.textContent = "Uploading and parsing deterministically...";
  statusEl.style.color = "var(--text-muted)";

  const formData = new FormData();
  formData.append("code", code);
  formData.append("title", title);
  formData.append("file", selectedAdminFile);

  try {
    const response = await fetch("/api/policies/upload", {
      method: "POST",
      body: formData
    });

    const result = await response.json();

    if (response.ok) {
      statusEl.textContent = "Success! Policy injected into RAG database.";
      statusEl.style.color = "var(--accent-green)";
      document.getElementById("adminCodeInput").value = "";
      document.getElementById("adminTitleInput").value = "";
      document.getElementById("adminFileInput").value = "";
      document.getElementById("adminFileName").textContent = "";
      selectedAdminFile = null;
      
      // Reload regulations to reflect new data
      loadRegulations();
    } else {
      throw new Error(result.error || "Upload failed");
    }
  } catch (error) {
    statusEl.textContent = "Error: " + error.message;
    statusEl.style.color = "var(--accent-red)";
  }
}

function renderHistoryList(filterText = "") {
  const listEl = document.getElementById("historyList");
  listEl.innerHTML = ""

  const filtered = documentHistory.filter(doc => {
    const text = JSON.stringify(doc).toLowerCase();
    return text.includes(filterText.toLowerCase());
  });

  if (filtered.length === 0) {
    listEl.innerHTML = `<div class="empty-history">No saved documents.</div>`;
    return;
  }

  filtered.forEach(doc => {
    const item = document.createElement("div");
    item.className = "history-item";
    
    let title = doc.type === 'jha' ? "Incident Report Draft" : (doc.incident_title || "Edge Anomaly");
    let subtitle = doc.type === 'jha' ? doc.task_desc.substring(0, 30) + "..." : doc.inc_date;
    
    item.innerHTML = window.sanitizeHTML(`
      <div class=");history-item-header">
        <span class="history-type-badge ${doc.type === 'jha' ? 'badge-jha' : 'badge-inc'}">
          ${doc.type === 'jha' ? 'Gen-Inc' : 'Edge-AI'}
        </span>
        <span class="history-date">${doc.date.split(',')[0]}</span>
      </div>
      <div class="history-title">${title}</div>
      <div class="history-desc">${subtitle}</div>
    `;

    item.addEventListener("click", () => loadDocumentFromHistory(doc));
    listEl.appendChild(item);
  });
}

function loadDocumentFromHistory(doc) {
  if (doc.type === 'jha') {
    switchTab("jha");
    currentJhaDoc = doc;
    renderJhaOutput();
  } else {
    switchTab("dashboard");
    currentIncidentDoc = doc;
    renderIncidentOutput();
  }
}

function filterHistory() {
  const text = document.getElementById("historySearch").value;
  renderHistoryList(text);
}

function clearAllData() {
  if(confirm("Are you sure you want to delete all offline reports from this device? This cannot be undone.")) {
    documentHistory = [];
    localStorage.removeItem("safetask_history");
    renderHistoryList();
    document.getElementById("jhaOutputSection").classList.add("hidden");
    document.getElementById("incidentOutputSection").classList.add("hidden");
  }
}

// 8. UTILITIES
let activeRecognition = null;
let activeDictationBtn = null;

async function checkAudioHardware() {
  try {
    // Need user permission first to read labels
    await navigator.mediaDevices.getUserMedia({ audio: true });
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = devices.filter(d => d.kind === 'audioinput');
    
    // Check if any device label implies a headset or external mic
    const hasHeadset = audioInputs.some(d => {
      const label = d.label.toLowerCase();
      return label.includes('headset') || label.includes('headphone') || label.includes('usb') || label.includes('bluetooth') || label.includes('external');
    });
    
    if (audioInputs.length > 0 && !hasHeadset && audioInputs[0].label !== "") {
      return false; // No headset found
    }
    return true;
  } catch (e) {
    console.warn("Could not enumerate devices", e);
    return true; // Fallback allow if API fails
  }
}

async function toggleDictation(inputId, btnId) {
  const btn = document.getElementById(btnId);
  const input = document.getElementById(inputId);
  
  if (btn.classList.contains("active")) {
    // Stop
    if (activeRecognition) {
      activeRecognition.stop();
      activeRecognition = null;
    }
    btn.classList.remove("active");
    btn.querySelector("span").textContent = "Dictate";
    activeDictationBtn = null;
    return;
  } 

  // Hardware Enforcement
  const isSafe = await checkAudioHardware();
  if (!isSafe) {
    alert("⚠️ Headset Required for Privacy\n\nPlease connect an approved headset to use dictation. Open-air laptop microphones are disabled to prevent crosstalk and privacy violations.");
    return;
  }

  // Start Recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech Recognition is not supported in this browser.");
    return;
  }

  btn.classList.add("active");
  btn.querySelector("span").textContent = "Listening...";
  activeDictationBtn = btn;

  activeRecognition = new SpeechRecognition();
  activeRecognition.continuous = true;
  activeRecognition.interimResults = true;

  activeRecognition.onresult = (event) => {
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      }
    }
    
    if (finalTranscript) {
      // Voice Command Controller
      const cmd = finalTranscript.toLowerCase().trim();
      const pullMatch = cmd.match(/(?:pull|export) (?:the )?(?:last )?(.+?) from (.+)/i);
      
      if (pullMatch) {
        const timeFrame = pullMatch[1];
        const targetCam = pullMatch[2];
        showToast(`Voice Command: Retroactive Export Triggered for ${targetCam}`);
        
        // Open the camera and log an observation to the active thread
        const parsedCamName = targetCam.replace(/\s+/g, '').toUpperCase();
        openPipFeed(parsedCamName);
        
        activeObservations.push({
          id: 'obs_' + Date.now(),
          timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
          camera: parsedCamName,
          location: "Voice Export",
          text: `Automated Video Export Triggered for previous ${timeFrame}.`,
          confidence: "High",
          type: "Export"
        });
        
        if (typeof constellation !== 'undefined' && constellation) {
          constellation.updateGraph(activeObservations);
        }
        renderObservations();
        renderActiveDutyStack();
        return;
      } else if (cmd.startsWith("open camera") || cmd.startsWith("safetask open camera")) {
        const match = cmd.match(/open camera\s*(\w+)/);
        if (match && match[1]) {
          showToast(`Voice Command: Opened Camera ${match[1]}`);
          openPipFeed(match[1]);
          return; // Do not append to text
        }
      } else if (cmd.includes("add observation") || cmd.includes("log observation")) {
        showToast("Voice Command: Open Observation Log");
        openObservationModal();
        return;
      }

      // Append dictation
      const currentVal = input.value;
      input.value = currentVal + (currentVal.endsWith(" ") || currentVal === "" ? "" : " ") + finalTranscript.trim() + " ";
      if (inputId === 'jhaTaskInput') onInputTextChange('jha');
      else if (inputId === 'incidentTaskInput') onInputTextChange('incident');
    }
  };

  activeRecognition.onerror = (event) => {
    console.error("Speech error", event);
    btn.classList.remove("active");
    btn.querySelector("span").textContent = "Dictate";
    activeRecognition = null;
  };

  activeRecognition.onend = () => {
    // Automatically toggle off when speech ends
    if (btn.classList.contains("active")) {
      btn.classList.remove("active");
      btn.querySelector("span").textContent = "Dictate";
      activeRecognition = null;
    }
  };

  activeRecognition.start();
}

function showToast(msg) {
  const toast = document.createElement("div");
  toast.className = "voice-toast";
  toast.innerHTML = window.sanitizeHTML(`
    <svg width=");14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
    ${msg}
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function printDocument(type) {
  window.print();
}

function copyMarkdown(type) {
  let md = "";
  if (type === 'jha' && currentJhaDoc) {
    md = `# Incident Narrative\n${currentJhaDoc.formatted_narrative}\n\n# Radio Script\n${currentJhaDoc.radio_script}\n\n# Escalation Contact Slate\n- ${currentJhaDoc.contact_slate.join('\n- ')}`;
  } else if (type === 'incident' && currentIncidentDoc) {
    md = `# Automated Anomaly Package\n**Title:** ${currentIncidentDoc.incident_title}\n**Camera Hash:** ${currentIncidentDoc.hash}\n\n# Narrative\n${currentIncidentDoc.narrative}\n\n# Contacts\n- ${currentIncidentDoc.contact_slate.join('\n- ')}`;
  }

  if (md) {
    navigator.clipboard.writeText(md).then(() => {
      alert("Markdown copied to clipboard.");
    });
  }
}

// 9. CONSTELLATION UI - SPATIAL EVENT GRAPH
class ConstellationEventGraph {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = [];
    this.edges = [];
    this.mouse = { x: null, y: null };
    
    this.init();
    this.animate();
    
    // Resize handler
    window.addEventListener('resize', () => this.resize());
    
    // Mouse tracking
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - rect.left;
      this.mouse.y = e.clientY - rect.top;
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.mouse.x = null;
      this.mouse.y = null;
    });
  }

  resize() {
    const parent = this.canvas.parentElement;
    if (parent) {
      this.canvas.width = parent.clientWidth;
      this.canvas.height = parent.clientHeight;
      this.updateGraph(activeObservations); // re-layout on resize
    }
  }

  init() {
    this.resize();
    this.updateGraph([]);
  }

  updateGraph(observations) {
    this.nodes = [];
    this.edges = [];
    
    const cx = this.canvas.width / 2;
    const cy = this.canvas.height / 2;

    // Create Incident Core Node
    const coreNode = {
      id: 'core',
      label: 'Incident Core',
      type: 'core',
      x: cx, y: cy,
      vx: 0, vy: 0,
      radius: 14,
      color: '#00f2fe'
    };
    this.nodes.push(coreNode);

    if (!observations || observations.length === 0) return;

    // Extract unique cameras
    const cameras = [...new Set(observations.map(obs => obs.camera_id))];
    const camRadius = Math.min(cx, cy) * 0.4; // Inner orbit
    
    const camNodes = {};
    
    cameras.forEach((camId, idx) => {
      const angle = (Math.PI * 2 * idx) / cameras.length;
      const camNode = {
        id: `cam_${camId}`,
        label: camId,
        type: 'camera',
        x: cx + Math.cos(angle) * camRadius,
        y: cy + Math.sin(angle) * camRadius,
        vx: 0, vy: 0,
        radius: 10,
        color: '#94a3b8'
      };
      this.nodes.push(camNode);
      camNodes[camId] = camNode;
      
      // Edge from core to camera
      this.edges.push({
        source: coreNode,
        target: camNode,
        style: 'solid',
        color: 'rgba(148, 163, 184, 0.4)'
      });
    });

    // Create Observation nodes
    observations.forEach((obs, idx) => {
      const parentCam = camNodes[obs.camera_id];
      const offsetAngle = Math.random() * Math.PI * 2;
      const offsetDist = 40 + Math.random() * 20; // Outer orbit
      
      let r = 5; // Default radius
      if (obs.confidence === 'High') r = 8;
      else if (obs.confidence === 'Low') r = 4;

      let edgeStyle = 'solid';
      let edgeColor = 'rgba(0, 242, 254, 0.8)';
      let nodeColor = '#00f2fe';
      
      if (obs.evidence_quality === 'inferred') {
        edgeStyle = 'dashed';
        edgeColor = 'rgba(255, 153, 0, 0.6)';
        nodeColor = '#ff9900';
      } else if (obs.evidence_quality === 'confirmed') {
        nodeColor = '#00ffcc';
        edgeColor = 'rgba(0, 255, 204, 0.9)';
      }

      const obsNode = {
        id: `obs_${obs.id}`,
        label: obs.text.substring(0, 15) + '...',
        fullText: obs.text,
        type: 'observation',
        x: parentCam.x + Math.cos(offsetAngle) * offsetDist,
        y: parentCam.y + Math.sin(offsetAngle) * offsetDist,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: r,
        color: nodeColor,
        parent: parentCam,
        distToParent: offsetDist
      };
      
      this.nodes.push(obsNode);
      this.edges.push({
        source: parentCam,
        target: obsNode,
        style: edgeStyle,
        color: edgeColor
      });
    });
  }

  updatePositions() {
    this.nodes.forEach(node => {
      if (node.type === 'observation') {
         node.x += node.vx;
         node.y += node.vy;
         
         const dx = node.parent.x - node.x;
         const dy = node.parent.y - node.y;
         const dist = Math.sqrt(dx*dx + dy*dy);
         if (dist > node.distToParent + 15) {
            node.vx += dx * 0.002;
            node.vy += dy * 0.002;
         } else if (dist < node.distToParent - 15) {
            node.vx -= dx * 0.002;
            node.vy -= dy * 0.002;
         }
      }
    });
  }

  drawEdges() {
    this.edges.forEach(edge => {
      this.ctx.beginPath();
      this.ctx.strokeStyle = edge.color;
      this.ctx.lineWidth = 1.5;
      
      if (edge.style === 'dashed') {
        this.ctx.setLineDash([4, 4]);
      } else {
        this.ctx.setLineDash([]);
      }
      
      this.ctx.moveTo(edge.source.x, edge.source.y);
      this.ctx.lineTo(edge.target.x, edge.target.y);
      this.ctx.stroke();
    });
    this.ctx.setLineDash([]); // Reset
  }

  drawNodes() {
    let hoveringNode = null;

    this.nodes.forEach(node => {
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = node.color;
      
      if (this.mouse.x) {
        const dx = node.x - this.mouse.x;
        const dy = node.y - this.mouse.y;
        if (Math.sqrt(dx*dx + dy*dy) < node.radius + 15) {
          hoveringNode = node;
          this.ctx.shadowBlur = 12;
          this.ctx.shadowColor = node.color;
        } else {
          this.ctx.shadowBlur = 0;
        }
      } else {
        this.ctx.shadowBlur = 0;
      }
      
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      if (node.type === 'core' || node.type === 'camera') {
        this.ctx.font = "10px Inter";
        this.ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
        this.ctx.fillText(node.label, node.x + node.radius + 4, node.y + 4);
      }
    });

    if (hoveringNode) {
      this.canvas.style.cursor = 'pointer';
      // Render tooltip
      const text = hoveringNode.type === 'observation' ? hoveringNode.fullText : hoveringNode.label;
      
      // Calculate tooltip box size
      this.ctx.font = "12px Inter";
      const textWidth = this.ctx.measureText(text).width;
      const boxWidth = Math.max(120, textWidth + 20);
      const boxHeight = 28;
      
      let tooltipX = this.mouse.x + 15;
      let tooltipY = this.mouse.y + 15;
      
      // Keep tooltip on screen
      if (tooltipX + boxWidth > this.canvas.width) tooltipX = this.canvas.width - boxWidth - 10;
      if (tooltipY + boxHeight > this.canvas.height) tooltipY = this.canvas.height - boxHeight - 10;

      this.ctx.fillStyle = 'rgba(6, 11, 19, 0.9)';
      this.ctx.fillRect(tooltipX, tooltipY, boxWidth, boxHeight);
      this.ctx.strokeStyle = hoveringNode.color;
      this.ctx.lineWidth = 1;
      this.ctx.strokeRect(tooltipX, tooltipY, boxWidth, boxHeight);
      
      this.ctx.fillStyle = "#fff";
      this.ctx.fillText(text, tooltipX + 10, tooltipY + 19);
    } else {
      this.canvas.style.cursor = 'crosshair';
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.updatePositions();
    this.drawEdges();
    this.drawNodes();
    requestAnimationFrame(() => this.animate());
  }
}

// Graveyard Shift Dark Mode Toggle
function toggleDarkMode(isDark) {
  if (isDark) {
    document.body.classList.add('true-dark-mode');
  } else {
    document.body.classList.remove('true-dark-mode');
  }
}

// OBSERVATION LOGIC
function openObservationModal() {
  document.getElementById('observationModal').style.display = 'flex';
  document.getElementById('obsCameraId').value = '';
  document.getElementById('obsTimestamp').value = '';
  document.getElementById('obsLocation').value = '';
  document.getElementById('obsText').value = '';
  document.getElementById('obsConfidence').value = 'High';
  document.getElementById('obsEvidenceQuality').value = 'observed';
}

function closeObservationModal() {
  document.getElementById('observationModal').style.display = 'none';
}

function saveObservation() {
  const obs = {
    id: Date.now().toString(),
    camera_id: document.getElementById('obsCameraId').value.trim(),
    timestamp: document.getElementById('obsTimestamp').value.trim(),
    location: document.getElementById('obsLocation').value.trim(),
    text: document.getElementById('obsText').value.trim(),
    confidence: document.getElementById('obsConfidence').value,
    evidence_quality: document.getElementById('obsEvidenceQuality').value
  };

  if (!obs.camera_id || !obs.timestamp || !obs.text) {
    alert("Camera ID, Timestamp, and Notes are required.");
    return;
  }

  activeObservations.push(obs);

  // Sort observations chronologically
  activeObservations.sort((a, b) => a.timestamp.localeCompare(b.timestamp));

  renderObservations();
  closeObservationModal();

  // Trigger RAG scan with new info
  onInputTextChange("jha");
  
  if (constellation) {
    constellation.updateGraph(activeObservations);
  }
}

function renderObservations() {
  const container = document.getElementById('observationTimelineList');
  if (!container) return;

  if (activeObservations.length === 0) {
    container.innerHTML = '<div class="empty-history" style="padding: 10px; font-size: 12px;">No structured observations added yet.</div>';
    return;
  }

  let html = '';
  activeObservations.forEach((obs, idx) => {
    html += `
      <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); padding: 10px; border-radius: var(--border-radius-sm); font-size: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span style="font-weight: 600; color: var(--accent-blue);">${obs.timestamp} | ${obs.camera_id}</span>
          <span style="color: var(--text-muted);">${obs.evidence_quality.toUpperCase()}</span>
        </div>
        <div style="margin-bottom: 4px;">${obs.text}</div>
        <div style="font-size: 10px; color: var(--text-secondary);">Location: ${obs.location} | Confidence: ${obs.confidence}</div>
      </div>
    `;
  });

  container.innerHTML = html;
}

// Epic 7: Evidence Registry & Retention Ledger
let evidenceRegistry = [];

function sealEvidencePackage() {
  if (!activeThreadId || !incidentThreads[activeThreadId]) return;
  
  const thread = incidentThreads[activeThreadId];
  if (thread.observations.length === 0) {
    alert("Cannot seal an empty evidence package.");
    return;
  }
  
  const retentionDays = 1095;
  const expirationDate = new Date();
  expirationDate.setDate(expirationDate.getDate() + retentionDays);
  
  const sealedCase = {
    id: thread.id,
    title: thread.title,
    agent: document.getElementById('currentAgentIdLabel') ? document.getElementById('currentAgentIdLabel').innerText : 'System',
    sealedAt: new Date().toLocaleString(),
    expiration: expirationDate.toLocaleDateString(),
    daysRemaining: retentionDays,
    observations: [...thread.observations],
    text: thread.draftText || "",
    videoHash: "sha256-" + Math.random().toString(36).substring(2, 10),
    audioHash: "sha256-" + Math.random().toString(36).substring(2, 10)
  };
  
  evidenceRegistry.push(sealedCase);
  delete incidentThreads[activeThreadId];
  
  // EPIC 16 Integration: Auto-forward to dispatch
  if (typeof dispatchLog !== 'undefined') {
    dispatchLog.unshift({
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      type: 'Surveillance Task',
      location: 'Review Desk',
      details: 'Task generated from sealed Evidence Package ' + sealedCase.id.replace('thread_', 'EV-'),
      status: 'Pending'
    });
    if (typeof renderDispatchLog === 'function') renderDispatchLog();
  }
  
  if (Object.keys(incidentThreads).length === 0) {
    createNewThread("Initial Thread");
  } else {
    switchIncidentThread(Object.keys(incidentThreads)[0]);
  }
  
  showToast("Evidence Package Sealed & Vaulted.");
  renderEvidenceLedger();
}

function renderEvidenceLedger() {
  const container = document.getElementById('evidenceLedgerTable');
  if (!container) return;
  if (evidenceRegistry.length === 0) {
    container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No sealed evidence in registry.</div>';
    return;
  }
  container.innerHTML = ''
  evidenceRegistry.forEach(c => {
    const card = document.createElement('div');
    card.style.background = 'rgba(0,0,0,0.2)';
    card.style.border = '1px solid var(--border-color)';
    card.style.padding = '15px';
    card.style.borderRadius = '8px';
    card.style.cursor = 'pointer';
    card.style.transition = 'all 0.2s';
    card.onmouseover = () => card.style.borderColor = 'var(--accent-cyan)';
    card.onmouseout = () => card.style.borderColor = 'var(--border-color)';
    
    let retentionBadgeColor = c.daysRemaining > 30 ? 'var(--accent-cyan)' : '#ff6b6b';
    let retentionBadge = `<span style="background: rgba(0,0,0,0.5); border: 1px solid ${retentionBadgeColor}; color: ${retentionBadgeColor}; padding: 2px 6px; border-radius: 4px; font-size: 10px;">${c.daysRemaining} Days Left</span>`;
    if (c.daysRemaining > 1000) {
        retentionBadge = `<span style="background: rgba(0,0,0,0.5); border: 1px solid #4ade80; color: #4ade80; padding: 2px 6px; border-radius: 4px; font-size: 10px;">Indefinite Hold</span>`;
    }
    
    card.innerHTML = window.sanitizeHTML(`
      <div style=");display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <strong style="color: #fff; font-size: 14px;">Case: ${c.id.replace('thread_', 'EV-')}</strong>
        ${retentionBadge}
      </div>
      <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">
        Sealed By: ${c.agent} on ${c.sealedAt}<br/>
        Video Hash: <span style="font-family: monospace; color: var(--accent-cyan);">${c.videoHash}</span><br/>
        Audio Hash: <span style="font-family: monospace; color: #ff9900;">${c.audioHash}</span>
      </div>
    `;
    card.onclick = () => renderDistributionSummaries(c);
    container.appendChild(card);
  });
}

function renderDistributionSummaries(sealedCase) {
  const container = document.getElementById('distributionSummaries');
  if (!container) return;
  container.innerHTML = window.sanitizeHTML(`
    <div style=");margin-bottom: 10px; font-size: 13px; color: #fff;"><strong>Case ${sealedCase.id.replace('thread_', 'EV-')}</strong></div>
    <div style="background: rgba(0,242,254,0.05); border-left: 2px solid var(--accent-cyan); padding: 10px; margin-bottom: 10px; border-radius: 0 4px 4px 0;">
      <div style="font-size: 11px; font-weight: bold; color: var(--accent-cyan); margin-bottom: 4px;">Security Dispatch Task (Auto-Forwarded)</div>
      <div style="font-size: 12px; color: var(--text-primary);">Sanitized Task: Follow up with patron regarding reported incident. Evidence hashes appended.</div>
    </div>
    <div style="background: rgba(74,222,128,0.05); border-left: 2px solid #4ade80; padding: 10px; margin-bottom: 10px; border-radius: 0 4px 4px 0;">
      <div style="font-size: 11px; font-weight: bold; color: #4ade80; margin-bottom: 4px;">Risk Management (Auto-Forwarded)</div>
      <div style="font-size: 12px; color: var(--text-primary);">Full liability summary and highly confidential narrative attached. Media retained securely.</div>
    </div>
  `;
}

function approveFieldEvidence(btn) {
  const item = btn.closest('.field-inbox-item');
  if (!item) return;
  if (activeThreadId && incidentThreads[activeThreadId]) {
    activeObservations.push({
      id: 'obs_' + Date.now(),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      camera: "Field Mobile",
      location: "Zone 4",
      text: "Field Photo Approved & Attached: IMG_4492.jpg",
      confidence: "High",
      type: "Media"
    });
    if (typeof constellation !== 'undefined' && constellation) {
      constellation.updateGraph(activeObservations);
    }
    renderObservations();
    renderActiveDutyStack();
    showToast("Field Evidence Attached to Active Thread.");
  }
  item.remove();
}

function denyFieldEvidence(btn) {
  const item = btn.closest('.field-inbox-item');
  if (item) {
    item.remove();
    showToast("Field Evidence Rejected. Remains on Mobile Node.");
  }
}

// Epic 16: Security Management & Dispatch
let currentRole = 'surveillance';
let dispatchLog = [];
let officerRoster = [
  { name: 'Officer Reyes', zone: 'Zone 4', status: 'Available' },
  { name: 'Sgt. Vance', zone: 'Sector A', status: 'On Break' },
  { name: 'Officer Smith', zone: 'Casino Floor', status: 'En Route' }
];
let lostAndFound = [
  { id: 'LF-001', time: '10:15 AM', item: 'iPhone 13 (Blue)', location: 'Slot Bank 40', status: 'Bin A2' },
  { id: 'LF-002', time: '11:30 AM', item: 'Leather Wallet', location: 'Restroom (South)', status: 'Bin C1' }
];

function switchRole(role) {
  currentRole = role;
  if (role === 'dispatch') {
    document.querySelectorAll('.surveillance-only').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.dispatch-only').forEach(el => el.style.display = 'flex');
    switchTab('dispatch');
  } else {
    document.querySelectorAll('.surveillance-only').forEach(el => el.style.display = 'flex');
    document.querySelectorAll('.dispatch-only').forEach(el => el.style.display = 'none');
    switchTab('dashboard');
  }
}

function renderOfficerRoster() {
  const container = document.getElementById('officerRosterList');
  if (!container) return;
  container.innerHTML = ''
  officerRoster.forEach(o => {
    let badge = '#4ade80';
    if (o.status === 'On Break') badge = '#9ca3af';
    if (o.status === 'En Route' || o.status === 'Busy') badge = '#ff9900';
    container.innerHTML += window.sanitizeHTML(`
      <div style=");display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 4px;">
        <div>
          <div style="font-size: 12px; font-weight: bold; color: #fff;">${o.name}</div>
          <div style="font-size: 10px; color: var(--text-secondary);">${o.zone}</div>
        </div>
        <span style="font-size: 10px; border: 1px solid ${badge}; color: ${badge}; padding: 2px 6px; border-radius: 12px;">${o.status}</span>
      </div>
    `;
  });
}

function renderLostAndFound() {
  const container = document.getElementById('lostAndFoundList');
  if (!container) return;
  container.innerHTML = ''
  lostAndFound.forEach(lf => {
    container.innerHTML += window.sanitizeHTML(`
      <div style=");background: rgba(0,0,0,0.2); padding: 8px; border-left: 2px solid #4ade80; border-radius: 0 4px 4px 0;">
        <div style="font-size: 10px; color: var(--text-secondary); margin-bottom: 2px;">${lf.id} | ${lf.time} | ${lf.location}</div>
        <div style="font-size: 12px; font-weight: bold; color: #fff; margin-bottom: 4px;">${lf.item}</div>
        <div style="font-size: 10px; color: #4ade80;">Status: ${lf.status}</div>
      </div>
    `;
  });
}

function renderDispatchLog() {
  const table = document.getElementById('dispatchLogTable');
  if (!table) return;
  table.innerHTML = ''
  if (dispatchLog.length === 0) {
    table.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: var(--text-secondary);">No active dispatch events.</td></tr>';
    return;
  }
  dispatchLog.forEach(log => {
    table.innerHTML += window.sanitizeHTML(`
      <tr style=");border-bottom: 1px solid rgba(255,255,255,0.05);">
        <td style="padding: 8px;">${log.time}</td>
        <td style="padding: 8px; color: var(--accent-cyan); font-weight: bold;">${log.type}</td>
        <td style="padding: 8px;">${log.location}</td>
        <td style="padding: 8px;">${log.details}</td>
        <td style="padding: 8px;">
          <select style="background: rgba(0,0,0,0.5); color: #fff; border: 1px solid var(--border-color); padding: 2px 4px; font-size: 11px;">
            <option ${log.status === 'Pending' ? 'selected' : ''}>Pending</option>
            <option ${log.status === 'En Route' ? 'selected' : ''}>En Route</option>
            <option ${log.status === 'Cleared' ? 'selected' : ''}>Cleared</option>
          </select>
        </td>
      </tr>
    `;
  });
}

function logDispatchEvent() {
  const details = prompt("Enter Dispatch Details:");
  if (details) {
    dispatchLog.unshift({
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      type: 'Routine',
      location: 'Unknown',
      details: details,
      status: 'Pending'
    });
    renderDispatchLog();
  }
}

function addLostAndFound() {
  const item = prompt("Enter recovered item description:");
  if (item) {
    lostAndFound.unshift({
      id: 'LF-' + Math.floor(100 + Math.random() * 900),
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
      item: item,
      location: 'Drop box',
      status: 'Logged'
    });
    renderLostAndFound();
  }
}

// PTZ Flight Controls
function bindPTZFlightControls(paneId) {
  const sim = document.getElementById(paneId + '_sim');
  const bg = document.getElementById(paneId + '_bg');
  if (!sim || !bg) return;
  
  let bgX = 0, bgY = 0;
  let zoom = 1;
  let isDragging = false;
  let velocityX = 0, velocityY = 0;
  let ptzLoop = null;
  
  const updatePTZ = () => {
    bgX += velocityX;
    bgY += velocityY;
    bg.style.backgroundPosition = `${bgX}px \${bgY}px`;
    bg.style.transform = `scale(\${zoom})`;
    if (isDragging || velocityX !== 0 || velocityY !== 0) {
      ptzLoop = requestAnimationFrame(updatePTZ);
    }
  };
  
  sim.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    isDragging = true;
    sim.classList.add('ptz-active');
    sim.focus();
    const rect = sim.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const moveHandler = (moveEvent) => {
      if (!isDragging) return;
      const dx = moveEvent.clientX - centerX;
      const dy = moveEvent.clientY - centerY;
      velocityX = -(dx / rect.width) * 20;
      velocityY = -(dy / rect.height) * 20;
    };
    const upHandler = () => {
      isDragging = false;
      velocityX = 0;
      velocityY = 0;
      sim.classList.remove('ptz-active');
      window.removeEventListener('mousemove', moveHandler);
      window.removeEventListener('mouseup', upHandler);
    };
    window.addEventListener('mousemove', moveHandler);
    window.addEventListener('mouseup', upHandler);
    if (!ptzLoop) updatePTZ();
    e.stopPropagation();
  });
  
  sim.addEventListener('wheel', (e) => {
    e.preventDefault();
    zoom += e.deltaY > 0 ? -0.1 : 0.1;
    zoom = Math.max(0.5, Math.min(zoom, 5));
    bg.style.transform = `scale(\${zoom})`;
  });
  
  sim.addEventListener('keydown', (e) => {
    const step = 20;
    let moved = false;
    switch (e.key.toLowerCase()) {
      case 'w': bgY += step; moved = true; break;
      case 's': bgY -= step; moved = true; break;
      case 'a': bgX += step; moved = true; break;
      case 'd': bgX -= step; moved = true; break;
      case 'q': zoom = Math.max(0.5, zoom - 0.1); bg.style.transform = `scale(\${zoom})`; moved = true; break;
      case 'e': zoom = Math.min(5, zoom + 0.1); bg.style.transform = `scale(\${zoom})`; moved = true; break;
    }
    if (moved) {
      bg.style.backgroundPosition = `${bgX}px \${bgY}px`;
      e.preventDefault();
    }
  });
}

// Global Hotkeys
window.addEventListener('keydown', (e) => {
  if (e.altKey) {
    switch (e.key.toLowerCase()) {
      case 'n': e.preventDefault(); createNewThread('Manual Thread'); showToast('Hotkey: New Thread Started'); break;
      case 'd': e.preventDefault(); toggleDictation('incidentTaskInput', 'incidentDictationBtn'); break;
      case 's': e.preventDefault(); sealEvidencePackage(); break;
      case 'l': e.preventDefault(); openHandoffModal(); break;
      case '1': e.preventDefault(); switchTab('dashboard'); break;
      case '2': e.preventDefault(); switchTab('jha'); break;
      case '3': e.preventDefault(); switchTab('evidence'); break;
    }
  }
});

// Init calls
setTimeout(() => {
  if (typeof renderOfficerRoster === 'function') renderOfficerRoster();
  if (typeof renderLostAndFound === 'function') renderLostAndFound();
  if (typeof renderDispatchLog === 'function') renderDispatchLog();
}, 500);
// Epic 17: Keywatcher Integration
let keywatcherLedger = [];

function renderKeywatcherLedger() {
  const container = document.getElementById('keywatcherLedger');
  if (!container) return;
  container.innerHTML = ''
  
  if (keywatcherLedger.length === 0) {
    container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; padding: 10px;">Waiting for Keywatcher Sync...</div>';
    return;
  }
  
  keywatcherLedger.forEach(event => {
    let color = 'var(--text-primary)';
    let badge = '';
    if (event.isHighValue) {
      color = '#ff9900';
      badge = '<span style="background: rgba(255,153,0,0.2); color: #ff9900; border: 1px solid #ff9900; padding: 1px 4px; border-radius: 4px; font-size: 8px; margin-left: 5px;">RESTRICTED ALARM</span>';
    } else if (event.type === 'Returned') {
      color = '#4ade80';
    }
    
    container.innerHTML += window.sanitizeHTML(`
      <div style=");background: rgba(0,0,0,0.2); padding: 6px; border-left: 2px solid ${color}; border-radius: 0 4px 4px 0; margin-bottom: 4px;">
        <div style="font-size: 9px; color: var(--text-secondary);">${event.time} | Cabinet ${event.cabinet}</div>
        <div style="font-size: 11px; font-weight: bold; color: ${color};">${event.keyName} (${event.type}) ${badge}</div>
        <div style="font-size: 10px; color: var(--text-secondary);">User: ${event.user}</div>
      </div>
    `;
  });
}

function startKeywatcherSimulation() {
  setInterval(() => {
    // Only simulate if dispatch tab is open or we want background events
    if (Math.random() > 0.7) {
      const isReturn = Math.random() > 0.5;
      const keyName = isReturn ? 'Drop Box 4' : 'Maintenance Cart';
      
      keywatcherLedger.unshift({
        time: new Date().toLocaleTimeString('en-US', { hour12: false }),
        cabinet: 'South Floor',
        keyName: keyName,
        type: isReturn ? 'Returned' : 'Pulled',
        user: 'Officer ' + Math.floor(100 + Math.random() * 900),
        isHighValue: false
      });
      
      // Keep only last 10
      if (keywatcherLedger.length > 10) keywatcherLedger.pop();
      renderKeywatcherLedger();
    }
  }, 10000);
}

function triggerHighValueKey() {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false });
  
  // 1. Add to Keywatcher Ledger
  keywatcherLedger.unshift({
    time: time,
    cabinet: 'Vault Vestibule',
    keyName: 'Master Casino Key',
    type: 'Pulled',
    user: 'Unidentified User',
    isHighValue: true
  });
  if (keywatcherLedger.length > 10) keywatcherLedger.pop();
  renderKeywatcherLedger();
  
  // 2. Add to Dispatch Log
  if (typeof dispatchLog !== 'undefined') {
    dispatchLog.unshift({
      time: time,
      type: 'ALARM: Restricted Key',
      location: 'Vault Vestibule',
      details: 'Master Casino Key pulled. Verification required.',
      status: 'Pending'
    });
    if (typeof renderDispatchLog === 'function') renderDispatchLog();
  }
  
  // 3. Auto-spawn PiP for Surveillance with gentle pulse
  if (typeof spawnPipPane === 'function') {
    // Spawn PiP
    const paneId = spawnPipPane('Camera 12 (Vault Key Room)', time, 'live');
    
    // Find the spawned pane's video sim to add the gentle pulse class
    // Since spawnPipPane doesn't return the paneId, we'll find the last added pip
    setTimeout(() => {
      const pips = document.querySelectorAll('.pip-window');
      if (pips.length > 0) {
        const latestPip = pips[pips.length - 1];
        const sim = latestPip.querySelector('.pip-video-sim');
        if (sim) {
          sim.classList.add('border-pulse-warning');
        }
      }
    }, 100);
    
    // Log observation if thread active
    if (typeof activeObservations !== 'undefined' && typeof activeThreadId !== 'undefined' && activeThreadId) {
      activeObservations.push({
        id: 'obs_' + Date.now(),
        timestamp: time,
        camera: 'Camera 12',
        location: 'Vault Vestibule',
        text: "Automated Syslog Alarm: Master Casino Key Pulled. Verifying identity.",
        confidence: "High",
        type: "System Alarm"
      });
      if (typeof constellation !== 'undefined' && constellation) {
        constellation.updateGraph(activeObservations);
      }
      if (typeof renderObservations === 'function') renderObservations();
      if (typeof renderActiveDutyStack === 'function') renderActiveDutyStack();
    }
  }
  
  showToast("High Value Key Pulled. Dispatch & Surveillance Notified.");
}

// Start simulation after 2 seconds
setTimeout(() => {
  if (typeof renderKeywatcherLedger === 'function') renderKeywatcherLedger();
  startKeywatcherSimulation();
}, 2000);
// Epic 8: Recall Search & Research Hub Toggle
let currentResearchMode = 'policy';

function setResearchMode(mode) {
  currentResearchMode = mode;
  
  const btnPolicy = document.getElementById('btnModePolicy');
  const btnRecall = document.getElementById('btnModeRecall');
  const chatHistory = document.getElementById('chatHistory');
  const recallResults = document.getElementById('recallResults');
  const desc = document.getElementById('researchDesc');
  const input = document.getElementById('researchInput');
  
  if (mode === 'policy') {
    btnPolicy.className = 'btn primary-btn';
    btnRecall.className = 'btn nav-btn';
    chatHistory.style.display = 'flex';
    recallResults.style.display = 'none';
    desc.innerText = 'Ask questions regarding MICS/TICS policies or compliance procedures. The AI will pull from the offline regulations database.';
    input.placeholder = 'e.g., What are the personnel requirements for a table drop?';
  } else {
    btnPolicy.className = 'btn nav-btn';
    btnRecall.className = 'btn primary-btn';
    chatHistory.style.display = 'none';
    recallResults.style.display = 'flex';
    desc.innerText = 'Search through historical incidents, observation logs, and sealed evidence packages using keywords.';
    input.placeholder = 'e.g., fight in Zone 4, Master Casino Key...';
    
    // Clear previous results or show default
    if (recallResults.innerHTML.trim() === '') {
      recallResults.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">Enter a keyword to search the incident database.</div>';
    }
  }
}

async function executeResearchQuery() {
  const input = document.getElementById('researchInput');
  const query = input.value.trim();
  if (!query) return;
  
  if (currentResearchMode === 'policy') {
    // Re-route to existing sendResearchQuery if policy
    if (typeof sendResearchQuery === 'function') {
        sendResearchQuery();
    }
  } else {
    // Epic 8 Recall Search
    const recallResults = document.getElementById('recallResults');
    recallResults.innerHTML = '<div style="color: var(--accent-cyan); text-align: center; margin-top: 20px;">Searching database...</div>';
    
    try {
      const response = await fetch('/api/search?q=' + encodeURIComponent(query));
      const results = await response.json();
      
      if (results.length === 0) {
        recallResults.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No historical incidents found matching your query.</div>';
        return;
      }
      
      recallResults.innerHTML = ''
      results.forEach(inc => {
        let snippetHtml = inc.snippet ? `<div style="font-size: 12px; color: var(--text-secondary); margin-top: 8px; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px; font-style: italic;">"...${inc.snippet}..."</div>` : '';
        
        recallResults.innerHTML += window.sanitizeHTML(`
          <div style=");background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='var(--accent-cyan)'" onmouseout="this.style.borderColor='var(--border-color)'">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <strong style="color: #fff; font-size: 14px;">${inc.incident_title || 'Untitled Incident'}</strong>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">ID: ${inc.id} | Date: ${inc.date || inc.inc_date} | Location: ${inc.location}</div>
              </div>
              <span style="background: rgba(0, 242, 254, 0.1); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); padding: 2px 6px; border-radius: 4px; font-size: 10px;">${inc.category || inc.type}</span>
            </div>
            ${snippetHtml}
          </div>
        `;
      });
      
    } catch (err) {
      console.error(err);
      recallResults.innerHTML = '<div style="color: #ff6b6b; text-align: center; margin-top: 20px;">Error searching database. Check server connection.</div>';
    }
  }
}
// Epic 18: Subject Profile Management (BOLO)
async function fetchSubjects() {
  const container = document.getElementById('subjectsListContainer');
  if (!container) return;
  
  try {
    const response = await fetch('/api/subjects');
    const subjects = await response.json();
    
    container.innerHTML = ''
    
    if (subjects.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; padding: 20px; grid-column: 1/-1;">No subjects found.</div>';
      return;
    }
    
    subjects.forEach(subj => {
      let badgeColor = '#4ade80';
      if (subj.status === 'Banned') badgeColor = '#ff6b6b';
      if (subj.risk_level === 'High') badgeColor = '#ff6b6b';
      
      container.innerHTML += window.sanitizeHTML(`
        <div style=");background: rgba(0,0,0,0.3); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; display: flex; gap: 16px;">
          <div style="width: 80px; height: 100px; background: rgba(255,255,255,0.05); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 32px; color: var(--text-secondary);">
            👤
          </div>
          <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <strong style="color: #fff; font-size: 14px;">${subj.name}</strong>
              <span style="background: rgba(0,0,0,0.5); border: 1px solid ${badgeColor}; color: ${badgeColor}; padding: 2px 6px; border-radius: 4px; font-size: 10px;">${subj.status}</span>
            </div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Aliases: ${subj.aliases}</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Facial: ${subj.facial_hash} | Gait: ${subj.gait_profile}</div>
            <div style="font-size: 12px; color: var(--text-primary); margin-top: 8px; font-style: italic;">"${subj.notes}"</div>
          </div>
        </div>
      `;
    });
  } catch (err) {
    console.error(err);
    container.innerHTML = '<div style="color: #ff6b6b; text-align: center; padding: 20px; grid-column: 1/-1;">Failed to load subjects.</div>';
  }
}

function triggerBiometricHit(type) {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false });
  let msg = '';
  let pulseClass = '';
  let conf = '';
  let subj = 'John "The Count" Doe';
  
  if (type === 'facial') {
    msg = `Facial Recognition Match: ${subj}`;
    pulseClass = 'border-pulse-critical';
    conf = '98% (High)';
  } else {
    msg = `Gait Recognition Profile Match: ${subj}`;
    pulseClass = 'border-pulse-warning';
    conf = '68% (Low - Requires Verification)';
  }
  
  // 1. Spawn PiP with the correct pulse
  if (typeof spawnPipPane === 'function') {
    spawnPipPane(`Floor Cam 4 (${type.toUpperCase()} ALERT)`, time, 'live');
    setTimeout(() => {
      const pips = document.querySelectorAll('.pip-window');
      if (pips.length > 0) {
        const latestPip = pips[pips.length - 1];
        const sim = latestPip.querySelector('.pip-video-sim');
        if (sim) {
          sim.classList.add(pulseClass);
        }
      }
    }, 100);
  }
  
  // 2. Add to active thread if present
  if (typeof activeObservations !== 'undefined' && typeof activeThreadId !== 'undefined' && activeThreadId) {
    activeObservations.push({
      id: 'obs_' + Date.now(),
      timestamp: time,
      camera: 'Floor Cam 4',
      location: 'Main Floor',
      text: `BOLO ALERT: ${msg}. Confidence: ${conf}. Agent verification requested.`,
      confidence: conf.includes('High') ? 'High' : 'Low',
      type: "System Alarm"
    });
    if (typeof constellation !== 'undefined' && constellation) {
      constellation.updateGraph(activeObservations);
    }
    if (typeof renderObservations === 'function') renderObservations();
    if (typeof renderActiveDutyStack === 'function') renderActiveDutyStack();
  }
  
  // 3. Dispatch log if available
  if (typeof dispatchLog !== 'undefined') {
    dispatchLog.unshift({
      time: time,
      type: 'BOLO ALERT',
      location: 'Main Floor',
      details: `${msg} (${conf})`,
      status: 'Pending'
    });
    if (typeof renderDispatchLog === 'function') renderDispatchLog();
  }
  
  showToast(msg);
}

// Init call
setTimeout(() => {
  fetchSubjects();
}, 2000);
// Epic 9: Admin Governance Console
async function uploadPolicy() {
  const codeInput = document.getElementById('adminPolicyCode');
  const titleInput = document.getElementById('adminPolicyTitle');
  const fileInput = document.getElementById('adminPolicyFile');
  const statusDiv = document.getElementById('uploadStatus');
  
  if (!codeInput.value || !titleInput.value || !fileInput.files[0]) {
    statusDiv.style.color = 'var(--accent-amber)';
    statusDiv.innerText = 'Please fill out all fields and select a PDF.';
    return;
  }
  
  statusDiv.style.color = 'var(--accent-cyan)';
  statusDiv.innerText = 'Uploading and processing document...';
  
  const formData = new FormData();
  formData.append('code', codeInput.value);
  formData.append('title', titleInput.value);
  formData.append('file', fileInput.files[0]);
  
  try {
    const response = await fetch('/api/policies/upload', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (response.ok) {
      statusDiv.style.color = '#4ade80';
      statusDiv.innerText = `Success! Processed as ${result.policy.code}`;
      codeInput.value = '';
      titleInput.value = '';
      fileInput.value = '';
      fetchActivePolicies(); // Refresh dashboard
    } else {
      statusDiv.style.color = '#ff6b6b';
      statusDiv.innerText = `Error: ${result.error}`;
    }
  } catch (err) {
    statusDiv.style.color = '#ff6b6b';
    statusDiv.innerText = `Upload failed: ${err.message}`;
  }
}

async function fetchActivePolicies() {
  const container = document.getElementById('activePoliciesContainer');
  if (!container) return;
  
  try {
    // We fetch from the existing regulations file
    const response = await fetch('/policy-packs/gaming/regulations.json');
    if (!response.ok) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No policies found.</div>';
      return;
    }
    
    const policies = await response.json();
    
    container.innerHTML = ''
    
    if (policies.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No active policies.</div>';
      return;
    }
    
    policies.forEach(p => {
      container.innerHTML += window.sanitizeHTML(`
        <div style=");background: rgba(0,0,0,0.5); border: 1px solid var(--border-color); border-radius: 4px; padding: 12px; display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <div style="color: var(--accent-cyan); font-weight: bold; font-size: 13px;">${p.code}</div>
            <div style="color: #fff; font-size: 12px; margin-top: 2px;">${p.title}</div>
            <div style="color: var(--text-secondary); font-size: 11px; margin-top: 4px; font-style: italic;">Tags: ${(p.keywords || []).slice(0,5).join(', ')}</div>
          </div>
          <div style="background: rgba(255,255,255,0.1); border-radius: 4px; padding: 2px 6px; font-size: 10px; color: var(--text-secondary);">
            v${p.version || 1}
          </div>
        </div>
      `;
    });
    
  } catch (err) {
    container.innerHTML = '<div style="color: #ff6b6b; text-align: center; margin-top: 20px;">Error loading policies.</div>';
  }
}

// Fetch on load
setTimeout(() => {
  fetchActivePolicies();
}, 2000);
// Epic 10: Governance, RBAC & PDF Exports

function switchRole(role) {
  // Hide all role-specific elements first
  document.querySelectorAll('.surveillance-only').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.dispatch-only').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.management-only').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.auditor-only').forEach(el => el.style.display = 'none');
  
  // Show base auditor-hidden elements (unless auditor)
  document.querySelectorAll('.auditor-hidden').forEach(el => el.classList.remove('hidden'));

  let defaultTab = 'dashboard';

  if (role === 'surveillance') {
    document.querySelectorAll('.surveillance-only').forEach(el => el.style.display = 'flex');
  } else if (role === 'dispatch') {
    document.querySelectorAll('.dispatch-only').forEach(el => el.style.display = 'flex');
    defaultTab = 'dispatch';
  } else if (role === 'management') {
    document.querySelectorAll('.surveillance-only').forEach(el => el.style.display = 'flex');
    document.querySelectorAll('.management-only').forEach(el => el.style.display = 'flex');
    // Management gets everything
  } else if (role === 'auditor') {
    document.querySelectorAll('.auditor-only').forEach(el => el.style.display = 'flex');
    // Auditor sees very little
    document.querySelectorAll('.auditor-hidden').forEach(el => el.classList.add('hidden'));
    defaultTab = 'auditor';
    fetchAuditorDashboard();
  }

  // Auto-switch to the appropriate default tab for the role
  switchTab(defaultTab);
}

// Ensure the CSS handles .auditor-hidden.hidden { display: none !important; }

async function fetchAuditorDashboard() {
  const container = document.getElementById('auditorIncidentsContainer');
  if (!container) return;
  
  container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">Loading incident ledger...</div>';
  
  try {
    const response = await fetch('/api/incidents');
    const data = await response.json();
    
    if (!data || data.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No finalized incidents found.</div>';
      return;
    }
    
    container.innerHTML = ''
    
    data.forEach(inc => {
      // Create a nice card for the auditor
      const html = `
        <div style="background: rgba(0,0,0,0.5); border: 1px solid var(--border-color); border-radius: 4px; padding: 16px; display: flex; flex-direction: column; gap: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <div style="color: var(--accent-cyan); font-weight: bold; font-size: 14px;">${inc.title || 'Incident Report'}</div>
              <div style="color: var(--text-secondary); font-size: 11px;">ID: ${inc.id} | Date: ${inc.date}</div>
            </div>
            <div style="font-family: monospace; font-size: 10px; color: var(--accent-amber); max-width: 150px; word-break: break-all; text-align: right;">
              SEAL: ${inc.evidence_hash.substring(0, 16)}...
            </div>
          </div>
          <div style="color: #fff; font-size: 12px; line-height: 1.4;">
            ${inc.summary || 'No summary available.'}
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
            <button class="btn nav-btn" style="font-size: 11px; padding: 4px 8px;" onclick='exportToPDF(${JSON.stringify(inc).replace(/'/g, "&#39;")})'>
              Export PDF
            </button>
            <button class="btn nav-btn" style="font-size: 11px; padding: 4px 8px;" onclick='emailReport(${JSON.stringify(inc).replace(/'/g, "&#39;")})'>
              Email Report
            </button>
          </div>
        </div>
      `;
      container.innerHTML += html;
    });
    
  } catch (err) {
    container.innerHTML = '<div style="color: #ff6b6b; text-align: center; margin-top: 20px;">Error loading ledger.</div>';
  }
}

function exportToPDF(inc) {
  // Populate the hidden print template
  document.getElementById('printTitle').innerText = inc.title || 'Official Incident Report';
  document.getElementById('printId').innerText = inc.id;
  document.getElementById('printDate').innerText = inc.date;
  document.getElementById('printLocation').innerText = 'Casino Floor'; // Mock
  document.getElementById('printHash').innerText = inc.evidence_hash;
  document.getElementById('printNarrative').innerText = inc.summary || '';
  
  const obsTbody = document.getElementById('printObservations');
  obsTbody.innerHTML = ''
  
  if (inc.observations && inc.observations.length > 0) {
    inc.observations.forEach(obs => {
      obsTbody.innerHTML += window.sanitizeHTML(`
        <tr>
          <td style=");border: 1px solid #ccc; padding: 8px;">${obs.timestamp}</td>
          <td style="border: 1px solid #ccc; padding: 8px;">${obs.camera_id}</td>
          <td style="border: 1px solid #ccc; padding: 8px;">${obs.description}</td>
        </tr>
      `;
    });
  } else {
    obsTbody.innerHTML = `<tr><td colspan="3" style="border: 1px solid #ccc; padding: 8px; text-align: center;">No observations attached.</td></tr>`;
  }
  
  // Trigger print dialog (CSS @media print handles the rest)
  window.print();
}

function emailReport(inc) {
  // Feature Request: Email Integration
  // For the prototype, we trigger a standard mailto: link pre-filled with the incident summary
  // In a full implementation, this would trigger an SMTP POST to the python backend.
  const subject = encodeURIComponent(`SafeTask Sealed Report: ${inc.title || inc.id}`);
  let body = `Official Incident Report: ${inc.title || inc.id}\n`;
  body += `Date: ${inc.date}\n`;
  body += `Cryptographic Seal: ${inc.evidence_hash}\n\n`;
  body += `Narrative:\n${inc.summary || ''}\n\n`;
  body += `To view full evidence, please log into the SafeTask Auditor Ledger.`;
  
  body = encodeURIComponent(body);
  
  window.location.href = `mailto:stakeholder@gamingcommission.gov?subject=${subject}&body=${body}`;
}
// Epic 11: Release Authorization & E-Signature
let sigCanvas, sigCtx;
let isDrawing = false;
let currentAuthIncidentId = null;

function initSignatureCanvas() {
  sigCanvas = document.getElementById('sigCanvas');
  if (!sigCanvas) return;
  sigCtx = sigCanvas.getContext('2d');
  
  // Set drawing styles
  sigCtx.strokeStyle = '#000000';
  sigCtx.lineWidth = 2;
  sigCtx.lineCap = 'round';
  sigCtx.lineJoin = 'round';

  sigCanvas.addEventListener('mousedown', startDrawing);
  sigCanvas.addEventListener('mousemove', draw);
  sigCanvas.addEventListener('mouseup', stopDrawing);
  sigCanvas.addEventListener('mouseout', stopDrawing);
  
  // Touch support
  sigCanvas.addEventListener('touchstart', handleTouchStart, { passive: false });
  sigCanvas.addEventListener('touchmove', handleTouchMove, { passive: false });
  sigCanvas.addEventListener('touchend', stopDrawing);
}

function getCursorPosition(e) {
  const rect = sigCanvas.getBoundingClientRect();
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  };
}

function handleTouchStart(e) {
  e.preventDefault();
  const touch = e.touches[0];
  const mouseEvent = new MouseEvent('mousedown', {
    clientX: touch.clientX,
    clientY: touch.clientY
  });
  sigCanvas.dispatchEvent(mouseEvent);
}

function handleTouchMove(e) {
  e.preventDefault();
  const touch = e.touches[0];
  const mouseEvent = new MouseEvent('mousemove', {
    clientX: touch.clientX,
    clientY: touch.clientY
  });
  sigCanvas.dispatchEvent(mouseEvent);
}

function startDrawing(e) {
  isDrawing = true;
  const pos = getCursorPosition(e);
  sigCtx.beginPath();
  sigCtx.moveTo(pos.x, pos.y);
}

function draw(e) {
  if (!isDrawing) return;
  const pos = getCursorPosition(e);
  sigCtx.lineTo(pos.x, pos.y);
  sigCtx.stroke();
}

function stopDrawing() {
  isDrawing = false;
  sigCtx.closePath();
}

function clearSignature() {
  if (sigCtx) sigCtx.clearRect(0, 0, sigCanvas.width, sigCanvas.height);
}

function openAuthModal(incidentId) {
  currentAuthIncidentId = incidentId;
  document.getElementById('authRepName').value = localStorage.getItem('authRepName') || '';
  document.getElementById('authUid').value = localStorage.getItem('authUid') || '';
  document.getElementById('authSecureRoom').checked = false;
  
  clearSignature();
  
  const savedSig = localStorage.getItem('authSignature');
  const reuseBtn = document.getElementById('reuseSigBtn');
  if (savedSig) {
    reuseBtn.style.display = 'inline';
  } else {
    reuseBtn.style.display = 'none';
  }
  
  if (!sigCanvas) initSignatureCanvas();
  document.getElementById('authModal').style.display = 'block';
}

function closeAuthModal() {
  document.getElementById('authModal').style.display = 'none';
  currentAuthIncidentId = null;
}

function reuseSignature() {
  const savedSig = localStorage.getItem('authSignature');
  if (savedSig) {
    const img = new Image();
    img.onload = () => {
      clearSignature();
      sigCtx.drawImage(img, 0, 0);
    };
    img.src = savedSig;
  }
}

async function submitAuthorization() {
  const name = document.getElementById('authRepName').value;
  const uid = document.getElementById('authUid').value;
  const secureRoom = document.getElementById('authSecureRoom').checked;
  const saveSig = document.getElementById('authSaveSig').checked;
  
  if (!name || !uid) {
    alert("Please enter Representative Name and UID.");
    return;
  }
  if (!secureRoom) {
    alert("You must verify that you reviewed the footage in a Secure Review Room.");
    return;
  }
  
  // Check if canvas is blank
  const blankCanvas = document.createElement('canvas');
  blankCanvas.width = sigCanvas.width;
  blankCanvas.height = sigCanvas.height;
  if (sigCanvas.toDataURL() === blankCanvas.toDataURL()) {
    alert("Please provide a digital signature.");
    return;
  }
  
  const sigB64 = sigCanvas.toDataURL('image/png');
  
  if (saveSig) {
    localStorage.setItem('authRepName', name);
    localStorage.setItem('authUid', uid);
    localStorage.setItem('authSignature', sigB64);
  }
  
  const payload = {
    commission_rep_name: name,
    commission_uid: uid,
    secure_room_reviewed: 1,
    signature_b64: sigB64
  };
  
  try {
    const response = await fetch(`/api/incidents/${currentAuthIncidentId}/authorize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (response.ok) {
      closeAuthModal();
      fetchAuditorDashboard(); // refresh ledger
    } else {
      alert("Error saving authorization.");
    }
  } catch(e) {
    alert("Network error.");
  }
}

// Override fetchAuditorDashboard to include Authorize button and badges
window.fetchAuditorDashboard = async function() {
  const container = document.getElementById('auditorIncidentsContainer');
  if (!container) return;
  
  container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">Loading incident ledger...</div>';
  
  try {
    const response = await fetch('/api/incidents');
    const data = await response.json();
    
    // data is an object: { incidents: [...] } because we reverted app.py to return jsonify(incidents) 
    // wait, I reverted it to `jsonify(incidents)`. So it is an array.
    const incidents = Array.isArray(data) ? data : (data.incidents || []);
    
    if (incidents.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No finalized incidents found.</div>';
      return;
    }
    
    container.innerHTML = ''
    
    incidents.forEach(inc => {
      const isAuth = inc.authorized;
      const authBadge = isAuth 
        ? `<span style="background: rgba(74, 222, 128, 0.2); color: #4ade80; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #4ade80;">AUTHORIZED</span>`
        : `<span style="background: rgba(255, 171, 0, 0.2); color: #ffab00; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ffab00;">PENDING RELEASE</span>`;
        
      const authBtn = !isAuth
        ? `<button class="btn btn-primary" style="font-size: 11px; padding: 4px 8px;" onclick='openAuthModal("${inc.id}")'>Authorize Release</button>`
        : '';
        
      const html = `
        <div style="background: rgba(0,0,0,0.5); border: 1px solid ${isAuth ? '#4ade80' : 'var(--border-color)'}; border-radius: 4px; padding: 16px; display: flex; flex-direction: column; gap: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="color: var(--accent-cyan); font-weight: bold; font-size: 14px;">${inc.title || 'Incident Report'}</div>
                ${authBadge}
              </div>
              <div style="color: var(--text-secondary); font-size: 11px; margin-top: 4px;">ID: ${inc.id} | Date: ${inc.date}</div>
            </div>
            <div style="font-family: monospace; font-size: 10px; color: var(--accent-amber); max-width: 150px; word-break: break-all; text-align: right;">
              SEAL: ${inc.evidence_hash ? inc.evidence_hash.substring(0, 16) + '...' : 'N/A'}
            </div>
          </div>
          <div style="color: #fff; font-size: 12px; line-height: 1.4;">
            ${inc.summary || 'No summary available.'}
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
            ${authBtn}
            <button class="btn nav-btn" style="font-size: 11px; padding: 4px 8px;" onclick='exportToPDF(${JSON.stringify(inc).replace(/'/g, "&#39;")})'>
              Export PDF
            </button>
            <button class="btn nav-btn" style="font-size: 11px; padding: 4px 8px;" onclick='emailReport(${JSON.stringify(inc).replace(/'/g, "&#39;")})'>
              Email Report
            </button>
          </div>
        </div>
      `;
      container.innerHTML += html;
    });
    
  } catch (err) {
    container.innerHTML = '<div style="color: #ff6b6b; text-align: center; margin-top: 20px;">Error loading ledger.</div>';
  }
};

// Override exportToPDF to stamp the authorization if present
window.exportToPDF = async function(inc) {
  document.getElementById('printTitle').innerText = inc.title || 'Official Incident Report';
  document.getElementById('printId').innerText = inc.id;
  document.getElementById('printDate').innerText = inc.date;
  document.getElementById('printLocation').innerText = inc.location || 'Casino Floor';
  document.getElementById('printHash').innerText = inc.evidence_hash || 'N/A';
  document.getElementById('printNarrative').innerText = inc.summary || '';
  
  const obsTbody = document.getElementById('printObservations');
  obsTbody.innerHTML = ''
  if (inc.observations && inc.observations.length > 0) {
    inc.observations.forEach(obs => {
      obsTbody.innerHTML += `<tr><td style="border: 1px solid #ccc; padding: 8px;">${obs.timestamp}</td><td style="border: 1px solid #ccc; padding: 8px;">${obs.camera_id}</td><td style="border: 1px solid #ccc; padding: 8px;">${obs.description}</td></tr>`;
    });
  } else {
    obsTbody.innerHTML = `<tr><td colspan="3" style="border: 1px solid #ccc; padding: 8px; text-align: center;">No observations attached.</td></tr>`;
  }
  
  // Handle signature stamping
  const sigBlock = document.getElementById('printSignatureBlock');
  if (inc.authorized) {
    // We need to fetch the full incident details to get the signature base64
    const res = await fetch(`/api/incidents/${inc.id}`);
    const fullInc = await res.json();
    if (fullInc.authorization) {
      document.getElementById('printSigInfo').innerHTML = window.sanitizeHTML(`
        <strong>Authorized By:</strong> ${fullInc.authorization.commission_rep_name} (UID: ${fullInc.authorization.commission_uid})<br>
        <strong>Date:</strong> ${fullInc.authorization.timestamp}<br>
        <strong>Secure Room Verified:</strong> Yes
      `);
      document.getElementById('printSigImage').src = fullInc.authorization.signature_b64;
      sigBlock.style.display = 'block';
    } else {
      sigBlock.style.display = 'none';
    }
  } else {
    sigBlock.style.display = 'none';
  }
  
  setTimeout(() => window.print(), 500); // give image time to load
};

// Initialize canvas if modal exists
setTimeout(initSignatureCanvas, 1000);
// Epic 12: Telephonic Auth & Digital Evidence Link

let currentAuthType = 'physical';

function toggleAuthType(type) {
  currentAuthType = type;
  if (type === 'physical') {
    document.getElementById('btnAuthPhysical').className = 'btn primary-btn';
    document.getElementById('btnAuthPhone').className = 'btn nav-btn';
    document.getElementById('physicalAuthSection').style.display = 'block';
    document.getElementById('telephonicAuthSection').style.display = 'none';
  } else {
    document.getElementById('btnAuthPhysical').className = 'btn nav-btn';
    document.getElementById('btnAuthPhone').className = 'btn primary-btn';
    document.getElementById('physicalAuthSection').style.display = 'none';
    document.getElementById('telephonicAuthSection').style.display = 'block';
  }
}

// Override submitAuthorization from Epic 11
window.submitAuthorization = async function() {
  const name = document.getElementById('authRepName').value;
  const uid = document.getElementById('authUid').value;
  const secureRoom = document.getElementById('authSecureRoom').checked;
  const saveSig = document.getElementById('authSaveSig').checked;
  
  if (!name || !uid) {
    alert("Please enter Representative Name and UID.");
    return;
  }
  if (!secureRoom) {
    alert("You must verify that you reviewed the footage in a Secure Review Room.");
    return;
  }
  
  const payload = {
    commission_rep_name: name,
    commission_uid: uid,
    secure_room_reviewed: 1,
    auth_type: currentAuthType
  };
  
  if (currentAuthType === 'physical') {
    // Check if canvas is blank
    const blankCanvas = document.createElement('canvas');
    blankCanvas.width = sigCanvas.width;
    blankCanvas.height = sigCanvas.height;
    if (sigCanvas.toDataURL() === blankCanvas.toDataURL()) {
      alert("Please provide a digital signature.");
      return;
    }
    
    const sigB64 = sigCanvas.toDataURL('image/png');
    
    if (saveSig) {
      localStorage.setItem('authRepName', name);
      localStorage.setItem('authUid', uid);
      localStorage.setItem('authSignature', sigB64);
    }
    payload.signature_b64 = sigB64;
    payload.call_time = '';
  } else {
    // Telephonic
    const callTime = document.getElementById('authCallTime').value;
    if (!callTime) {
      alert("Please provide the Time of Call.");
      return;
    }
    payload.call_time = callTime;
    payload.signature_b64 = '';
  }
  
  try {
    const response = await fetch(`/api/incidents/${currentAuthIncidentId}/authorize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (response.ok) {
      closeAuthModal();
      fetchAuditorDashboard(); // refresh ledger
    } else {
      alert("Error saving authorization.");
    }
  } catch(e) {
    alert("Network error.");
  }
};

// Override fetchAuditorDashboard from Epic 11
window.fetchAuditorDashboard = async function() {
  const container = document.getElementById('auditorIncidentsContainer');
  if (!container) return;
  
  container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">Loading incident ledger...</div>';
  
  try {
    const response = await fetch('/api/incidents');
    const data = await response.json();
    
    const incidents = Array.isArray(data) ? data : (data.incidents || []);
    
    if (incidents.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No finalized incidents found.</div>';
      return;
    }
    
    container.innerHTML = ''
    
    incidents.forEach(inc => {
      const isAuth = inc.authorized;
      const authBadge = isAuth 
        ? `<span style="background: rgba(74, 222, 128, 0.2); color: #4ade80; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #4ade80;">AUTHORIZED</span>`
        : `<span style="background: rgba(255, 171, 0, 0.2); color: #ffab00; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ffab00;">PENDING RELEASE</span>`;
        
      const authBtn = !isAuth
        ? `<button class="btn btn-primary" style="font-size: 11px; padding: 4px 8px;" onclick='openAuthModal("${inc.id}")'>Authorize Release</button>`
        : `<button class="btn btn-secondary" style="font-size: 11px; padding: 4px 8px; border-color: var(--accent-cyan); color: var(--accent-cyan);" onclick='generateEvidenceLink("${inc.id}")'>Generate LE Link</button>`;
        
      const html = `
        <div style="background: rgba(0,0,0,0.5); border: 1px solid ${isAuth ? '#4ade80' : 'var(--border-color)'}; border-radius: 4px; padding: 16px; display: flex; flex-direction: column; gap: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="color: var(--accent-cyan); font-weight: bold; font-size: 14px;">${inc.title || 'Incident Report'}</div>
                ${authBadge}
              </div>
              <div style="color: var(--text-secondary); font-size: 11px; margin-top: 4px;">ID: ${inc.id} | Date: ${inc.date}</div>
            </div>
            <div style="font-family: monospace; font-size: 10px; color: var(--accent-amber); max-width: 150px; word-break: break-all; text-align: right;">
              SEAL: ${inc.evidence_hash ? inc.evidence_hash.substring(0, 16) + '...' : 'N/A'}
            </div>
          </div>
          <div style="color: #fff; font-size: 12px; line-height: 1.4;">
            ${inc.summary || 'No summary available.'}
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
            ${authBtn}
            <button class="btn nav-btn" style="font-size: 11px; padding: 4px 8px;" onclick='exportToPDF(${JSON.stringify(inc).replace(/'/g, "&#39;")})'>
              Export PDF
            </button>
            <button class="btn nav-btn" style="font-size: 11px; padding: 4px 8px;" onclick='emailReport(${JSON.stringify(inc).replace(/'/g, "&#39;")})'>
              Email Report
            </button>
          </div>
        </div>
      `;
      container.innerHTML += html;
    });
    
  } catch (err) {
    container.innerHTML = '<div style="color: #ff6b6b; text-align: center; margin-top: 20px;">Error loading ledger.</div>';
  }
};

async function generateEvidenceLink(incidentId) {
  try {
    const res = await fetch(`/api/incidents/${incidentId}/link`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      document.getElementById('generatedLinkUrl').innerText = window.location.origin + data.link;
      document.getElementById('generatedLinkPin').innerText = data.pin;
      document.getElementById('linkModal').style.display = 'block';
    } else {
      alert(data.error || "Could not generate link.");
    }
  } catch(e) {
    alert("Network error.");
  }
}

// Override exportToPDF to handle Telephonic display
window.exportToPDF = async function(inc) {
  document.getElementById('printTitle').innerText = inc.title || 'Official Incident Report';
  document.getElementById('printId').innerText = inc.id;
  document.getElementById('printDate').innerText = inc.date;
  document.getElementById('printLocation').innerText = inc.location || 'Casino Floor';
  document.getElementById('printHash').innerText = inc.evidence_hash || 'N/A';
  document.getElementById('printNarrative').innerText = inc.summary || '';
  
  const obsTbody = document.getElementById('printObservations');
  obsTbody.innerHTML = ''
  if (inc.observations && inc.observations.length > 0) {
    inc.observations.forEach(obs => {
      obsTbody.innerHTML += `<tr><td style="border: 1px solid #ccc; padding: 8px;">${obs.timestamp}</td><td style="border: 1px solid #ccc; padding: 8px;">${obs.camera_id}</td><td style="border: 1px solid #ccc; padding: 8px;">${obs.description}</td></tr>`;
    });
  } else {
    obsTbody.innerHTML = `<tr><td colspan="3" style="border: 1px solid #ccc; padding: 8px; text-align: center;">No observations attached.</td></tr>`;
  }
  
  // Handle signature stamping
  const sigBlock = document.getElementById('printSignatureBlock');
  if (inc.authorized) {
    const res = await fetch(`/api/incidents/${inc.id}`);
    const fullInc = await res.json();
    if (fullInc.authorization) {
      if (fullInc.authorization.auth_type === 'telephonic') {
        document.getElementById('printSigInfo').innerHTML = window.sanitizeHTML(`
          <strong>Authorized By:</strong> ${fullInc.authorization.commission_rep_name} (UID: ${fullInc.authorization.commission_uid})<br>
          <strong>Method:</strong> Telephonic Override<br>
          <strong>Time of Call:</strong> ${fullInc.authorization.call_time}<br>
          <strong>Reason:</strong> ${inc.title || inc.category || ');Incident Override'}<br>
          <strong>Secure Room Verified:</strong> Yes
        `;
        document.getElementById('printSigImage').style.display = 'none';
      } else {
        document.getElementById('printSigInfo').innerHTML = window.sanitizeHTML(`
          <strong>Authorized By:</strong> ${fullInc.authorization.commission_rep_name} (UID: ${fullInc.authorization.commission_uid})<br>
          <strong>Date:</strong> ${fullInc.authorization.timestamp}<br>
          <strong>Secure Room Verified:</strong> Yes
        `);
        document.getElementById('printSigImage').src = fullInc.authorization.signature_b64;
        document.getElementById('printSigImage').style.display = 'block';
      }
      sigBlock.style.display = 'block';
    } else {
      sigBlock.style.display = 'none';
    }
  } else {
    sigBlock.style.display = 'none';
  }
  
  setTimeout(() => window.print(), 500); 
};
// Epic 13: Subject Profile Management & Biometrics

async function fetchSubjects() {
  const container = document.getElementById('subjectsGrid');
  if (!container) return;
  
  container.innerHTML = '<div style="color: var(--text-secondary);">Loading biometric database...</div>';
  
  try {
    const res = await fetch('/api/subjects');
    const data = await res.json();
    
    if (!data.subjects || data.subjects.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary);">No subjects found in database.</div>';
      return;
    }
    
    container.innerHTML = ''
    data.subjects.forEach(sub => {
      let color = 'var(--text-secondary)';
      if (sub.risk_level === 'High') color = '#ff6b6b';
      else if (sub.risk_level === 'Medium') color = '#ffab00';
      else if (sub.risk_level === 'Low') color = '#4ade80';
      
      const html = `
        <div style="background: rgba(0,0,0,0.5); border: 1px solid ${color}; border-radius: 4px; padding: 15px; display: flex; gap: 15px;">
          <div style="width: 80px; height: 80px; background: #222; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: ${color};">
            <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="1.5" fill="none"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </div>
          <div style="flex: 1;">
            <div style="font-weight: bold; color: ${color}; font-size: 16px;">${sub.name}</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 5px;">Aliases: ${sub.aliases || 'N/A'}</div>
            <div style="display: flex; gap: 5px; margin-bottom: 5px;">
              <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 10px;">${sub.status}</span>
              <span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 10px;">Risk: ${sub.risk_level}</span>
            </div>
            <div style="font-size: 10px; font-family: monospace; color: var(--accent-cyan);">
              F-HASH: ${sub.facial_hash}<br>
              G-PROF: ${sub.gait_profile}
            </div>
          </div>
        </div>
      `;
      container.innerHTML += html;
    });
    
  } catch (err) {
    container.innerHTML = '<div style="color: #ff6b6b;">Error loading subjects.</div>';
  }
}

// Intercept switchTab to load subjects
const originalSwitchTab = window.switchTab;
window.switchTab = function(tabId) {
  if (originalSwitchTab) {
    originalSwitchTab(tabId);
  } else {
    // Fallback if not hooked properly
    document.querySelectorAll('.tab-pane').forEach(t => t.style.display = 'none');
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    
    if (tabId === 'dashboard') {
      document.getElementById('tabDashboard').style.display = 'flex';
      document.getElementById('btnTabDashboard').classList.add('active');
    } else if (tabId === 'subjects') {
      document.getElementById('tabSubjects').style.display = 'block';
      document.getElementById('btnTabSubjects').classList.add('active');
    } else if (tabId === 'dispatch') {
      document.getElementById('tabDispatch').style.display = 'flex';
      document.getElementById('btnTabDispatch').classList.add('active');
    } else if (tabId === 'keywatcher') {
      document.getElementById('tabKeywatcher').style.display = 'block';
      document.getElementById('btnTabKeywatcher').classList.add('active');
    } else if (tabId === 'admin') {
      document.getElementById('tabAdmin').style.display = 'block';
      document.getElementById('btnTabAdmin').classList.add('active');
    } else if (tabId === 'auditor') {
      document.getElementById('tabAuditor').style.display = 'block';
    }
  }
  
  if (tabId === 'subjects') fetchSubjects();
  
  // Show Biometric Scan button only on Dashboard for Surveillance/Management
  const scanBtn = document.getElementById('biometricScanBtn');
  if (scanBtn) {
    if (tabId === 'dashboard' && currentRole !== 'Government Auditor' && currentRole !== 'Dispatch') {
      scanBtn.style.display = 'block';
    } else {
      scanBtn.style.display = 'none';
    }
  }
};

let currentHitlMatch = null;

async function initiateBiometricScan() {
  const btn = document.getElementById('biometricScanBtn');
  const originalText = btn.innerHTML;
  btn.innerHTML = 'Scanning Feed...'
  btn.disabled = true;
  
  try {
    const res = await fetch('/api/biometrics/scan', { method: 'POST' });
    const data = await res.json();
    
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.disabled = false;
      
      if (res.ok && data.match) {
        currentHitlMatch = data.match;
        document.getElementById('hitlRefName').innerText = data.match.name;
        document.getElementById('hitlRefStatus').innerText = `Status: ${data.match.status} | Risk: ${data.match.risk_level}`;
        document.getElementById('hitlConfidence').innerText = `CONFIDENCE: ${data.confidence}%`;
        
        let color = '#4ade80';
        if (data.match.risk_level === 'High') color = '#ff6b6b';
        else if (data.match.risk_level === 'Medium') color = '#ffab00';
        
        document.getElementById('hitlRefName').style.color = color;
        
        document.getElementById('hitlModal').style.display = 'block';
      } else {
        alert("Scan complete. No matches found.");
      }
    }, 1500); // simulate delay
  } catch(e) {
    btn.innerHTML = originalText;
    btn.disabled = false;
    alert("Scan failed.");
  }
}

function verifyAndEscalate() {
  if (!currentHitlMatch) return;
  document.getElementById('hitlModal').style.display = 'none';
  
  // Actually create an incident thread
  const narrative = `[SYSTEM] Biometric hit confirmed by Human-In-The-Loop. Subject identified as ${currentHitlMatch.name} (Risk: ${currentHitlMatch.risk_level}). F-HASH: ${currentHitlMatch.facial_hash}. G-PROF: ${currentHitlMatch.gait_profile}. Dispatching units.`;
  
  const id = "INC-" + Math.floor(Math.random()*90000 + 10000);
  const inc = {
    id: id,
    type: "incident",
    date: new Date().toLocaleTimeString('en-US', { hour12: false }),
    inc_date: new Date().toISOString().split('T')[0],
    category: "Biometric Detection",
    severity: currentHitlMatch.risk_level === 'High' ? "Critical" : "High",
    incident_title: `Biometric Match: ${currentHitlMatch.name}`,
    location: "CAM_21_PTZ",
    narrative: narrative,
    status: "active"
  };
  
  // Submit to backend
  fetch('/api/incidents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(inc)
  }).then(() => {
    switchRole(currentRole); // Force refresh
    setTimeout(() => {
      // Find the new tab and switch to it
      const tabs = document.querySelectorAll('.thread-tab');
      if (tabs.length > 0) {
        tabs[0].click();
      }
    }, 500);
  });
}
