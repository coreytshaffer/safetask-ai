document.addEventListener('DOMContentLoaded', () => {
    // Auto Shift Theme (Graveyard: 2300-0700 uses dark mode)
    function checkShiftTheme() {
        const hour = new Date().getHours();
        if (hour >= 23 || hour < 7) {
            document.body.classList.remove('light-mode');
        } else {
            document.body.classList.add('light-mode');
        }
    }
    checkShiftTheme();
    setInterval(checkShiftTheme, 60000);

    // Epic 20: Camera Drag and Drop
    const cameraItems = document.querySelectorAll('.camera-item');
    const mainMonitor = document.getElementById('main-monitor');
    const mainMonitorImg = document.getElementById('main-monitor-img');
    const mainMonitorTitle = document.getElementById('main-monitor-title');
    const dropOverlay = document.getElementById('drop-overlay');

    cameraItems.forEach(item => {
        item.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', JSON.stringify({
                cam: item.getAttribute('data-cam'),
                title: item.getAttribute('data-title'),
                img: item.getAttribute('data-img')
            }));
        });
    });

    if (mainMonitor) {
        mainMonitor.addEventListener('dragover', (e) => {
            e.preventDefault();
            mainMonitor.classList.add('drag-over');
            dropOverlay.style.display = 'flex';
        });

        mainMonitor.addEventListener('dragleave', (e) => {
            e.preventDefault();
            mainMonitor.classList.remove('drag-over');
            dropOverlay.style.display = 'none';
        });

        mainMonitor.addEventListener('drop', (e) => {
            e.preventDefault();
            mainMonitor.classList.remove('drag-over');
            dropOverlay.style.display = 'none';

            try {
                const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                if (data && data.img) {
                    mainMonitorImg.src = data.img;
                    mainMonitorTitle.textContent = data.title;
                    
                    // Trigger a brief pulse effect on the main monitor
                    mainMonitor.animate([
                        { boxShadow: '0 0 0 0 rgba(136,192,208,0.7)' },
                        { boxShadow: '0 0 0 20px rgba(136,192,208,0)' }
                    ], {
                        duration: 500,
                        easing: 'ease-out'
                    });
                }
            } catch (err) {
                console.error("Invalid drop data");
            }
        });
    }

    // Epic 21: Numpad Camera Switching
    const numpadHud = document.getElementById('numpad-hud');
    const numpadInput = document.getElementById('numpad-input');
    let numpadBuffer = '';
    let numpadTimeout = null;

    document.addEventListener('keydown', (e) => {
        // Only active when Live Surveillance tab is visible
        const liveTab = document.getElementById('live-tab');
        if (!liveTab || !liveTab.classList.contains('active')) return;
        
        // Ignore if typing in an input or textarea
        if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

        if (e.key >= '0' && e.key <= '9') {
            numpadBuffer += e.key;
            if (numpadHud && numpadInput) {
                numpadInput.textContent = numpadBuffer;
                numpadHud.style.opacity = '1';
                
                // Clear after 3 seconds of inactivity
                clearTimeout(numpadTimeout);
                numpadTimeout = setTimeout(() => {
                    numpadBuffer = '';
                    numpadHud.style.opacity = '0';
                }, 3000);
            }
        } else if (e.key === 'Enter' && numpadBuffer.length > 0) {
            const targetId = parseInt(numpadBuffer, 10);
            const targetItem = document.querySelector(`.camera-item[data-cam="cam-${targetId}"]`);
            
            if (targetItem && mainMonitorImg && mainMonitorTitle) {
                mainMonitorImg.src = targetItem.getAttribute('data-img');
                mainMonitorTitle.textContent = targetItem.getAttribute('data-title');
                
                if (mainMonitor) {
                    mainMonitor.animate([
                        { boxShadow: '0 0 0 0 rgba(136,192,208,0.7)' },
                        { boxShadow: '0 0 0 20px rgba(136,192,208,0)' }
                    ], { duration: 500, easing: 'ease-out' });
                }
            } else {
                // Invalid camera flash red
                if (numpadHud) {
                    numpadHud.style.borderColor = 'var(--danger)';
                    numpadHud.style.color = 'var(--danger)';
                    setTimeout(() => {
                        numpadHud.style.borderColor = 'var(--accent)';
                        numpadHud.style.color = 'var(--accent)';
                    }, 500);
                }
            }
            
            numpadBuffer = '';
            setTimeout(() => { if(numpadHud) numpadHud.style.opacity = '0'; }, 500);
        } else if (e.key === 'Escape' || e.key === 'Backspace') {
            numpadBuffer = '';
            if (numpadHud) numpadHud.style.opacity = '0';
        }
    });

    // Epic 22: AI-Assisted Provisioning
    const btnAiName = document.getElementById('btn-ai-name');
    if (btnAiName) {
        btnAiName.addEventListener('click', async () => {
            const notes = document.getElementById('provision-notes').value;
            const rows = document.querySelectorAll('#provision-tbody tr');
            const rawNames = Array.from(rows).map(row => row.querySelector('td').innerText);
            
            btnAiName.classList.add('loading');
            btnAiName.innerHTML = 'Analyzing... <i class="ph ph-spinner ph-spin"></i>';

            const prompt = `You are a VMS naming assistant.
I have these raw cameras discovered on the network: ${rawNames.join(', ')}.
The technician noted: "${notes}".
Return a JSON array of exactly ${rawNames.length} strings representing the new, standardized, aesthetic camera names (e.g. CAM-101-LOBBY).
Only return the JSON array, no other text.`;

            let assignedNames = [];
            
            try {
                const response = await fetch('/api/safetask/ai-advisor', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await response.json();
                
                // Try to parse the response text as JSON
                try {
                    // LLM might wrap in ```json ... ```
                    let cleanText = data.response.replace(/```json/g, '').replace(/```/g, '').trim();
                    assignedNames = JSON.parse(cleanText);
                } catch (e) {
                    console.warn("Failed to parse LLM JSON, falling back.", e);
                    throw new Error("JSON Parse failed"); // Trigger fallback
                }

                if (!Array.isArray(assignedNames) || assignedNames.length !== rawNames.length) {
                    throw new Error("Invalid array length"); // Trigger fallback
                }

            } catch (err) {
                console.warn("Using simulation fallback for AI Naming.", err);
                // Fallback simulation if LM Studio is offline or returned bad format
                await new Promise(r => setTimeout(r, 1500));
                assignedNames = [
                    "CAM-101-LOBBY-MAIN",
                    "CAM-102-LOBBY-EAST",
                    "CAM-103-LOBBY-WEST",
                    "CAM-201-FENCE-NORTH",
                    "CAM-202-FENCE-SOUTH"
                ];
            }

            // Apply the names to the UI
            const nameCells = document.querySelectorAll('.assigned-name');
            nameCells.forEach((cell, index) => {
                if (assignedNames[index]) {
                    cell.textContent = assignedNames[index];
                    cell.style.color = 'var(--success)';
                    cell.style.fontWeight = 'bold';
                    
                    // Flash effect
                    cell.parentElement.style.backgroundColor = 'rgba(163, 190, 140, 0.2)';
                    setTimeout(() => {
                        cell.parentElement.style.backgroundColor = '';
                    }, 800);
                }
            });

            btnAiName.classList.remove('loading');
            btnAiName.innerHTML = 'AI Auto-Name <i class="ph ph-check-circle"></i>';
            btnAiName.style.backgroundColor = 'var(--success)';
            btnAiName.style.color = 'var(--bg-dark)';
        });
    }

    // Tab Switching
    const tabs = document.querySelectorAll('.nav-links li[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-tab') + '-tab';
            document.getElementById(targetId).classList.add('active');
            
            // Epic 16: Fetch data when opening dispatch tab
            if (tab.getAttribute('data-tab') === 'dispatch') {
                fetchDispatchTasks();
                fetchLostItems();
            }
            // Epic 7: Fetch data when opening evidence tab
            if (tab.getAttribute('data-tab') === 'evidence') {
                fetchEvidenceLog();
            }
            // Epic 11: Fetch data when opening evac tab
            if (tab.getAttribute('data-tab') === 'evac') {
                fetchEvacuationRoster();
            }
            
            // Epic 19: Vision Analytics Tab
            if (tab.getAttribute('data-tab') === 'analytics') {
                startVisionAnalytics();
            } else {
                stopVisionAnalytics();
            }
        });
    });

    // Form Submission
    const form = document.getElementById('incident-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            title: document.getElementById('inc-title').value,
            location: document.getElementById('inc-location').value,
            equipment_involved: document.getElementById('inc-equipment').value,
            reporter: document.getElementById('inc-reporter').value,
            description: document.getElementById('inc-desc').value
        };

        const btn = form.querySelector('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Processing...';
        btn.disabled = true;

        try {
            const response = await fetch('/api/safetask/incident', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const data = await response.json();
                displayReviewPacket(data.packet);
                // Switch to Review Tab
                document.querySelector('.nav-links li[data-tab="review"]').click();
                form.reset();
            } else {
                alert('Error submitting incident.');
            }
        } catch (err) {
            console.error(err);
            alert('Failed to connect to the server.');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });

    function displayReviewPacket(packet) {
        document.getElementById('no-incident-msg').classList.add('hidden');
        document.getElementById('review-packet').classList.remove('hidden');

        document.getElementById('packet-id').textContent = packet.incident_id;
        document.getElementById('packet-status').textContent = packet.status;
        document.getElementById('packet-location').textContent = packet.details.location;
        document.getElementById('packet-desc').textContent = packet.details.description;
        document.getElementById('packet-escalation').textContent = packet.escalation_prompt;

        const policyList = document.getElementById('policy-list');
        policyList.innerHTML = ''; // clear

        if (packet.recommended_review && packet.recommended_review.length > 0) {
            function escapeHTML(str) {
                if (!str) return '';
                return str.toString()
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }
            packet.recommended_review.forEach(pol => {
                const card = document.createElement('div');
                card.className = 'glass-panel policy-card require_review';
                card.style.marginBottom = '1rem';
                card.innerHTML = `
                    <h4><i class="ph ph-file-text"></i> ${escapeHTML(pol.title)}</h4>
                    <p class="meta" style="font-size: 0.85rem; color: var(--accent); margin-bottom: 0.5rem;">Source: ${escapeHTML(pol.source)} | Page: ${escapeHTML(pol.page)}</p>
                    <p style="color: var(--text-main); line-height: 1.5; font-size: 0.95rem;">"${escapeHTML(pol.excerpt)}"</p>
                    <div style="margin-top: 1rem;">
                        <button class="btn secondary-btn" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" onclick="alert('Opening PDF viewer to page ${escapeHTML(pol.page)}')"><i class="ph ph-arrow-square-out"></i> Open Document</button>
                    </div>
                `;
                policyList.appendChild(card);
            });
        } else {
            policyList.innerHTML = '<p>No specific policies found for this incident type.</p>';
        }
    }

    // Epic 16: Dispatch Console Logic
    function escapeHTML(str) {
        if (!str) return '';
        return str.toString()
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    async function fetchDispatchTasks() {
        try {
            const res = await fetch('/api/safetask/dispatch');
            if (res.ok) {
                const data = await res.json();
                const list = document.getElementById('dispatch-list');
                list.innerHTML = '';
                data.tasks.forEach(task => {
                    const card = document.createElement('div');
                    card.className = `glass-panel policy-card ${task.status === 'completed' ? 'status-completed' : ''}`;
                    card.style.padding = '1rem';
                    card.style.borderLeft = task.status === 'completed' ? '4px solid var(--success, #4caf50)' : '4px solid var(--warning, #ff9800)';
                    
                    card.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin:0;">${escapeHTML(task.title)}</h4>
                                <p style="margin: 0.2rem 0; font-size: 0.85rem; color: var(--text-muted);">
                                    <i class="ph ph-user"></i> ${escapeHTML(task.officer)} &bull; ${new Date(task.timestamp).toLocaleTimeString()}
                                </p>
                            </div>
                            ${task.status !== 'completed' ? `<button class="btn secondary-btn" onclick="completeTask('${escapeHTML(task.id)}')"><i class="ph ph-check"></i></button>` : `<span class="badge" style="background:var(--success, #4caf50)">Done</span>`}
                        </div>
                    `;
                    list.appendChild(card);
                });
            }
        } catch (e) {
            console.error("Failed to fetch tasks", e);
        }
    }

    window.completeTask = async function(taskId) {
        try {
            const res = await fetch(`/api/safetask/dispatch/${taskId}/complete`, { method: 'PATCH' });
            if (res.ok) fetchDispatchTasks();
        } catch(e) {
            console.error(e);
        }
    };

    const dispatchForm = document.getElementById('dispatch-form');
    if (dispatchForm) {
        dispatchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                title: document.getElementById('dispatch-title').value,
                officer: document.getElementById('dispatch-officer').value
            };
            try {
                const res = await fetch('/api/safetask/dispatch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    dispatchForm.reset();
                    fetchDispatchTasks();
                }
            } catch (err) { console.error(err); }
        });
    }

    async function fetchLostItems() {
        try {
            const res = await fetch('/api/safetask/lostandfound');
            if (res.ok) {
                const data = await res.json();
                const list = document.getElementById('lnf-list');
                list.innerHTML = '';
                data.items.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'glass-panel policy-card';
                    card.style.padding = '1rem';
                    card.innerHTML = `
                        <h4 style="margin:0;">${escapeHTML(item.description)}</h4>
                        <p style="margin: 0.2rem 0; font-size: 0.85rem; color: var(--text-muted);">
                            <i class="ph ph-map-pin"></i> ${escapeHTML(item.location_found)} &bull; ${new Date(item.timestamp).toLocaleDateString()}
                        </p>
                    `;
                    list.appendChild(card);
                });
            }
        } catch (e) {
            console.error("Failed to fetch lost items", e);
        }
    }

    const lnfForm = document.getElementById('lnf-form');
    if (lnfForm) {
        lnfForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                description: document.getElementById('lnf-desc').value,
                location_found: document.getElementById('lnf-location').value
            };
            try {
                const res = await fetch('/api/safetask/lostandfound', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    lnfForm.reset();
                    fetchLostItems();
                }
            } catch (err) { console.error(err); }
        });
    }

    // Epic 7: Evidence Registry Logic
    async function fetchEvidenceLog() {
        try {
            const res = await fetch('/api/safetask/evidence');
            if (res.ok) {
                const data = await res.json();
                const tbody = document.getElementById('evidence-list');
                tbody.innerHTML = '';
                data.evidence.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
                    tr.innerHTML = `
                        <td style="padding: 0.8rem; white-space: nowrap;">${new Date(item.timestamp).toLocaleString()}</td>
                        <td style="padding: 0.8rem;">${escapeHTML(item.incident_id)}</td>
                        <td style="padding: 0.8rem; word-break: break-all;">${escapeHTML(item.filename)}</td>
                        <td style="padding: 0.8rem; font-family: monospace; font-size: 0.8rem; color: var(--accent); word-break: break-all;">${escapeHTML(item.file_hash)}</td>
                        <td style="padding: 0.8rem;">${escapeHTML(item.uploaded_by)}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } catch (e) {
            console.error("Failed to fetch evidence log", e);
        }
    }

    const evidenceForm = document.getElementById('evidence-form');
    if (evidenceForm) {
        evidenceForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById('evd-file');
            if (!fileInput.files.length) {
                alert("Please select a file to upload.");
                return;
            }

            const formData = new FormData();
            formData.append('incident_id', document.getElementById('evd-incident').value);
            formData.append('officer', document.getElementById('evd-officer').value);
            formData.append('file', fileInput.files[0]);

            const btn = evidenceForm.querySelector('button');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Sealing...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/safetask/evidence/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (res.ok) {
                    evidenceForm.reset();
                    fetchEvidenceLog();
                } else {
                    alert('Error uploading evidence. Make sure the backend supports python-multipart.');
                }
            } catch (err) {
                console.error(err);
                alert('Failed to connect to the server.');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }

    // Epic 3: PiP Review Deck Logic
    const spawnPipBtn = document.getElementById('spawn-pip-btn');
    const pipContainer = document.getElementById('pip-container');
    let pipCounter = 1;
    let maxZIndex = 100;

    if (spawnPipBtn && pipContainer) {
        spawnPipBtn.addEventListener('click', () => {
            spawnPiPPane(`CAM-${String(pipCounter).padStart(2, '0')} REVIEW`);
            pipCounter++;
        });
    }

    function spawnPiPPane(cameraId) {
        const pane = document.createElement('div');
        pane.className = 'pip-window';
        pane.style.left = `${50 + (pipCounter * 30)}px`;
        pane.style.top = `${100 + (pipCounter * 30)}px`;
        maxZIndex++;
        pane.style.zIndex = maxZIndex;

        pane.innerHTML = `
            <div class="pip-header">
                <span class="pip-header-title"><i class="ph ph-video-camera"></i> ${cameraId}</span>
                <button class="pip-close"><i class="ph ph-x"></i></button>
            </div>
            <div class="pip-content">
                <i class="ph ph-play-circle" style="font-size: 3rem; color: rgba(255,255,255,0.2);"></i>
                <div class="pip-overlay">
                    -00:15:30
                </div>
                <div class="pip-controls">
                    <i class="ph ph-rewind-circle"></i>
                    <i class="ph ph-pause-circle"></i>
                    <i class="ph ph-fast-forward-circle"></i>
                    <i class="ph ph-corners-out"></i>
                </div>
            </div>
        `;

        pipContainer.appendChild(pane);

        // Close logic
        const closeBtn = pane.querySelector('.pip-close');
        closeBtn.addEventListener('click', () => {
            pane.remove();
        });

        // Bring to front
        pane.addEventListener('mousedown', () => {
            document.querySelectorAll('.pip-window').forEach(p => p.classList.remove('active'));
            pane.classList.add('active');
            maxZIndex++;
            pane.style.zIndex = maxZIndex;
        });

        // Dragging logic
        const header = pane.querySelector('.pip-header');
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = parseInt(window.getComputedStyle(pane).left, 10) || 0;
            initialTop = parseInt(window.getComputedStyle(pane).top, 10) || 0;
            e.preventDefault(); // Prevent text selection
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            pane.style.left = `${initialLeft + dx}px`;
            pane.style.top = `${initialTop + dy}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        // Auto-activate the new pane
        document.querySelectorAll('.pip-window').forEach(p => p.classList.remove('active'));
        pane.classList.add('active');
    }

    // Epic 3: Live Clock Update
    const liveClock = document.getElementById('live-clock');
    if (liveClock) {
        setInterval(() => {
            const now = new Date();
            liveClock.textContent = now.toISOString().replace('T', ' ').substring(0, 19);
        }, 1000);
    }

    // Epic 11: Evacuation Accountability Board Logic
    async function fetchEvacuationRoster() {
        try {
            const res = await fetch('/api/safetask/evacuation/roster');
            if (res.ok) {
                const data = await res.json();
                const tbody = document.getElementById('evac-list');
                tbody.innerHTML = '';
                
                let counts = { total: 0, Safe: 0, Missing: 0, Injured: 0, Unknown: 0 };
                
                data.roster.forEach(person => {
                    counts.total++;
                    if (counts[person.status] !== undefined) counts[person.status]++;
                    
                    const tr = document.createElement('tr');
                    tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
                    
                    let statusBadge = `<span class="badge" style="background: rgba(255,255,255,0.2)">${escapeHTML(person.status)}</span>`;
                    if (person.status === 'Safe') statusBadge = `<span class="badge" style="background: var(--success)">Safe</span>`;
                    if (person.status === 'Missing') statusBadge = `<span class="badge" style="background: var(--danger)">Missing</span>`;
                    if (person.status === 'Injured') statusBadge = `<span class="badge" style="background: var(--warning)">Injured</span>`;
                    
                    tr.innerHTML = `
                        <td style="padding: 0.8rem; font-weight: bold;">${escapeHTML(person.name)}</td>
                        <td style="padding: 0.8rem; color: var(--text-muted);">${escapeHTML(person.department)}</td>
                        <td style="padding: 0.8rem;">${statusBadge}</td>
                        <td style="padding: 0.8rem; text-align: right; display: flex; gap: 0.5rem; justify-content: flex-end;">
                            <button class="btn secondary-btn" style="padding: 0.3rem 0.6rem; color: var(--success); border-color: var(--success);" onclick="updateEvacStatus('${escapeHTML(person.id)}', 'Safe')"><i class="ph ph-check"></i> Safe</button>
                            <button class="btn secondary-btn" style="padding: 0.3rem 0.6rem; color: var(--danger); border-color: var(--danger);" onclick="updateEvacStatus('${escapeHTML(person.id)}', 'Missing')"><i class="ph ph-warning"></i> Missing</button>
                            <button class="btn secondary-btn" style="padding: 0.3rem 0.6rem; color: var(--warning); border-color: var(--warning);" onclick="updateEvacStatus('${escapeHTML(person.id)}', 'Injured')"><i class="ph ph-bandaids"></i> Injured</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
                
                // Update tallies
                document.getElementById('evac-count-total').textContent = counts.total;
                document.getElementById('evac-count-safe').textContent = counts.Safe;
                document.getElementById('evac-count-missing').textContent = counts.Missing;
                document.getElementById('evac-count-injured').textContent = counts.Injured;
            }
        } catch (e) {
            console.error("Failed to fetch evacuation roster", e);
        }
    }

    window.updateEvacStatus = async function(personId, status) {
        try {
            const res = await fetch(`/api/safetask/evacuation/roster/${personId}/status`, {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ status })
            });
            if (res.ok) {
                fetchEvacuationRoster(); // Refresh the board
            }
        } catch (e) {
            console.error(e);
        }
    };

    const seedBtn = document.getElementById('seed-roster-btn');
    if (seedBtn) {
        seedBtn.addEventListener('click', async () => {
            if (!confirm("This will clear the current roster and generate dummy data. Proceed?")) return;
            try {
                const res = await fetch('/api/safetask/evacuation/seed', { method: 'POST' });
                if (res.ok) fetchEvacuationRoster();
            } catch (e) {
                console.error(e);
            }
        });
    }

    // Epic 4: Constellation Map Logic
    const constellationCanvas = document.getElementById('constellation-canvas');
    const svgLines = document.getElementById('constellation-lines');
    const addNodeBtn = document.getElementById('add-node-btn');
    const nodeNameInput = document.getElementById('node-name-input');
    const toggleLinkBtn = document.getElementById('toggle-link-btn');
    
    let isLinkMode = false;
    let selectedNodeForLink = null;
    let nodeCounter = 1;
    let links = []; // Array of { node1, node2, lineElement }

    if (toggleLinkBtn) {
        toggleLinkBtn.addEventListener('click', () => {
            isLinkMode = !isLinkMode;
            toggleLinkBtn.innerHTML = isLinkMode ? '<i class="ph ph-link-break"></i> Link Mode: ON' : '<i class="ph ph-link"></i> Link Mode: OFF';
            toggleLinkBtn.className = isLinkMode ? 'btn primary-btn' : 'btn secondary-btn';
            if (!isLinkMode && selectedNodeForLink) {
                selectedNodeForLink.classList.remove('active-link');
                selectedNodeForLink = null;
            }
        });
    }

    if (addNodeBtn && constellationCanvas) {
        addNodeBtn.addEventListener('click', () => {
            const name = nodeNameInput.value.trim() || `CAM-${String(nodeCounter).padStart(2, '0')}`;
            spawnConstellationNode(name);
            nodeNameInput.value = '';
            nodeCounter++;
        });
    }

    function spawnConstellationNode(name) {
        const node = document.createElement('div');
        node.className = 'graph-node';
        // Spawn near center
        node.style.left = `calc(50% + ${Math.random() * 50 - 25}px)`;
        node.style.top = `calc(50% + ${Math.random() * 50 - 25}px)`;
        node.innerHTML = `
            <i class="ph ph-camera"></i>
            <div class="graph-node-label">${escapeHTML(name)}</div>
        `;

        // Double-click to spawn PiP (Best Practice Integration)
        node.addEventListener('dblclick', () => {
            if (typeof spawnPiPPane === 'function') {
                // Switch to live tab to see it if not there, or just spawn it globally
                spawnPiPPane(name);
                // Also trigger click on Live tab to ensure visibility
                document.querySelector('.nav-links li[data-tab="live"]').click();
            }
        });

        // Link Mode Logic & Dragging Logic
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        node.addEventListener('mousedown', (e) => {
            if (isLinkMode) {
                // Linking logic
                if (!selectedNodeForLink) {
                    selectedNodeForLink = node;
                    node.classList.add('active-link');
                } else {
                    if (selectedNodeForLink !== node) {
                        createLink(selectedNodeForLink, node);
                    }
                    selectedNodeForLink.classList.remove('active-link');
                    selectedNodeForLink = null;
                }
                return; // Prevent dragging when linking
            }

            // Drag logic
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = parseInt(window.getComputedStyle(node).left, 10) || 0;
            initialTop = parseInt(window.getComputedStyle(node).top, 10) || 0;
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            node.style.left = `${initialLeft + dx}px`;
            node.style.top = `${initialTop + dy}px`;
            updateLines();
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        constellationCanvas.appendChild(node);
    }

    function createLink(node1, node2) {
        // Prevent duplicate links
        if (links.some(l => (l.node1 === node1 && l.node2 === node2) || (l.node1 === node2 && l.node2 === node1))) {
            return;
        }

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('class', 'constellation-line');
        line.setAttribute('marker-end', 'url(#arrowhead)');
        svgLines.appendChild(line);

        links.push({ node1, node2, lineElement: line });
        updateLines();
    }

    function updateLines() {
        if (!constellationCanvas || !svgLines) return;
        
        const canvasRect = constellationCanvas.getBoundingClientRect();

        links.forEach(link => {
            const rect1 = link.node1.getBoundingClientRect();
            const rect2 = link.node2.getBoundingClientRect();

            // Calculate center of node relative to canvas
            const x1 = rect1.left + (rect1.width / 2) - canvasRect.left;
            const y1 = rect1.top + (rect1.height / 2) - canvasRect.top;
            const x2 = rect2.left + (rect2.width / 2) - canvasRect.left;
            const y2 = rect2.top + (rect2.height / 2) - canvasRect.top;

            link.lineElement.setAttribute('x1', x1);
            link.lineElement.setAttribute('y1', y1);
            
            // Adjust end point slightly so the arrowhead doesn't hide under the node
            const angle = Math.atan2(y2 - y1, x2 - x1);
            const radius = 30; // node radius (60px width / 2)
            const adjustedX2 = x2 - (Math.cos(angle) * (radius + 5)); // +5 for marker width
            const adjustedY2 = y2 - (Math.sin(angle) * (radius + 5));

            link.lineElement.setAttribute('x2', adjustedX2);
            link.lineElement.setAttribute('y2', adjustedY2);
        });
    }

    // Handle window resize
    window.addEventListener('resize', updateLines);

    // Epic 5: Voice Dictation UI Placeholder Logic
    const dictateBtn = document.getElementById('dictate-btn');
    const dictateStatus = document.getElementById('dictation-status');
    const incDesc = document.getElementById('inc-desc');
    let isDictating = false;

    if (dictateBtn && dictateStatus && incDesc) {
        dictateBtn.addEventListener('click', () => {
            if (isDictating) return; // Prevent double clicks
            
            isDictating = true;
            dictateBtn.classList.add('pulse-record');
            dictateStatus.style.display = 'block';

            // Simulate 3 seconds of listening, then populate text
            setTimeout(() => {
                const simulatedTranscription = "Subject observed fleeing via the North Stairwell. Wearing a red jacket. Requesting backup immediately.";
                
                // Append text if already typing, otherwise just set it
                if (incDesc.value.trim() !== '') {
                    incDesc.value += " " + simulatedTranscription;
                } else {
                    incDesc.value = simulatedTranscription;
                }

                dictateBtn.classList.remove('pulse-record');
                dictateStatus.style.display = 'none';
                isDictating = false;
            }, 3000);
        });
    }

    // Epic 17: Training Academy (LM Studio Integration)
    const trainingInput = document.getElementById('training-user-input');
    const trainingSendBtn = document.getElementById('training-send-btn');
    const trainingHistory = document.getElementById('training-chat-history');
    const trainingTypingIndicator = document.getElementById('training-typing-indicator');

    let chatMessages = []; // Track history for context

    if (trainingInput && trainingSendBtn && trainingHistory) {
        
        const appendMessage = (role, content) => {
            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-message ${role === 'user' ? 'user' : 'ai'}`;
            msgDiv.innerHTML = `
                <div class="avatar"><i class="ph ${role === 'user' ? 'ph-user' : 'ph-robot'}"></i></div>
                <div class="bubble">${escapeHTML(content).replace(/\n/g, '<br>')}</div>
            `;
            trainingHistory.appendChild(msgDiv);
            trainingHistory.scrollTop = trainingHistory.scrollHeight;
        };

        const sendMessageToAdvisor = async () => {
            const content = trainingInput.value.trim();
            if (!content) return;

            // 1. Show user message
            appendMessage('user', content);
            chatMessages.push({ role: 'user', content: content });
            trainingInput.value = '';
            
            // 2. Show typing indicator
            trainingTypingIndicator.style.display = 'block';
            trainingInput.disabled = true;
            trainingSendBtn.disabled = true;

            try {
                // 3. Send to backend
                const res = await fetch('/api/safetask/training/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ messages: chatMessages })
                });

                const data = await res.json();
                
                if (data.status === 'success') {
                    appendMessage('assistant', data.response);
                    chatMessages.push({ role: 'assistant', content: data.response });
                } else {
                    appendMessage('assistant', data.response || "I'm having trouble connecting to my local language model.");
                }

            } catch (e) {
                console.error(e);
                appendMessage('assistant', "[SYSTEM ERROR] Cannot reach SafeTask backend API.");
            } finally {
                trainingTypingIndicator.style.display = 'none';
                trainingInput.disabled = false;
                trainingSendBtn.disabled = false;
                trainingInput.focus();
            }
        };

        trainingSendBtn.addEventListener('click', sendMessageToAdvisor);
        trainingInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessageToAdvisor();
        });
    }

    // Epic 18: Authentication & RBAC
    const loginScreen = document.getElementById('login-screen');
    const mainAppContainer = document.getElementById('main-app-container');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const logoutBtn = document.getElementById('logout-btn');

    // Tab Elements for RBAC hiding
    const tabNavReview = document.querySelector('li[data-tab="review"]');
    const tabNavEvidence = document.querySelector('li[data-tab="evidence"]');
    const tabNavDispatch = document.querySelector('li[data-tab="dispatch"]');
    const tabNavTraining = document.querySelector('li[data-tab="training"]');
    const tabNavAnalytics = document.querySelector('li[data-tab="analytics"]');
    const tabNavProvision = document.querySelector('li[data-tab="provision"]'); // Epic 22

    const applyRBAC = (role) => {
        // Reset all tabs to visible
        document.querySelectorAll('.nav-links li[data-tab]').forEach(el => el.style.display = 'flex');

        if (role === 'GUARD') {
            // Guards only see Live Surveillance, Constellation, Intake, Evac, and Training
            if(tabNavReview) tabNavReview.style.display = 'none';
            if(tabNavEvidence) tabNavEvidence.style.display = 'none';
            if(tabNavDispatch) tabNavDispatch.style.display = 'none';
            if(tabNavAnalytics) tabNavAnalytics.style.display = 'none';
            if(tabNavProvision) tabNavProvision.style.display = 'none';
        } else if (role === 'OPERATOR') {
            // Operators see everything except Evidence Locker and Provisioning
            if(tabNavEvidence) tabNavEvidence.style.display = 'none';
            if(tabNavProvision) tabNavProvision.style.display = 'none';
        }
        // Admin sees everything
    };

    const handleLoginSuccess = (role) => {
        loginScreen.style.display = 'none';
        mainAppContainer.style.display = 'flex';
        applyRBAC(role);
        
        // Initial fetch of active data once logged in
        fetchDispatchTasks();
        fetchEvidenceLog();
        fetchEvacuationRoster();
        
        // Ensure first visible tab is active
        const firstVisibleTab = document.querySelector('.nav-links li[data-tab][style*="display: flex"], .nav-links li[data-tab]:not([style*="none"])');
        if (firstVisibleTab) firstVisibleTab.click();
    };

    // Check if already logged in via sessionStorage
    const storedRole = sessionStorage.getItem('safetask_role');
    if (storedRole) {
        handleLoginSuccess(storedRole);
    } else {
        loginScreen.style.display = 'flex';
        mainAppContainer.style.display = 'none';
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value.trim();

            try {
                const res = await fetch('/api/safetask/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                
                if (data.status === 'success') {
                    sessionStorage.setItem('safetask_role', data.role);
                    sessionStorage.setItem('safetask_token', data.token);
                    loginError.style.display = 'none';
                    handleLoginSuccess(data.role);
                } else {
                    loginError.textContent = data.message;
                    loginError.style.display = 'block';
                }
            } catch (err) {
                loginError.textContent = "Cannot reach server.";
                loginError.style.display = 'block';
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            sessionStorage.removeItem('safetask_role');
            sessionStorage.removeItem('safetask_token');
            loginScreen.style.display = 'flex';
            mainAppContainer.style.display = 'none';
        });
    // Epic 19: Vision Analytics Simulation
    const cvOverlay = document.getElementById('cv-overlay');
    const cvEventLog = document.getElementById('cv-event-log');
    let visionInterval = null;
    let knownEvents = new Set(); // To prevent duplicate log entries

    function startVisionAnalytics() {
        if (!visionInterval) {
            // Fetch immediately, then every 2 seconds
            fetchVisionEvents();
            visionInterval = setInterval(fetchVisionEvents, 2000);
        }
    }

    function stopVisionAnalytics() {
        if (visionInterval) {
            clearInterval(visionInterval);
            visionInterval = null;
        }
    }

    async function fetchVisionEvents() {
        try {
            const res = await fetch('/api/safetask/vision/events');
            if (res.ok) {
                const data = await res.json();
                renderBoundingBoxes(data.tracked_objects);
                renderNewEvents(data.events);
            }
        } catch (e) {
            console.error("Failed to fetch vision analytics", e);
        }
    }

    function renderBoundingBoxes(objects) {
        if (!cvOverlay) return;
        cvOverlay.innerHTML = ''; // Clear previous frame
        
        objects.forEach(obj => {
            const box = document.createElement('div');
            box.className = `cv-bounding-box ${obj.status}`;
            // Convert percentage coordinates to CSS
            box.style.left = `${obj.x}%`;
            box.style.top = `${obj.y}%`;
            box.style.width = `${obj.width}%`;
            box.style.height = `${obj.height}%`;
            
            box.innerHTML = `<div class="cv-label">${escapeHTML(obj.id.toUpperCase())}</div>`;
            cvOverlay.appendChild(box);
        });
    }

    function renderNewEvents(events) {
        if (!cvEventLog) return;
        
        events.forEach(evt => {
            const eventKey = `${evt.timestamp}-${evt.type}`;
            if (!knownEvents.has(eventKey)) {
                knownEvents.add(eventKey);
                
                // Remove the "Awaiting detections..." placeholder if it exists
                const placeholder = cvEventLog.querySelector('div[style*="Awaiting"]');
                if (placeholder) placeholder.remove();

                const card = document.createElement('div');
                card.className = 'cv-event-card';
                card.style.borderColor = evt.color;
                
                const timeStr = new Date(evt.timestamp).toLocaleTimeString();
                
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <strong style="color: ${evt.color}">${escapeHTML(evt.type)}</strong>
                        <span style="color: var(--text-muted); font-size: 0.75rem;">${timeStr}</span>
                    </div>
                    <div style="color: var(--text-main); margin-bottom: 0.3rem;">${escapeHTML(evt.description)}</div>
                    <div style="font-family: monospace; font-size: 0.75rem; color: var(--text-muted);">
                        <i class="ph ph-target"></i> Confidence: ${(evt.confidence * 100).toFixed(0)}%
                    </div>
                `;
                
                // Prepend to top of log
                cvEventLog.insertBefore(card, cvEventLog.firstChild);
                
                // Keep log from growing infinitely
                if (cvEventLog.children.length > 20) {
                    cvEventLog.lastChild.remove();
                }
            }
        });
    }

});
