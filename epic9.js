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
      container.innerHTML += `
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
    };
    
  } catch (err) {
    container.innerHTML = '<div style="color: #ff6b6b; text-align: center; margin-top: 20px;">Error loading policies.</div>';
  }
}

// Fetch on load
setTimeout(() => {
  fetchActivePolicies();
}, 2000);
