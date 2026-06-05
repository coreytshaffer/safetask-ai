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
    
    if (!data.incidents || data.incidents.length === 0) {
      container.innerHTML = '<div style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No finalized incidents found.</div>';
      return;
    }
    
    container.innerHTML = ''
    
    data.incidents.forEach(inc => {
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
