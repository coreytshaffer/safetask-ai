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

  // Initialize Constellation UI
  const canvas = document.getElementById('constellationCanvas');
  if (canvas) {
    constellation = new ConstellationMenu(canvas);
  }

  // Initialize PiP Dragging
  initPiPDrag();
});

// PiP Drag Logic
function initPiPDrag() {
  const pipWindow = document.getElementById("pipViewer");
  const pipHeader = document.getElementById("pipHeader");
  
  if(!pipWindow || !pipHeader) return;

  let isDragging = false;
  let offsetX, offsetY;

  pipHeader.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - pipWindow.getBoundingClientRect().left;
    offsetY = e.clientY - pipWindow.getBoundingClientRect().top;
    pipWindow.style.transition = 'none'; // remove smooth transition while dragging
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    pipWindow.style.left = `${e.clientX - offsetX}px`;
    pipWindow.style.top = `${e.clientY - offsetY}px`;
    pipWindow.style.right = 'auto'; // Reset right anchor so left/top take over
    pipWindow.style.bottom = 'auto';
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
  });
}

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
async function loadRegulations() {
  try {
    const response = await fetch("regulations.json");
    if (!response.ok) throw new Error("Could not load regulations database");
    regulationsDatabase = await response.json();
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
    sidebarContainer.innerHTML = `
      <div class="empty-regs-state">
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

  const systemPrompt = `You are a Casino Surveillance AI assistant. Your function is to evaluate raw agent notes and generate a formatted, MICS-compliant Incident Report, a short Radio Script, and an Escalation Contact Slate.
WARNING: You are an AI. Maintain a highly professional, objective, and cautious tone. Do not fabricate facts that are not present in the user notes.

RULES:
1. Generate a "formatted_narrative" that rewrites the raw notes into a professional, legally defensible security report.
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

  const userPrompt = `Agent Raw Notes: ${taskDesc}\n${contextInjection}`;

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
    const rawOutput = data.choices[0].message.content;

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
      reasoning: reasoning
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

// 5. EDGE AI SIMULATION (MOCK)
async function triggerEdgeAnomaly(anomalyType, details, camera, timestamp) {
  switchTab('tabJha');

  // Trigger PiP Window
  const pipWindow = document.getElementById("pipViewer");
  if(pipWindow) {
    pipWindow.style.display = "flex";
    document.getElementById("pipTitle").textContent = "VMS Stream: " + camera;
    document.getElementById("pipTimestamp").textContent = timestamp;
    
    // Set mock adjacent cameras
    let camNum = parseInt(camera.replace(/[^\d]/g, ''));
    document.getElementById("pipAdj1").textContent = "Cam " + (camNum + 1);
    document.getElementById("pipAdj2").textContent = "Cam " + (camNum - 1);
  }

  document.getElementById("jhaTaskInput").value = `[AUTOMATED EDGE AI ALERT]
Type: ${anomalyType}
Camera: ${camera}
Timestamp: ${timestamp}
Edge Vision Details: ${details}

Request: Generate an official incident report citing relevant regulations.`;
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
    contextInjection = "\nMANDATORY CASINO MICS/TICS CODES TO COMPLY WITH:\n";
    matchedRegulations.forEach(reg => {
      contextInjection += `- Code: ${reg.code}\n  Title: ${reg.title}\n  Mandate: ${reg.summary}\n`;
    });
  }

  const systemPrompt = `You are a Casino Surveillance AI assistant. Your function is to evaluate raw agent notes and generate a formatted, MICS-compliant Incident Report, a short Radio Script, and an Escalation Contact Slate.
WARNING: You are an AI. Maintain a highly professional, objective, and cautious tone. Do not fabricate facts that are not present in the user notes.

RULES:
1. Generate a "formatted_narrative" that rewrites the raw notes into a professional, legally defensible security report.
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

  const userPrompt = `Agent Raw Notes: ${taskDesc}
${contextInjection}`;

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
    const rawOutput = data.choices[0].message.content;

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
      reasoning: reasoning
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
  slateUl.innerHTML = "";
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
    const rawOutput = data.choices[0].message.content;

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
  slateUl.innerHTML = "";
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
  tempMsg.innerHTML = "<em>Analyzing regulations database...</em>";
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
    let rawOutput = data.choices[0].message.content;

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

  msgDiv.innerHTML = `<strong>${sender}:</strong> ${formattedText}`;
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
  listEl.innerHTML = "";

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
    
    item.innerHTML = `
      <div class="history-item-header">
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
function toggleDictation(inputId, btnId) {
  const btn = document.getElementById(btnId);
  const input = document.getElementById(inputId);
  
  if (btn.classList.contains("active")) {
    btn.classList.remove("active");
    btn.querySelector("span").textContent = "Dictate";
    // Dummy stop
  } else {
    btn.classList.add("active");
    btn.querySelector("span").textContent = "Listening...";
    // Dummy start - insert text after delay
    setTimeout(() => {
      input.value += (input.value ? " " : "") + "Subject was highly uncooperative and appeared to be counting cards.";
      onInputTextChange(inputId === 'jhaTaskInput' ? 'jha' : 'incident');
      toggleDictation(inputId, btnId);
    }, 2500);
  }
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

// 9. CONSTELLATION UI
class ConstellationMenu {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = [];
    this.mouse = { x: null, y: null };
    
    // Categories matching the original presets
    this.categories = [
      { id: 0, label: "Patron Dispute" },
      { id: 1, label: "Slot Malfunction" },
      { id: 2, label: "Medical Emergency" },
      { id: 3, label: "Suspicious Subject" },
      { id: 4, label: "Table Games" },
      { id: 5, label: "Facilities/Maintenance" },
      { id: 6, label: "Theft/Larceny" }
    ];

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

    // Click handler
    this.canvas.addEventListener('click', () => {
      if (!this.mouse.x) return;
      // Find closest node
      let closestNode = null;
      let minDistance = 40; // Click radius
      
      this.nodes.forEach(node => {
        const dx = this.mouse.x - node.x;
        const dy = this.mouse.y - node.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < minDistance) {
          minDistance = dist;
          closestNode = node;
        }
      });
      
      if (closestNode) {
        // Trigger preset
        if (closestNode.cat.id <= 3) {
           loadPreset('jha', closestNode.cat.id);
        } else {
           // Fallback for types without presets
           document.getElementById("jhaTaskInput").value = `Incident Category: ${closestNode.cat.label}\n\nDetails: `;
           onInputTextChange("jha");
        }
        document.getElementById("constellationActiveLabel").textContent = closestNode.cat.label;
        
        // Visual feedback
        closestNode.radius = 8;
        setTimeout(() => { closestNode.radius = 4; }, 200);
      }
    });
  }

  resize() {
    const parent = this.canvas.parentElement;
    this.canvas.width = parent.clientWidth;
    this.canvas.height = parent.clientHeight;
  }

  init() {
    this.resize();
    this.nodes = [];
    // Create nodes for each category plus some decorative background stars
    this.categories.forEach(cat => {
      this.nodes.push(this.createNode(cat, true));
    });
    // Add 15 decorative nodes
    for (let i=0; i<15; i++) {
      this.nodes.push(this.createNode(null, false));
    }
  }

  createNode(category, isMain) {
    return {
      x: Math.random() * this.canvas.width,
      y: Math.random() * this.canvas.height,
      vx: (Math.random() - 0.5) * (isMain ? 0.3 : 0.1),
      vy: (Math.random() - 0.5) * (isMain ? 0.3 : 0.1),
      radius: isMain ? 4 : 1.5,
      cat: category,
      isMain: isMain
    };
  }

  drawLines() {
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        const dx = this.nodes[i].x - this.nodes[j].x;
        const dy = this.nodes[i].y - this.nodes[j].y;
        const distance = Math.sqrt(dx*dx + dy*dy);

        if (distance < 100) {
          this.ctx.beginPath();
          this.ctx.strokeStyle = `rgba(0, 242, 254, ${1 - distance/100})`;
          this.ctx.lineWidth = 0.5;
          this.ctx.moveTo(this.nodes[i].x, this.nodes[i].y);
          this.ctx.lineTo(this.nodes[j].x, this.nodes[j].y);
          this.ctx.stroke();
        }
      }
      
      // Draw lines to mouse
      if (this.mouse.x) {
        const dx = this.nodes[i].x - this.mouse.x;
        const dy = this.nodes[i].y - this.mouse.y;
        const distance = Math.sqrt(dx*dx + dy*dy);
        if (distance < 120) {
          this.ctx.beginPath();
          this.ctx.strokeStyle = `rgba(79, 172, 254, ${0.8 - distance/120})`;
          this.ctx.lineWidth = 1;
          this.ctx.moveTo(this.nodes[i].x, this.nodes[i].y);
          this.ctx.lineTo(this.mouse.x, this.mouse.y);
          this.ctx.stroke();
        }
      }
    }
  }

  drawNodes() {
    this.nodes.forEach(node => {
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = node.isMain ? '#00f2fe' : '#94a3b8';
      
      // Hover effect
      if (node.isMain && this.mouse.x) {
        const dx = node.x - this.mouse.x;
        const dy = node.y - this.mouse.y;
        if (Math.sqrt(dx*dx + dy*dy) < 40) {
          this.ctx.fillStyle = '#fff';
          this.ctx.shadowBlur = 10;
          this.ctx.shadowColor = '#00f2fe';
          this.canvas.style.cursor = 'pointer';
        } else {
          this.ctx.shadowBlur = 0;
        }
      } else {
        this.ctx.shadowBlur = 0;
      }
      
      this.ctx.fill();

      // Draw label
      if (node.isMain) {
        this.ctx.font = "11px Inter";
        this.ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
        this.ctx.fillText(node.cat.label, node.x + 8, node.y + 4);
      }
    });
    
    // Reset cursor if not near any node
    let nearNode = false;
    if (this.mouse.x) {
       for(let node of this.nodes) {
         if(node.isMain) {
           const dx = node.x - this.mouse.x;
           const dy = node.y - this.mouse.y;
           if (Math.sqrt(dx*dx + dy*dy) < 40) { nearNode = true; break; }
         }
       }
    }
    if (!nearNode) this.canvas.style.cursor = 'crosshair';
  }

  updatePositions() {
    this.nodes.forEach(node => {
      node.x += node.vx;
      node.y += node.vy;

      // Bounce off walls
      if (node.x < 0 || node.x > this.canvas.width) node.vx *= -1;
      if (node.y < 0 || node.y > this.canvas.height) node.vy *= -1;
      
      // Slight mouse repel
      if (this.mouse.x) {
         const dx = node.x - this.mouse.x;
         const dy = node.y - this.mouse.y;
         const dist = Math.sqrt(dx*dx + dy*dy);
         if (dist < 80) {
            node.x += dx * 0.01;
            node.y += dy * 0.01;
         }
      }
    });
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.updatePositions();
    this.drawLines();
    this.drawNodes();
    requestAnimationFrame(() => this.animate());
  }
}

