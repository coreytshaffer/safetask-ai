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
