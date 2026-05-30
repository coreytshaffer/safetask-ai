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
