document.addEventListener('DOMContentLoaded', () => {
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
});
