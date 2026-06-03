document.addEventListener("DOMContentLoaded", () => {
    // Tab switching logic
    const tabs = document.querySelectorAll(".nav-links li");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));
            
            tab.classList.add("active");
            document.getElementById(`${tab.dataset.tab}-tab`).classList.add("active");
            
            // Reload data if needed
            if(tab.dataset.tab === "notebook") loadNotes();
            if(tab.dataset.tab === "maps") loadMaps();
        });
    });

    // Initial load
    loadWeather();
    loadNotes();
    loadPolicies();
    loadTelemetry();

    // Sync Handler
    const syncBtn = document.getElementById("sync-data-btn");
    if(syncBtn) {
        syncBtn.addEventListener("click", async () => {
            const originalText = syncBtn.innerHTML;
            syncBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Syncing...`;
            syncBtn.disabled = true;
            try {
                const res = await fetch("/api/sync/clearlake", { method: "POST" });
                const data = await res.json();
                if(res.ok) {
                    alert("Sync complete. Loading new data...");
                    loadTelemetry();
                } else {
                    alert("Sync failed: " + data.detail);
                }
            } catch (e) {
                alert("Network error during sync.");
            } finally {
                syncBtn.innerHTML = originalText;
                syncBtn.disabled = false;
            }
        });
    }

    // Dictation Handler
    const dictateBtn = document.getElementById("dictate-btn");
    const dictationInput = document.getElementById("dictation-input");
    const resultBox = document.getElementById("dictation-result");

    dictateBtn.addEventListener("click", async () => {
        const text = dictationInput.value.trim();
        if(text.length < 5) {
            alert("Dictation must be at least 5 characters long.");
            return;
        }

        dictateBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Processing...`;
        dictateBtn.disabled = true;
        resultBox.classList.add("hidden");

        try {
            const res = await fetch("/api/dictate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            
            resultBox.classList.remove("hidden", "block", "warn", "allow");
            
            if (data.status === "blocked") {
                resultBox.classList.add("block");
                resultBox.innerHTML = `
                    <h3><i class="ph ph-shield-warning"></i> HARNESS BLOCKED</h3>
                    <p>Triggered: ${data.packet.decision_state}</p>
                    <pre style="font-size: 0.8rem; margin-top: 10px; color: var(--text-muted);">${JSON.stringify(data.packet.triggered_rules, null, 2)}</pre>
                `;
            } else {
                if (data.packet.decision_state === "warn") {
                    resultBox.classList.add("warn");
                    resultBox.innerHTML = `<h3><i class="ph ph-warning"></i> WARNING (Saved)</h3><p>Note saved, but triggered warnings.</p>`;
                } else {
                    resultBox.classList.add("allow");
                    resultBox.innerHTML = `<h3><i class="ph ph-check-circle"></i> Note Saved</h3>`;
                }
                dictationInput.value = "";
                loadNotes();
            }
        } catch (e) {
            resultBox.classList.remove("hidden");
            resultBox.classList.add("block");
            resultBox.innerHTML = `<h3><i class="ph ph-warning"></i> Error</h3><p>Could not reach the backend. Check if the server is running.</p>`;
        } finally {
            dictateBtn.innerHTML = `<i class="ph ph-paper-plane-right"></i> Process Dictation`;
            dictateBtn.disabled = false;
        }
    });

    // Identify Handler
    const identifyBtn = document.getElementById("identify-btn");
    const specimenFile = document.getElementById("specimen-file");
    const identifyResult = document.getElementById("identify-result");

    identifyBtn.addEventListener("click", async () => {
        if (!specimenFile.files.length) {
            alert("Please select an image first.");
            return;
        }

        const formData = new FormData();
        formData.append("file", specimenFile.files[0]);

        identifyBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Analyzing...`;
        identifyBtn.disabled = true;
        identifyResult.classList.add("hidden");

        try {
            const res = await fetch("/api/identify", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            
            identifyResult.classList.remove("hidden", "block", "warn", "allow");
            identifyResult.classList.add("allow");
            
            let html = `<h3><i class="ph ph-check-circle"></i> Identification Complete</h3><ul style="margin-top:0.5rem; padding-left:1.5rem;">`;
            if (data.predictions && data.predictions.length > 0) {
                data.predictions.forEach(p => {
                    html += `<li><strong>${p.label}</strong> (${(p.score * 100).toFixed(1)}%)</li>`;
                });
            } else {
                html += `<li>No species identified.</li>`;
            }
            html += `</ul>`;
            identifyResult.innerHTML = html;
        } catch (e) {
            identifyResult.classList.remove("hidden");
            identifyResult.classList.add("block");
            identifyResult.innerHTML = `<h3><i class="ph ph-warning"></i> Error</h3><p>Could not reach the vision model.</p>`;
        } finally {
            identifyBtn.innerHTML = `<i class="ph ph-scan"></i> Identify`;
            identifyBtn.disabled = false;
        }
    });

    // Search Handler
    const searchBtn = document.getElementById("search-btn");
    const searchInput = document.getElementById("search-input");
    const searchResults = document.getElementById("search-results");
    const indexBtn = document.getElementById("index-btn");

    indexBtn.addEventListener("click", async () => {
        indexBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Indexing...`;
        indexBtn.disabled = true;
        try {
            const res = await fetch("/api/actions/index", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ arg: "" })
            });
            const data = await res.json();
            alert(data.message || "Indexing complete");
        } catch (e) {
            alert("Failed to run indexer.");
        } finally {
            indexBtn.innerHTML = `<i class="ph ph-arrows-clockwise"></i> Sync & Index Repo`;
            indexBtn.disabled = false;
        }
    });

    searchBtn.addEventListener("click", async () => {
        const query = searchInput.value.trim();
        if(!query) return;

        searchBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i>`;
        
        try {
            const res = await fetch("/api/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await res.json();
            
            searchResults.innerHTML = "";
            if(data.results.length === 0) {
                searchResults.innerHTML = "<p>No documents found.</p>";
                return;
            }

            data.results.forEach(card => {
                searchResults.innerHTML += `
                    <div class="result-card">
                        <h3>${card.metadata.title}</h3>
                        <div class="meta" style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">
                            Source: ${card.metadata.source} | Authority: ${card.metadata.authority_level}
                        </div>
                        <p>${card.content}</p>
                    </div>
                `;
            });
        } catch (e) {
            alert("Search failed.");
        } finally {
            searchBtn.innerHTML = `<i class="ph ph-magnifying-glass"></i> Search`;
        }
    });

    async function loadNotes() {
        const res = await fetch("/api/notes");
        const data = await res.json();
        const list = document.getElementById("notes-list");
        list.innerHTML = "";
        data.notes.forEach(note => {
            const date = new Date(note.timestamp).toLocaleString();
            list.innerHTML += `
                <div class="card">
                    <h3>Site: ${note.site_id}</h3>
                    <div class="meta">
                        <span><i class="ph ph-clock"></i> ${date}</span>
                    </div>
                    <p>${note.notes}</p>
                </div>
            `;
        });
    }

    async function loadMaps() {
        try {
            const res = await fetch("/api/maps");
            const data = await res.json();
            const list = document.getElementById("maps-list");
            list.innerHTML = "";
            
            let hasMaps = false;
            
            // Check for folium map specifically
            try {
                const foliumRes = await fetch("/exports/interactive_map.html", {method: 'HEAD'});
                if (foliumRes.ok) {
                    hasMaps = true;
                    list.innerHTML += `
                        <div class="card map-card" style="border: 2px solid var(--accent);">
                            <h3><i class="ph ph-globe"></i> Interactive Field Map</h3>
                            <p>An interactive, zoomable map of all field notes.</p>
                            <a href="/exports/interactive_map.html" target="_blank" class="btn primary-btn" style="display:inline-block; margin-top:10px; text-decoration:none;"><i class="ph ph-arrow-square-out"></i> Open Map in New Tab</a>
                        </div>
                    `;
                }
            } catch(e) {}
            
            if (data.maps.length > 0) {
                hasMaps = true;
                data.maps.forEach(map => {
                    const date = new Date(map.timestamp).toLocaleString();
                    list.innerHTML += `
                        <div class="card map-card">
                            ${map.image_url ? `<img src="${map.image_url}" alt="Map">` : ''}
                            <h3>Recipe: ${map.recipe_id}</h3>
                            <div class="meta">
                                <span><i class="ph ph-clock"></i> ${date}</span>
                            </div>
                            <p>Center: ${map.center_coordinates}</p>
                            <p style="margin-top:0.5rem; color: var(--success); font-size:0.8rem;">
                                <i class="ph ph-shield-check"></i> Harness: ${map.harness_decision.toUpperCase()}
                            </p>
                        </div>
                    `;
                });
            }
            
            if (!hasMaps) {
                list.innerHTML = "<p>No maps generated yet. Use the Quick Actions to generate a map.</p>";
            }
        } catch (e) {
            console.error("Failed to load maps");
        }
    }

    async function loadPolicies() {
        const res = await fetch("/api/policies");
        const data = await res.json();
        const list = document.getElementById("policies-list");
        list.innerHTML = "";
        
        data.policies.forEach(policy => {
            list.innerHTML += `
                <div class="policy-card ${policy.decision}">
                    <h4>${policy.id}</h4>
                    <p>${policy.description}</p>
                    <div style="margin-top:0.5rem; font-size:0.8rem; font-weight:600;" class="status-${policy.decision}">
                        Action: ${policy.decision.toUpperCase().replace("_", " ")}
                    </div>
                </div>
            `;
        });
    }

    async function loadWeather() {
        try {
            const res = await fetch("/api/weather");
            const data = await res.json();
            const widget = document.getElementById("weather-widget");
            
            let hazardsHtml = data.hazards.map(h => 
                `<span class="hazard-badge ${h.severity}"><i class="ph ph-warning"></i> ${h.type}: ${h.description}</span>`
            ).join('');

            widget.innerHTML = `
                <div class="weather-main" style="flex: 1; border-right: 1px solid var(--border); padding-right: 1rem;">
                    <h3 style="color: var(--accent); margin-bottom: 0.5rem;"><i class="ph ph-cloud-sun"></i> Cached Forecast: ${data.location}</h3>
                    <div style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; color: var(--text-main);">${data.current.temp}°F | <span style="font-size: 1.5rem; font-weight: 400;">${data.current.condition}</span></div>
                    <div style="color: var(--text-muted); font-size: 0.9rem;">Wind: ${data.current.wind} • Last synced: ${new Date(data.cached_time).toLocaleString()}</div>
                </div>
                <div class="weather-hazards" style="flex: 1; display: flex; flex-direction: column; gap: 0.75rem; justify-content: center; padding-left: 1rem;">
                    <div style="color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Active Field Hazards</div>
                    ${hazardsHtml || '<span class="hazard-badge low"><i class="ph ph-check-circle"></i> No active hazards</span>'}
                </div>
            `;
        } catch (e) {
            console.log("Weather cache unavailable.");
            document.getElementById("weather-widget").style.display = "none";
        }
    }

    // Chat Handler
    const chatBtn = document.getElementById("chat-send-btn");
    const chatInput = document.getElementById("chat-input");
    const chatHistory = document.getElementById("chat-history");
    let chatMessages = [
        {"role": "system", "content": "You are a helpful, concise AI assistant integrated into the FieldAware Cybernetic Ecology system. You assist field workers with their procedures and answer questions about the environment."}
    ];

    chatBtn.addEventListener("click", async () => {
        const text = chatInput.value.trim();
        if(!text) return;

        // Add user message
        chatHistory.innerHTML += `<div class="chat-msg user-msg">${text}</div>`;
        chatInput.value = "";
        chatHistory.scrollTop = chatHistory.scrollHeight;

        chatMessages.push({"role": "user", "content": text});
        chatBtn.innerHTML = `<i class="ph ph-spinner ph-spin"></i>`;
        
        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: chatMessages })
            });
            const data = await res.json();
            
            const reply = data.reply || "Sorry, I couldn't connect to the local model.";
            chatMessages.push({"role": "assistant", "content": reply});
            
            chatHistory.innerHTML += `<div class="chat-msg assistant-msg">${reply.replace(/\n/g, "<br>")}</div>`;
            chatHistory.scrollTop = chatHistory.scrollHeight;
        } catch (e) {
            chatHistory.innerHTML += `<div class="chat-msg assistant-msg" style="color: var(--danger)">Error connecting to LM Studio. Make sure it's running.</div>`;
        } finally {
            chatBtn.innerHTML = `<i class="ph ph-paper-plane-right"></i>`;
        }
    });

    chatInput.addEventListener("keypress", (e) => {
        if(e.key === "Enter") chatBtn.click();
    });

    // Quick Actions
    const actionAnalyze = document.getElementById("action-analyze");
    const actionExport = document.getElementById("action-export");
    const actionMap = document.getElementById("action-map");
    const actionFolium = document.getElementById("action-folium");
    const actionSpatial = document.getElementById("action-spatial");

    async function triggerAction(btn, endpoint, defaultHtml, payload = { arg: "" }) {
        btn.innerHTML = `<i class="ph ph-spinner ph-spin"></i> Running...`;
        btn.disabled = true;
        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.status === "blocked") {
                alert(`Action Blocked by Harness: ${data.packet.decision_state}`);
            } else {
                alert(data.message || "Action completed successfully");
                // Reload specific tabs based on action
                if (endpoint.includes("analyze")) loadNotes();
                if (endpoint.includes("map") || endpoint.includes("folium")) loadMaps();
            }
        } catch (e) {
            alert(`Action failed: ${e.message}`);
        } finally {
            btn.innerHTML = defaultHtml;
            btn.disabled = false;
        }
    }

    actionAnalyze.addEventListener("click", () => {
        triggerAction(actionAnalyze, "/api/actions/analyze", `<i class="ph ph-chart-line-up"></i> Run Analysis Sandbox`);
    });

    actionExport.addEventListener("click", () => {
        triggerAction(actionExport, "/api/actions/export", `<i class="ph ph-export"></i> Export Bundle`);
    });

    actionMap.addEventListener("click", () => {
        triggerAction(actionMap, "/api/actions/map", `<i class="ph ph-map-pin"></i> Generate Map (QGIS)`);
    });
    
    actionFolium.addEventListener("click", () => {
        triggerAction(actionFolium, "/api/actions/folium", `<i class="ph ph-globe"></i> Interactive Map (Folium)`);
    });

    actionSpatial.addEventListener("click", () => {
        const payload = {
            input_file: "data/clear-lake-watch-repo/data/lake-shoreline.json",
            output_file: "data/exports/lake-shoreline-standardized.geojson",
            tolerance: 0.001
        };
        triggerAction(actionSpatial, "/api/actions/preprocess-spatial", `<i class="ph ph-polygon"></i> Preprocess Spatial Data`, payload);
    });

    let lakeChartInstance = null;
    let dischargeChartInstance = null;

    async function loadTelemetry() {
        const errBox = document.getElementById("telemetry-error");
        try {
            const res = await fetch("/api/sensors/clearlake");
            if (!res.ok) {
                const data = await res.json();
                errBox.classList.remove("hidden");
                errBox.innerText = data.detail || "No telemetry data. Run pre-departure sync.";
                return;
            }
            errBox.classList.add("hidden");
            const data = await res.json();
            
            if (data.hydrologySeries) {
                const lakeData = data.hydrologySeries.find(s => s.label === "Lake level");
                const dischargeData = data.hydrologySeries.find(s => s.label === "Cole Creek discharge");

                if (lakeData && document.getElementById("lakeLevelChart")) {
                    const ctx = document.getElementById("lakeLevelChart").getContext("2d");
                    if (lakeChartInstance) lakeChartInstance.destroy();
                    lakeChartInstance = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: lakeData.points.map(p => p.date),
                            datasets: [{
                                label: 'Lake Level (ft)',
                                data: lakeData.points.map(p => p.value),
                                borderColor: 'rgba(52, 152, 219, 1)',
                                tension: 0.1
                            }]
                        }
                    });
                }

                if (dischargeData && document.getElementById("dischargeChart")) {
                    const ctx = document.getElementById("dischargeChart").getContext("2d");
                    if (dischargeChartInstance) dischargeChartInstance.destroy();
                    dischargeChartInstance = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: dischargeData.points.map(p => p.date),
                            datasets: [{
                                label: 'Cole Creek Discharge (cfs)',
                                data: dischargeData.points.map(p => p.value),
                                borderColor: 'rgba(46, 204, 113, 1)',
                                tension: 0.1
                            }]
                        }
                    });
                }
            }
        } catch (e) {
            console.error("Telemetry loading error", e);
        }
    }
});
