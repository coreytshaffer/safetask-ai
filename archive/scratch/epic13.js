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
