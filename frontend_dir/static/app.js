// Theme Toggle Logic
function toggleTheme() {
    const body = document.body;
    if (body.getAttribute("data-theme") === "light") {
        body.removeAttribute("data-theme");
    } else {
        body.setAttribute("data-theme", "light");
    }
}

window.onload = function() { fetchLeads(); };

// Expand BANT details
function toggleDetails(id) {
    const detailsDiv = document.getElementById(`details-${id}`);
    detailsDiv.style.display = detailsDiv.style.display === "block" ? "none" : "block";
}

// Drag and Drop Logic
function allowDrop(ev) {
    ev.preventDefault();
}

function dragStart(ev) {
    ev.dataTransfer.setData("card_id", ev.target.id);
}

async function dropCard(ev, newScore) {
    ev.preventDefault();
    const cardId = ev.dataTransfer.getData("card_id");
    const cardElement = document.getElementById(cardId);
    ev.currentTarget.appendChild(cardElement);

    const dbId = cardId.replace("card-", "");

    await fetch(`/api/leads/${dbId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ temperature_score: newScore })
    });
    
    // Refresh to update the pipeline metrics
    fetchLeads();
}

// Fetch Leads and Update UI
async function fetchLeads() {
    const response = await fetch('/api/leads');
    const leads = await response.json();
    
    document.getElementById('col-Cold').innerHTML = '<h3>❄️ Cold</h3>';
    document.getElementById('col-Warm').innerHTML = '<h3>🔥 Warm</h3>';
    document.getElementById('col-Hot').innerHTML = '<h3>🚨 Hot</h3>';
    
    const deletedLeads = [];
    let totalCount = 0;
    let hotCount = 0;

    leads.forEach(lead => {
        // Soft delete filter
        if (lead.is_active === false) { 
            deletedLeads.push(lead); 
            return; 
        }

        totalCount++;
        if (lead.temperature_score === "Hot") hotCount++;

        const safeScore = ["Cold", "Warm", "Hot"].includes(lead.temperature_score) ? lead.temperature_score : "Cold";
        
        const cardHtml = `
            <div class="card" id="card-${lead._id}" draggable="true" ondragstart="dragStart(event)">
                <h4>${lead.name}</h4>
                <p class="company-name">${lead.company}</p>
                
                <div onclick="toggleDetails('${lead._id}')">
                    <span class="tag">BANT Details ⬇️</span>
                </div>
                
                <div id="details-${lead._id}" class="bant-details">
                    <b>Budget:</b> ${lead.budget}<br><br>
                    <b>Authority:</b> ${lead.authority}<br><br>
                    <b>Need:</b> ${lead.need}<br><br>
                    <b>Timeline:</b> ${lead.timeline}
                </div>

                <div class="ai-advice">
                    <strong>💡 AI Next Step:</strong> ${lead.recommended_action || "Follow up manually."}
                </div>

                <div style="display: flex; gap: 0.5rem; margin-top: 10px;">
                    <button onclick="generateEmail('${lead._id}')" style="background:#10b981; margin:0; padding: 6px;">Draft Email</button>
                    <button onclick="deleteLead('${lead._id}')" class="danger" style="margin:0; padding: 6px;">Delete</button>
                </div>
            </div>
        `;
        document.getElementById(`col-${safeScore}`).insertAdjacentHTML('beforeend', cardHtml);
    });

    document.getElementById('metric-total').innerText = totalCount;
    document.getElementById('metric-hot').innerText = hotCount;

    renderDeletedLeads(deletedLeads);
}

// Render the Undo List
function renderDeletedLeads(deletedLeads) {
    const listDiv = document.getElementById('deleted-leads-list');
    if (deletedLeads.length === 0) { 
        listDiv.innerHTML = "No recently deleted leads."; 
        return; 
    }
    
    let html = "";
    deletedLeads.forEach(lead => {
        html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border-color);">
                <span>${lead.name}</span>
                <button onclick="restoreLead('${lead._id}')" class="secondary" style="width: auto; padding: 4px 8px; margin: 0;">Undo</button></div>`;
    });
    listDiv.innerHTML = html;
}

// AI Email Generation
async function generateEmail(id) {
    // 1. Grab the loading overlay and change the text
    const overlay = document.getElementById('loaderOverlay');
    const overlayText = overlay.querySelector('h3');
    overlayText.innerText = "🤖 AI is drafting email (approx 5s)...";
    overlay.style.display = 'flex';

    // 2. Ask Ollama to write the email
    const response = await fetch(`/api/leads/${id}/draft_email`, { method: 'POST' });
    const data = await response.json();
    
    // 3. Hide the spinner and show the completed email in the pop-up modal
    overlay.style.display = 'none';
    
    const modal = document.getElementById('emailModal');
    const outputBox = document.getElementById('emailOutput');
    outputBox.value = data.email;
    modal.style.display = 'block';

    // 4. Reset the spinner text back to normal for the next time we add a lead
    overlayText.innerText = "🤖 AI is qualifying lead...";
}

// Utility features
function copyEmail() {
    const emailText = document.getElementById('emailOutput');
    emailText.select();
    navigator.clipboard.writeText(emailText.value);
    showToast("Email copied to clipboard!");
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.innerText = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// API Interaction Functions
async function submitLead() {
    document.getElementById('loaderOverlay').style.display = 'flex';
    document.getElementById('submitBtn').disabled = true;

    const data = {
        name: document.getElementById('name').value,
        company: document.getElementById('company').value,
        raw_notes: document.getElementById('notes').value
    };

    await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    document.getElementById('loaderOverlay').style.display = 'none';
    document.getElementById('submitBtn').disabled = false;
    document.getElementById('name').value = '';
    document.getElementById('company').value = '';
    document.getElementById('notes').value = '';
    
    showToast("Lead Qualified & Saved!");
    fetchLeads();
}

async function deleteLead(id) {
    await fetch(`/api/leads/${id}`, { method: 'DELETE' });
    fetchLeads();
}

async function restoreLead(id) {
    await fetch(`/api/leads/${id}/restore`, { method: 'PUT' });
    fetchLeads();
}