
// Security Remediation: XSS Sanitizer
)'>
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
      obsTbody.innerHTML += `
        <tr>
          <td style=");border: 1px solid #ccc; padding: 8px;">${obs.timestamp}</td>
          <td style="border: 1px solid #ccc; padding: 8px;">${obs.camera_id}</td>
          <td style="border: 1px solid #ccc; padding: 8px;">${obs.description}</td>
        </tr>
      `;
    };
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
      document.getElementById('printSigInfo').innerHTML = `
        <strong>Authorized By:</strong> ${fullInc.authorization.commission_rep_name} (UID: ${fullInc.authorization.commission_uid})<br>
        <strong>Date:</strong> ${fullInc.authorization.timestamp}<br>
        <strong>Secure Room Verified:</strong> Yes
      `;
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
