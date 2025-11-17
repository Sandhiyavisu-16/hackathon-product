// API Configuration
const API_URL = 'http://localhost:3000';
let currentToken = null;
let currentRole = null;

// Role Selection
function selectRole(role) {
    currentRole = role;
    currentToken = `${role}-token`;
    
    // Update UI
    document.querySelectorAll('.role-btn').forEach(btn => btn.classList.remove('active'));
    event.target.closest('.role-btn').classList.add('active');
    
    document.getElementById('currentRole').innerHTML = `
        <strong>Logged in as: ${role.toUpperCase()}</strong>
    `;
    
    // Show/hide tabs based on role
    const rubricsTab = document.getElementById('rubricsTab');
    const modelsTab = document.getElementById('modelsTab');
    const ideasTab = document.getElementById('ideasTab');
    
    // Show/hide buttons and set default view based on role
    const singleModeBtn = document.getElementById('singleModeBtn');
    const bulkModeBtn = document.getElementById('bulkModeBtn');
    const allIdeasBtn = document.getElementById('allIdeasBtn');
    
    if (role === 'admin') {
        // Admin: Show all tabs
        if (rubricsTab) rubricsTab.style.display = 'inline-block';
        if (modelsTab) modelsTab.style.display = 'inline-block';
        if (ideasTab) ideasTab.style.display = 'inline-block';
        
        // Admin: Show bulk upload and all ideas, hide single idea
        if (singleModeBtn) singleModeBtn.style.display = 'none';
        if (bulkModeBtn) bulkModeBtn.style.display = 'block';
        if (allIdeasBtn) allIdeasBtn.style.display = 'block';
        
        // Default to rubrics tab for admin
        showTab('rubrics');
    } else {
        // Contributor: Hide rubrics and models tabs, show only ideas
        if (rubricsTab) rubricsTab.style.display = 'none';
        if (modelsTab) modelsTab.style.display = 'none';
        if (ideasTab) ideasTab.style.display = 'inline-block';
        
        // Contributor: Show only single idea, hide others
        if (singleModeBtn) singleModeBtn.style.display = 'block';
        if (bulkModeBtn) bulkModeBtn.style.display = 'none';
        if (allIdeasBtn) allIdeasBtn.style.display = 'none';
        
        // Default to ideas tab and single idea mode for contributor
        showTab('ideas');
        showSubmissionMode('single');
    }
    
    // Reload data
    loadRubrics();
    loadModels();
}

// Tab Navigation
function showTab(tabName) {
    // Update tabs
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update content
    document.querySelectorAll('.content').forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    
    // Load data for the tab
    if (tabName === 'rubrics') loadRubrics();
    if (tabName === 'models') loadModels();
    if (tabName === 'ideas') {
        loadSubmissions();
        // Set default submission mode based on role
        if (currentRole === 'admin') {
            showSubmissionMode('bulk');
        } else {
            showSubmissionMode('single');
        }
    }
}

// API Helper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': currentToken ? `Bearer ${currentToken}` : '',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Request failed' }));
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Check API Status - DISABLED (was causing too many logs)
async function checkApiStatus() {
    // Health check disabled - assume API is connected
    const statusEl = document.getElementById('apiStatus');
    const indicatorEl = document.querySelector('.status-indicator');
    
    if (statusEl) {
        statusEl.innerHTML = 'API Connected';
    }
    if (indicatorEl) {
        indicatorEl.classList.add('status-online');
        indicatorEl.classList.remove('status-offline');
    }
}

// Load Rubrics
async function loadRubrics() {
    if (!currentToken) {
        document.getElementById('rubricsLoading').innerHTML = '⚠️ Please select a role first';
        return;
    }
    
    try {
        document.getElementById('rubricsLoading').style.display = 'block';
        document.getElementById('rubricsList').innerHTML = '';
        document.getElementById('rubricsError').style.display = 'none';
        
        const data = await apiCall('/api/rubrics');
        const rubrics = data.rubrics || [];
        
        document.getElementById('rubricsLoading').style.display = 'none';
        
        // Calculate total weight
        const totalWeight = rubrics
            .filter(r => r.is_active)
            .reduce((sum, r) => sum + r.weight, 0);
        
        const weightElement = document.getElementById('totalWeight');
        weightElement.textContent = `${totalWeight}%`;
        weightElement.className = 'weight-value ' + (totalWeight === 100 ? 'valid' : 'invalid');
        
        // Display rubrics
        const isAdmin = currentRole === 'admin';
        const listHtml = rubrics.map(rubric => `
            <div class="rubric-item" id="rubric-${rubric.id}">
                <div class="rubric-header">
                    <div>
                        <span class="rubric-name">${rubric.name}</span>
                        ${rubric.is_default ? '<span class="badge badge-default">Default</span>' : '<span class="badge" style="background: #fff3e0; color: #f57c00;">Custom</span>'}
                        ${rubric.is_active ? '<span class="badge badge-active">Active</span>' : '<span class="badge" style="background: #ffebee; color: #c62828;">Inactive</span>'}
                    </div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        ${isAdmin ? `
                            <input type="number" 
                                   class="weight-input" 
                                   value="${rubric.weight}" 
                                   min="0" 
                                   max="100"
                                   onchange="updateRubricWeight('${rubric.id}', this.value)"
                                   ${!rubric.is_active ? 'disabled' : ''}>
                            <span style="font-size: 18px; color: #667eea;">%</span>
                        ` : `
                            <div class="rubric-weight">${rubric.weight}%</div>
                        `}
                    </div>
                </div>
                <div class="rubric-description">${rubric.description}</div>
                <div class="rubric-guidance">💡 ${rubric.guidance}</div>
                ${isAdmin ? `
                    <div class="rubric-actions">
                        <button class="btn btn-small ${rubric.is_active ? 'btn-danger' : 'btn-success'}" 
                                onclick="toggleRubricActive('${rubric.id}', ${!rubric.is_active})">
                            ${rubric.is_active ? '🚫 Deactivate' : '✅ Activate'}
                        </button>
                        ${!rubric.is_default ? `
                            <button class="btn btn-small btn-danger" onclick="deleteRubric('${rubric.id}', '${rubric.name}')">
                                🗑️ Delete
                            </button>
                        ` : '<small style="color: #999; padding: 8px;">Default rubrics cannot be deleted</small>'}
                    </div>
                ` : ''}
            </div>
        `).join('');
        
        document.getElementById('rubricsList').innerHTML = listHtml || '<p>No rubrics found</p>';
        
    } catch (error) {
        document.getElementById('rubricsLoading').style.display = 'none';
        document.getElementById('rubricsError').style.display = 'block';
        document.getElementById('rubricsError').textContent = `Error loading rubrics: ${error.message}`;
    }
}

// Show/Hide Create Rubric Form
function showCreateRubricForm() {
    if (currentRole !== 'admin') {
        alert('Only admins can create custom rubrics');
        return;
    }
    document.getElementById('createRubricForm').style.display = 'block';
}

function hideCreateRubricForm() {
    document.getElementById('createRubricForm').style.display = 'none';
    // Clear form
    document.getElementById('rubricName').value = '';
    document.getElementById('rubricDescription').value = '';
    document.getElementById('rubricGuidance').value = '';
    document.getElementById('rubricWeight').value = '10';
}

// Create Custom Rubric
async function createCustomRubric() {
    const name = document.getElementById('rubricName').value.trim();
    const description = document.getElementById('rubricDescription').value.trim();
    const guidance = document.getElementById('rubricGuidance').value.trim();
    const weight = parseInt(document.getElementById('rubricWeight').value);
    
    if (!name || !description || !guidance) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (weight < 0 || weight > 100) {
        alert('Weight must be between 0 and 100');
        return;
    }
    
    try {
        document.getElementById('rubricsError').style.display = 'none';
        document.getElementById('rubricsSuccess').style.display = 'none';
        
        await apiCall('/api/rubrics', {
            method: 'POST',
            body: JSON.stringify({
                name,
                description,
                guidance,
                weight
            })
        });
        
        document.getElementById('rubricsSuccess').style.display = 'block';
        document.getElementById('rubricsSuccess').textContent = `✅ Custom rubric "${name}" created successfully!`;
        
        hideCreateRubricForm();
        loadRubrics();
        
        setTimeout(() => {
            document.getElementById('rubricsSuccess').style.display = 'none';
        }, 5000);
        
    } catch (error) {
        document.getElementById('rubricsError').style.display = 'block';
        document.getElementById('rubricsError').textContent = `Error creating rubric: ${error.message}`;
    }
}

// Update Rubric Weight
async function updateRubricWeight(rubricId, newWeight) {
    const weight = parseInt(newWeight);
    
    if (weight < 0 || weight > 100) {
        alert('Weight must be between 0 and 100');
        loadRubrics(); // Reset to original value
        return;
    }
    
    try {
        await apiCall(`/api/rubrics/${rubricId}`, {
            method: 'PATCH',
            body: JSON.stringify({ weight })
        });
        
        document.getElementById('rubricsSuccess').style.display = 'block';
        document.getElementById('rubricsSuccess').textContent = '✅ Weight updated successfully!';
        
        loadRubrics();
        
        setTimeout(() => {
            document.getElementById('rubricsSuccess').style.display = 'none';
        }, 3000);
        
    } catch (error) {
        document.getElementById('rubricsError').style.display = 'block';
        document.getElementById('rubricsError').textContent = `Error updating weight: ${error.message}`;
        loadRubrics(); // Reset to original value
    }
}

// Toggle Rubric Active Status
async function toggleRubricActive(rubricId, newStatus) {
    try {
        await apiCall(`/api/rubrics/${rubricId}`, {
            method: 'PATCH',
            body: JSON.stringify({ is_active: newStatus })
        });
        
        document.getElementById('rubricsSuccess').style.display = 'block';
        document.getElementById('rubricsSuccess').textContent = `✅ Rubric ${newStatus ? 'activated' : 'deactivated'} successfully!`;
        
        loadRubrics();
        
        setTimeout(() => {
            document.getElementById('rubricsSuccess').style.display = 'none';
        }, 3000);
        
    } catch (error) {
        document.getElementById('rubricsError').style.display = 'block';
        document.getElementById('rubricsError').textContent = `Error updating rubric: ${error.message}`;
    }
}

// Delete Rubric
async function deleteRubric(rubricId, rubricName) {
    if (!confirm(`Are you sure you want to delete the rubric "${rubricName}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        // Note: Delete endpoint not implemented yet, but UI is ready
        alert('Delete functionality will be available once the DELETE endpoint is implemented in the backend.');
        
        // When implemented, it would be:
        // await apiCall(`/api/rubrics/${rubricId}`, { method: 'DELETE' });
        // loadRubrics();
        
    } catch (error) {
        document.getElementById('rubricsError').style.display = 'block';
        document.getElementById('rubricsError').textContent = `Error deleting rubric: ${error.message}`;
    }
}

// Load Models
async function loadModels() {
    if (!currentToken) {
        document.getElementById('modelsLoading').innerHTML = '⚠️ Please select a role first';
        return;
    }
    
    try {
        document.getElementById('modelsLoading').style.display = 'block';
        document.getElementById('modelsList').innerHTML = '';
        document.getElementById('modelsError').style.display = 'none';
        
        const data = await apiCall('/api/config/model');
        
        document.getElementById('modelsLoading').style.display = 'none';
        
        let html = '';
        
        if (data.active) {
            html += `
                <div style="padding: 20px; background: #e8f5e9; border-radius: 8px; margin-bottom: 20px;">
                    <h3>✅ Active Configuration</h3>
                    <p><strong>Name:</strong> ${data.active.name}</p>
                    <p><strong>Provider:</strong> ${data.active.provider}</p>
                    <p><strong>Status:</strong> ${data.active.status}</p>
                    <p><strong>Version:</strong> ${data.active.version}</p>
                </div>
            `;
        } else {
            html += '<p style="padding: 20px; background: #fff3e0; border-radius: 8px;">No active configuration</p>';
        }
        
        if (data.history && data.history.length > 0) {
            html += '<h3 style="margin-top: 30px; margin-bottom: 15px;">Configuration History</h3>';
            html += data.history.map(config => `
                <div style="padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 10px; background: ${config.is_active ? '#f0f8f0' : 'white'};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div>
                            <strong>${config.name}</strong>
                            <span style="margin-left: 10px; color: #666;">${config.provider.replace('_', ' ').toUpperCase()}</span>
                        </div>
                        <span style="padding: 4px 12px; background: ${
                            config.status === 'active' ? '#4caf50' : 
                            config.status === 'tested' ? '#2196f3' : 
                            config.status === 'draft' ? '#ff9800' : '#999'
                        }; color: white; border-radius: 12px; font-size: 12px;">
                            ${config.status.toUpperCase()}
                        </span>
                    </div>
                    <div style="font-size: 14px; color: #666; margin-bottom: 10px;">
                        Version ${config.version} • Created ${new Date(config.created_at).toLocaleDateString()}
                        ${config.purpose ? `<br>🎯 Purpose: <strong>${config.purpose.charAt(0).toUpperCase() + config.purpose.slice(1)}</strong>` : ''}
                        ${config.notes ? `<br>📝 ${config.notes}` : ''}
                    </div>
                    ${currentRole === 'admin' ? `
                        <div style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                            ${!config.is_active ? `
                                ${config.status === 'draft' ? `
                                    <button class="btn btn-small" onclick="testModelConnection('${config.id}', '${config.name}')">
                                        🧪 Test Connection
                                    </button>
                                ` : ''}
                                ${config.status === 'tested' ? `
                                    <button class="btn btn-small btn-success" onclick="activateModelConfig('${config.id}', '${config.name}')">
                                        ✅ Activate
                                    </button>
                                    <button class="btn btn-small" onclick="testModelConnection('${config.id}', '${config.name}')">
                                        🔄 Re-test
                                    </button>
                                ` : ''}
                                ${config.status === 'inactive' ? `
                                    <button class="btn btn-small" onclick="activateModelConfig('${config.id}', '${config.name}')">
                                        🔄 Rollback & Activate
                                    </button>
                                ` : ''}
                                <button class="btn btn-small" onclick="editModelConfig('${config.id}')">
                                    ✏️ Edit
                                </button>
                                <button class="btn btn-small btn-danger" onclick="deleteModelConfig('${config.id}', '${config.name}')">
                                    🗑️ Delete
                                </button>
                            ` : `
                                <div style="display: flex; gap: 10px; align-items: center;">
                                    <span style="color: #4caf50; font-weight: 600;">✅ Currently Active</span>
                                    <button class="btn btn-small btn-danger" onclick="deactivateModelConfig('${config.id}', '${config.name}')">
                                        🚫 Deactivate
                                    </button>
                                </div>
                            `}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
        
        document.getElementById('modelsList').innerHTML = html;
        
    } catch (error) {
        document.getElementById('modelsLoading').style.display = 'none';
        document.getElementById('modelsError').style.display = 'block';
        document.getElementById('modelsError').textContent = `Error loading models: ${error.message}`;
    }
}

// Show/Hide Create Model Form
function showCreateModelForm() {
    document.getElementById('createModelForm').style.display = 'block';
    updateProviderFields(); // Show correct fields for default provider
}

function hideCreateModelForm() {
    document.getElementById('createModelForm').style.display = 'none';
    clearModelForm();
}

// Update Provider-Specific Fields
function updateProviderFields() {
    const provider = document.getElementById('provider').value;
    
    // Hide all provider-specific fields
    document.getElementById('azureFields').style.display = 'none';
    document.getElementById('geminiFields').style.display = 'none';
    document.getElementById('gemmaFields').style.display = 'none';
    
    // Show relevant fields
    if (provider === 'azure_openai') {
        document.getElementById('azureFields').style.display = 'block';
    } else if (provider === 'gemini') {
        document.getElementById('geminiFields').style.display = 'block';
    } else if (provider === 'gemma') {
        document.getElementById('gemmaFields').style.display = 'block';
    }
}

// Clear Model Form
function clearModelForm() {
    document.getElementById('configName').value = '';
    document.getElementById('azureEndpoint').value = '';
    document.getElementById('azureApiKey').value = '';
    document.getElementById('azureDeployment').value = '';
    document.getElementById('azureApiVersion').value = '2024-08-01';
    document.getElementById('geminiProjectId').value = '';
    document.getElementById('geminiLocation').value = '';
    document.getElementById('geminiApiKey').value = '';
    document.getElementById('geminiModel').value = '';
    document.getElementById('gemmaEndpoint').value = '';
    document.getElementById('gemmaModel').value = '';
    document.getElementById('gemmaAuth').value = '';
    document.getElementById('temperature').value = '0.7';
    document.getElementById('maxTokens').value = '2048';
    document.getElementById('rateLimit').value = '120';
    document.getElementById('configNotes').value = '';
}

// Create Model Configuration
async function createModelConfig() {
    const provider = document.getElementById('provider').value;
    const name = document.getElementById('configName').value.trim();
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('maxTokens').value);
    const rateLimit = parseInt(document.getElementById('rateLimit').value);
    const notes = document.getElementById('configNotes').value.trim();
    
    if (!name) {
        alert('Please enter a configuration name');
        return;
    }
    
    let settings = {
        temperature,
        max_tokens: maxTokens,
        rate_limit: rateLimit
    };
    
    // Add provider-specific settings
    if (provider === 'azure_openai') {
        const endpoint = document.getElementById('azureEndpoint').value.trim();
        const apiKey = document.getElementById('azureApiKey').value.trim();
        const deployment = document.getElementById('azureDeployment').value.trim();
        const apiVersion = document.getElementById('azureApiVersion').value.trim();
        
        if (!endpoint || !apiKey || !deployment) {
            alert('Please fill in all required Azure OpenAI fields');
            return;
        }
        
        settings = {
            ...settings,
            endpoint,
            api_key: apiKey,
            deployment_name: deployment,
            api_version: apiVersion
        };
    } else if (provider === 'gemini') {
        const projectId = document.getElementById('geminiProjectId').value.trim();
        const location = document.getElementById('geminiLocation').value.trim();
        const apiKey = document.getElementById('geminiApiKey').value.trim();
        const model = document.getElementById('geminiModel').value.trim();
        
        if (!apiKey || !model) {
            alert('Please fill in API Key and Model Name');
            return;
        }
        
        settings = {
            ...settings,
            api_key: apiKey,
            model
        };
        
        // Add optional Vertex AI fields if provided
        if (projectId && location) {
            settings.project_id = projectId;
            settings.location = location;
            settings.use_vertex_ai = true;
        }
    } else if (provider === 'gemma') {
        const endpoint = document.getElementById('gemmaEndpoint').value.trim();
        const model = document.getElementById('gemmaModel').value.trim();
        const auth = document.getElementById('gemmaAuth').value.trim();
        
        if (!endpoint || !model) {
            alert('Please fill in all required Gemma fields');
            return;
        }
        
        settings = {
            ...settings,
            endpoint,
            model,
            ...(auth && { auth })
        };
    }
    
    try {
        document.getElementById('modelsError').style.display = 'none';
        document.getElementById('modelsSuccess').style.display = 'none';
        
        const config = {
            provider,
            name,
            settings,
            ...(notes && { notes })
        };
        
        const result = await apiCall('/api/config/model', {
            method: 'POST',
            body: JSON.stringify(config)
        });
        
        document.getElementById('modelsSuccess').style.display = 'block';
        document.getElementById('modelsSuccess').textContent = `✅ Configuration "${name}" created successfully! You can now test the connection.`;
        
        hideCreateModelForm();
        loadModels();
        
    } catch (error) {
        document.getElementById('modelsError').style.display = 'block';
        document.getElementById('modelsError').textContent = `Error creating configuration: ${error.message}`;
    }
}

// Test Model Connection
async function testModelConnection(configId, configName) {
    if (!confirm(`Test connection for "${configName}"?\n\nThis will make a test API call to verify the configuration.`)) {
        return;
    }
    
    try {
        document.getElementById('modelsError').style.display = 'none';
        document.getElementById('modelsSuccess').style.display = 'none';
        
        // Show loading state
        const testButton = event.target;
        const originalText = testButton.textContent;
        testButton.textContent = '⏳ Testing...';
        testButton.disabled = true;
        
        const result = await apiCall(`/api/config/model/${configId}/test`, {
            method: 'POST',
            body: JSON.stringify({})
        });
        
        testButton.textContent = originalText;
        testButton.disabled = false;
        
        if (result.success) {
            // Show toast notification instead of inline message
            showToast(
                'Connection Test Successful!',
                `Latency: ${result.latency}ms | Sample: ${result.sample || 'Connected'} | Status: Ready to activate`,
                'success',
                6000
            );
            loadModels();
        } else {
            // Show error toast
            showToast(
                'Connection Test Failed',
                `Error: ${result.error || 'Unknown error'}. Please check your configuration settings.`,
                'error',
                8000
            );
        }
        
    } catch (error) {
        document.getElementById('modelsError').style.display = 'block';
        document.getElementById('modelsError').textContent = `Error testing connection: ${error.message}`;
        
        // Reset button
        if (event.target) {
            event.target.textContent = '🧪 Test Connection';
            event.target.disabled = false;
        }
    }
}

// Activate Model Configuration
async function activateModelConfig(configId, configName) {
    // Show purpose selection dialog
    const purpose = await showPurposeDialog(configName);
    
    if (!purpose) {
        return; // User cancelled
    }
    
    try {
        document.getElementById('modelsError').style.display = 'none';
        document.getElementById('modelsSuccess').style.display = 'none';
        
        await apiCall(`/api/config/model/${configId}/activate`, {
            method: 'POST',
            body: JSON.stringify({ purpose })
        });
        
        showToast(
            'Configuration Activated',
            `"${configName}" is now active for ${purpose}`,
            'success',
            3000
        );
        
        loadModels();
        
    } catch (error) {
        console.error('Activation error:', error);
        let errorMsg = error.message;
        
        // Provide helpful hints based on common errors
        if (errorMsg.includes('tested')) {
            errorMsg += '\n\nℹ️ Tip: Test the connection first before activating.';
        }
        
        showToast(
            'Activation Failed',
            errorMsg,
            'error',
            7000
        );
    }
}

// Show purpose selection dialog
function showPurposeDialog(configName) {
    return new Promise((resolve) => {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;
        
        // Create modal content
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 8px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        `;
        
        modal.innerHTML = `
            <h3 style="margin-top: 0; color: #333;">Select Activation Purpose</h3>
            <p style="color: #666; margin-bottom: 20px;">
                Activate "${configName}" for:
            </p>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <button id="purposeEvaluation" class="btn btn-primary" style="padding: 15px; font-size: 16px;">
                    📊 Evaluation
                    <div style="font-size: 12px; font-weight: normal; margin-top: 5px; opacity: 0.9;">
                        Use this model to evaluate and score idea submissions
                    </div>
                </button>
                <button id="purposeVerification" class="btn btn-primary" style="padding: 15px; font-size: 16px;">
                    ✅ Verification
                    <div style="font-size: 12px; font-weight: normal; margin-top: 5px; opacity: 0.9;">
                        Use this model to verify and validate evaluation results
                    </div>
                </button>
                <button id="purposeCancel" class="btn" style="padding: 10px;">
                    Cancel
                </button>
            </div>
        `;
        
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // Handle button clicks
        document.getElementById('purposeEvaluation').onclick = () => {
            document.body.removeChild(overlay);
            resolve('evaluation');
        };
        
        document.getElementById('purposeVerification').onclick = () => {
            document.body.removeChild(overlay);
            resolve('verification');
        };
        
        document.getElementById('purposeCancel').onclick = () => {
            document.body.removeChild(overlay);
            resolve(null);
        };
        
        // Close on overlay click
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                document.body.removeChild(overlay);
                resolve(null);
            }
        };
    });
}

// Deactivate Model Configuration
async function deactivateModelConfig(configId, configName) {
    if (!confirm(`Deactivate configuration "${configName}"?\n\nNo model will be active after this action.`)) {
        return;
    }
    
    try {
        document.getElementById('modelsError').style.display = 'none';
        document.getElementById('modelsSuccess').style.display = 'none';
        
        await apiCall(`/api/config/model/${configId}/deactivate`, {
            method: 'POST',
            body: JSON.stringify({})
        });
        
        showToast(
            'Configuration Deactivated',
            `"${configName}" has been deactivated successfully`,
            'success',
            3000
        );
        
        loadModels();
        
    } catch (error) {
        showToast(
            'Deactivation Failed',
            error.message,
            'error',
            5000
        );
    }
}

// Download CSV Template
async function downloadTemplate() {
    try {
        const response = await fetch(`${API_URL}/api/ideas/template`, {
            headers: {
                'Authorization': currentToken ? `Bearer ${currentToken}` : ''
            }
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ideas_template.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        document.getElementById('ideasSuccess').style.display = 'block';
        document.getElementById('ideasSuccess').textContent = 'Template downloaded successfully!';
        setTimeout(() => {
            document.getElementById('ideasSuccess').style.display = 'none';
        }, 3000);
        
    } catch (error) {
        document.getElementById('ideasError').style.display = 'block';
        document.getElementById('ideasError').textContent = `Error downloading template: ${error.message}`;
    }
}

// Handle CSV File Selection
let selectedCsvFile = null;
let selectedSupportFile = null;

function handleCsvFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    if (!hasValidExtension) {
        alert('Please select a CSV or Excel file (.csv, .xlsx, .xls)');
        return;
    }
    
    selectedCsvFile = file;
    document.getElementById('csvFileName').innerHTML = `
        ✅ ${file.name} <span style="color: #666; font-size: 14px;">(${(file.size / 1024).toFixed(2)} KB)</span>
    `;
    document.getElementById('csvFileName').style.color = '#4caf50';
}

// Handle Support File Selection
function handleSupportFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validExtensions = ['.pdf', '.docx', '.pptx', '.mp4', '.png', '.jpg', '.jpeg'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
        alert('Invalid file type. Please select: PDF, DOCX, PPTX, MP4, PNG, or JPEG');
        return;
    }
    
    // Check file size (max 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
        alert(`File too large. Maximum size is 100MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB`);
        event.target.value = ''; // Clear the file input
        return;
    }
    
    selectedSupportFile = file;
    document.getElementById('supportFileName').innerHTML = `
        ✅ ${file.name} <span style="color: #666; font-size: 14px;">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
    `;
    document.getElementById('supportFileName').style.color = '#4caf50';
}

// Submit Ideas
async function submitIdeas() {
    if (!currentToken) {
        alert('Please select a role first');
        return;
    }
    
    // Validate required fields
    if (!selectedCsvFile) {
        alert('Please select a CSV or Excel file');
        return;
    }
    
    try {
        document.getElementById('ideasError').style.display = 'none';
        document.getElementById('ideasSuccess').style.display = 'none';
        document.getElementById('uploadStatus').style.display = 'block';
        
        // Disable submit button
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Submitting...';
        
        document.getElementById('uploadDetails').innerHTML = `
            <p>📄 CSV File: ${selectedCsvFile.name}</p>
            ${selectedSupportFile ? `<p>📎 Support File: ${selectedSupportFile.name}</p>` : ''}
            <p style="color: #667eea;">⏳ Uploading and processing...</p>
            <p style="color: #666; font-size: 14px;">Email notifications will be sent to addresses in your CSV</p>
        `;
        
        // Create FormData
        const formData = new FormData();
        formData.append('csv', selectedCsvFile);
        if (selectedSupportFile) {
            formData.append('supportFile', selectedSupportFile);
        }
        
        // Submit to backend
        const response = await fetch(`${API_URL}/api/ideas/submit`, {
            method: 'POST',
            headers: {
                'Authorization': currentToken ? `Bearer ${currentToken}` : ''
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Submission failed' }));
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show success
        document.getElementById('uploadDetails').innerHTML = `
            <p style="color: #4caf50; font-weight: 600;">✅ Submission Successful!</p>
            <p>📄 CSV File: ${selectedCsvFile.name}</p>
            ${selectedSupportFile ? `<p>📎 Support File: ${selectedSupportFile.name}</p>` : ''}
            <hr style="margin: 15px 0; border: none; border-top: 1px solid #e0e0e0;">
            <p><strong>Submission ID:</strong> ${result.submission_id || 'N/A'}</p>
            <p><strong>Total Ideas:</strong> ${result.total_rows || 'Processing...'}</p>
            <p><strong>Valid Ideas:</strong> ${result.valid_rows || 'Processing...'}</p>
            <p><strong>Invalid Ideas:</strong> ${result.invalid_rows || 0}</p>
            <p><strong>Status:</strong> ${result.status || 'Received'}</p>
            <p style="color: #666; font-size: 14px; margin-top: 15px;">
                Email notifications will be sent to the addresses in your CSV file
            </p>
        `;
        
        document.getElementById('ideasSuccess').style.display = 'block';
        document.getElementById('ideasSuccess').textContent = '✅ Ideas submitted successfully! Email notifications sent to CSV addresses.';
        
        // Reset form
        selectedCsvFile = null;
        selectedSupportFile = null;
        document.getElementById('csvFile').value = '';
        document.getElementById('supportFile').value = '';
        document.getElementById('csvFileName').innerHTML = '📄 Click to select CSV file';
        document.getElementById('csvFileName').style.color = '#667eea';
        document.getElementById('supportFileName').innerHTML = '📎 Click to select support file';
        document.getElementById('supportFileName').style.color = '#667eea';
        
        // Load submissions
        loadSubmissions();
        
    } catch (error) {
        document.getElementById('uploadDetails').innerHTML = `
            <p style="color: #f44336; font-weight: 600;">❌ Submission Failed</p>
            <p>${error.message}</p>
        `;
        
        document.getElementById('ideasError').style.display = 'block';
        document.getElementById('ideasError').textContent = `Error: ${error.message}`;
    } finally {
        // Re-enable submit button
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Submit Ideas';
    }
}

// Load Submissions
async function loadSubmissions() {
    if (!currentToken) return;
    
    try {
        document.getElementById('submissionsLoading').style.display = 'block';
        document.getElementById('submissionsList').innerHTML = '';
        
        const data = await apiCall('/api/ideas/submissions');
        
        document.getElementById('submissionsLoading').style.display = 'none';
        
        if (!data.submissions || data.submissions.length === 0) {
            document.getElementById('submissionsList').innerHTML = '<p style="color: #666;">No submissions yet</p>';
            return;
        }
        
        const html = data.submissions.map(sub => `
            <div style="padding: 20px; background: white; border: 2px solid #e0e0e0; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                    <div>
                        <strong style="font-size: 16px;">Submission #${sub.id}</strong>
                        <div style="color: #666; font-size: 14px; margin-top: 5px;">
                            Submitted: ${new Date(sub.created_at).toLocaleString()}
                        </div>
                    </div>
                    <span style="padding: 6px 12px; background: ${
                        sub.status === 'validated' ? '#4caf50' :
                        sub.status === 'queued_for_scoring' ? '#2196f3' :
                        sub.status === 'failed' ? '#f44336' : '#ff9800'
                    }; color: white; border-radius: 12px; font-size: 12px; font-weight: 600;">
                        ${sub.status.toUpperCase().replace(/_/g, ' ')}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 15px;">
                    <div>
                        <div style="color: #666; font-size: 12px;">Total Ideas</div>
                        <div style="font-size: 20px; font-weight: 600; color: #667eea;">${sub.total_rows || 0}</div>
                    </div>
                    <div>
                        <div style="color: #666; font-size: 12px;">Valid</div>
                        <div style="font-size: 20px; font-weight: 600; color: #4caf50;">${sub.valid_rows || 0}</div>
                    </div>
                    <div>
                        <div style="color: #666; font-size: 12px;">Invalid</div>
                        <div style="font-size: 20px; font-weight: 600; color: #f44336;">${sub.invalid_rows || 0}</div>
                    </div>
                </div>
                ${sub.support_file_uri ? `
                    <div style="margin-top: 10px; padding: 10px; background: #f9f9f9; border-radius: 4px;">
                        📎 Support file attached (${sub.support_file_type})
                    </div>
                ` : ''}
                <div style="margin-top: 15px; display: flex; gap: 10px;">
                    <button class="btn btn-small btn-danger" onclick="deleteSubmission('${sub.id}', 'Submission #${sub.id}')" style="background: #f44336; padding: 8px 16px; font-size: 14px;">
                        🗑️ Delete Submission
                    </button>
                </div>
            </div>
        `).join('');
        
        document.getElementById('submissionsList').innerHTML = html;
        
    } catch (error) {
        document.getElementById('submissionsLoading').style.display = 'none';
        document.getElementById('submissionsList').innerHTML = `<p style="color: #f44336;">Error loading submissions: ${error.message}</p>`;
    }
}

// Edit Model Configuration
async function editModelConfig(configId) {
    try {
        // Fetch the configuration details
        const config = await apiCall(`/api/config/model/${configId}`);
        
        // Show the form
        showCreateModelForm();
        
        // Populate the form with existing values
        document.getElementById('provider').value = config.provider;
        document.getElementById('configName').value = config.name;
        document.getElementById('temperature').value = config.settings.temperature || 0.7;
        document.getElementById('maxTokens').value = config.settings.max_tokens || 2048;
        document.getElementById('rateLimit').value = config.settings.rate_limit || 120;
        document.getElementById('configNotes').value = config.notes || '';
        
        // Update provider-specific fields
        updateProviderFields();
        
        if (config.provider === 'azure_openai') {
            document.getElementById('azureEndpoint').value = config.settings.endpoint || '';
            document.getElementById('azureDeployment').value = config.settings.deployment_name || '';
            document.getElementById('azureApiVersion').value = config.settings.api_version || '2024-08-01';
            // API key is not returned for security, leave empty
        } else if (config.provider === 'gemini') {
            document.getElementById('geminiProjectId').value = config.settings.project_id || '';
            document.getElementById('geminiLocation').value = config.settings.location || '';
            document.getElementById('geminiModel').value = config.settings.model || '';
            // API key is not returned for security, leave empty
        } else if (config.provider === 'gemma') {
            document.getElementById('gemmaEndpoint').value = config.settings.endpoint || '';
            document.getElementById('gemmaModel').value = config.settings.model || '';
            // Auth token is not returned for security, leave empty
        }
        
        // Change the form title and button
        document.querySelector('#createModelForm h3').textContent = 'Edit Model Configuration';
        const createButton = document.querySelector('#createModelForm button[onclick="createModelConfig()"]');
        createButton.textContent = 'Update Configuration';
        createButton.setAttribute('onclick', `updateModelConfig('${configId}')`);
        
        // Add a note about API keys
        const noteDiv = document.createElement('div');
        noteDiv.id = 'editNote';
        noteDiv.style.cssText = 'background: #fff3e0; padding: 12px; border-radius: 8px; margin-bottom: 15px; color: #f57c00;';
        noteDiv.innerHTML = '⚠️ <strong>Note:</strong> API keys are not displayed for security. Leave the API key field empty to keep the existing key, or enter a new one to update it.';
        document.querySelector('#createModelForm h3').after(noteDiv);
        
    } catch (error) {
        document.getElementById('modelsError').style.display = 'block';
        document.getElementById('modelsError').textContent = `Error loading configuration: ${error.message}`;
    }
}

// Update Model Configuration
async function updateModelConfig(configId) {
    const provider = document.getElementById('provider').value;
    const name = document.getElementById('configName').value.trim();
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('maxTokens').value);
    const rateLimit = parseInt(document.getElementById('rateLimit').value);
    const notes = document.getElementById('configNotes').value.trim();
    
    if (!name) {
        alert('Please enter a configuration name');
        return;
    }
    
    let settings = {
        temperature,
        max_tokens: maxTokens,
        rate_limit: rateLimit
    };
    
    // Add provider-specific settings
    if (provider === 'azure_openai') {
        const endpoint = document.getElementById('azureEndpoint').value.trim();
        const apiKey = document.getElementById('azureApiKey').value.trim();
        const deployment = document.getElementById('azureDeployment').value.trim();
        const apiVersion = document.getElementById('azureApiVersion').value.trim();
        
        if (!endpoint || !deployment) {
            alert('Please fill in all required Azure OpenAI fields');
            return;
        }
        
        settings = {
            ...settings,
            endpoint,
            deployment_name: deployment,
            api_version: apiVersion
        };
        
        // Only include API key if it was changed
        if (apiKey) {
            settings.api_key = apiKey;
        }
    } else if (provider === 'gemini') {
        const projectId = document.getElementById('geminiProjectId').value.trim();
        const location = document.getElementById('geminiLocation').value.trim();
        const apiKey = document.getElementById('geminiApiKey').value.trim();
        const model = document.getElementById('geminiModel').value.trim();
        
        if (!model) {
            alert('Please fill in Model Name');
            return;
        }
        
        settings = {
            ...settings,
            model
        };
        
        // Add optional Vertex AI fields if provided
        if (projectId && location) {
            settings.project_id = projectId;
            settings.location = location;
            settings.use_vertex_ai = true;
        }
        
        if (apiKey) {
            settings.api_key = apiKey;
        }
    } else if (provider === 'gemma') {
        const endpoint = document.getElementById('gemmaEndpoint').value.trim();
        const model = document.getElementById('gemmaModel').value.trim();
        const auth = document.getElementById('gemmaAuth').value.trim();
        
        if (!endpoint || !model) {
            alert('Please fill in all required Gemma fields');
            return;
        }
        
        settings = {
            ...settings,
            endpoint,
            model
        };
        
        if (auth) {
            settings.auth = auth;
        }
    }
    
    try {
        document.getElementById('modelsError').style.display = 'none';
        document.getElementById('modelsSuccess').style.display = 'none';
        
        const config = {
            name,
            settings,
            ...(notes && { notes })
        };
        
        await apiCall(`/api/config/model/${configId}`, {
            method: 'PATCH',
            body: JSON.stringify(config)
        });
        
        document.getElementById('modelsSuccess').style.display = 'block';
        document.getElementById('modelsSuccess').textContent = `✅ Configuration "${name}" updated successfully! You can now test the connection.`;
        
        hideCreateModelForm();
        loadModels();
        
        setTimeout(() => {
            document.getElementById('modelsSuccess').style.display = 'none';
        }, 5000);
        
    } catch (error) {
        document.getElementById('modelsError').style.display = 'block';
        document.getElementById('modelsError').textContent = `Error updating configuration: ${error.message}`;
    }
}

// Delete Model Configuration
async function deleteModelConfig(configId, configName) {
    if (!confirm(`Are you sure you want to delete the configuration "${configName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        document.getElementById('modelsError').style.display = 'none';
        document.getElementById('modelsSuccess').style.display = 'none';
        
        await apiCall(`/api/config/model/${configId}`, {
            method: 'DELETE'
        });
        
        document.getElementById('modelsSuccess').style.display = 'block';
        document.getElementById('modelsSuccess').textContent = `✅ Configuration "${configName}" deleted successfully!`;
        
        loadModels();
        
        setTimeout(() => {
            document.getElementById('modelsSuccess').style.display = 'none';
        }, 5000);
        
    } catch (error) {
        document.getElementById('modelsError').style.display = 'block';
        document.getElementById('modelsError').textContent = `Error deleting configuration: ${error.message}`;
    }
}

// Override hideCreateModelForm to reset edit mode
const originalHideCreateModelForm = hideCreateModelForm;
hideCreateModelForm = function() {
    // Reset form title and button
    document.querySelector('#createModelForm h3').textContent = 'Create Model Configuration';
    const createButton = document.querySelector('#createModelForm button[onclick^="createModelConfig"], button[onclick^="updateModelConfig"]');
    if (createButton) {
        createButton.textContent = 'Create Configuration';
        createButton.setAttribute('onclick', 'createModelConfig()');
    }
    
    // Remove edit note if exists
    const editNote = document.getElementById('editNote');
    if (editNote) {
        editNote.remove();
    }
    
    // Call original function
    originalHideCreateModelForm();
};

// Initialize
// Health check completely disabled - was causing too many logs
// checkApiStatus();
// setInterval(checkApiStatus, 5000);

// Delete Submission
async function deleteSubmission(submissionId, displayId) {
    if (!confirm(`Are you sure you want to delete submission ${displayId}?\n\nThis will permanently delete:\n- The submission record\n- All associated ideas\n- Uploaded files\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        document.getElementById('ideasError').style.display = 'none';
        document.getElementById('ideasSuccess').style.display = 'none';
        
        await apiCall(`/api/ideas/${submissionId}`, {
            method: 'DELETE'
        });
        
        document.getElementById('ideasSuccess').style.display = 'block';
        document.getElementById('ideasSuccess').textContent = `✅ Submission ${displayId} deleted successfully!`;
        
        // Reload submissions list
        loadSubmissions();
        
        setTimeout(() => {
            document.getElementById('ideasSuccess').style.display = 'none';
        }, 5000);
        
    } catch (error) {
        document.getElementById('ideasError').style.display = 'block';
        document.getElementById('ideasError').textContent = `Error deleting submission: ${error.message}`;
    }
}


// Submission Mode Switcher
function showSubmissionMode(mode) {
    // Hide all modes
    document.getElementById('singleIdeaMode').style.display = 'none';
    document.getElementById('bulkUploadMode').style.display = 'none';
    document.getElementById('allIdeasMode').style.display = 'none';
    document.getElementById('submissionsHistory').style.display = 'none';
    
    // Reset button styles (only for visible buttons)
    const singleModeBtn = document.getElementById('singleModeBtn');
    const bulkModeBtn = document.getElementById('bulkModeBtn');
    const allIdeasBtn = document.getElementById('allIdeasBtn');
    
    if (singleModeBtn && singleModeBtn.style.display !== 'none') {
        singleModeBtn.style.background = '#e0e0e0';
        singleModeBtn.style.color = '#333';
    }
    if (bulkModeBtn && bulkModeBtn.style.display !== 'none') {
        bulkModeBtn.style.background = '#e0e0e0';
        bulkModeBtn.style.color = '#333';
    }
    if (allIdeasBtn && allIdeasBtn.style.display !== 'none') {
        allIdeasBtn.style.background = '#e0e0e0';
        allIdeasBtn.style.color = '#333';
    }
    
    // Show selected mode
    if (mode === 'single') {
        document.getElementById('singleIdeaMode').style.display = 'block';
        document.getElementById('submissionsHistory').style.display = 'block';
        if (singleModeBtn) {
            singleModeBtn.style.background = '#667eea';
            singleModeBtn.style.color = 'white';
        }
    } else if (mode === 'bulk') {
        document.getElementById('bulkUploadMode').style.display = 'block';
        document.getElementById('submissionsHistory').style.display = 'block';
        if (bulkModeBtn) {
            bulkModeBtn.style.background = '#667eea';
            bulkModeBtn.style.color = 'white';
        }
    } else if (mode === 'all') {
        document.getElementById('allIdeasMode').style.display = 'block';
        if (allIdeasBtn) {
            allIdeasBtn.style.background = '#667eea';
            allIdeasBtn.style.color = 'white';
        }
        loadAllIdeas();
    }
}

// Submit Single Idea
async function submitSingleIdea(event) {
    event.preventDefault();
    
    if (!currentToken) {
        alert('Please select a role first');
        return;
    }
    
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        document.getElementById('singleIdeaStatus').style.display = 'none';
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Submitting...';
        
        // Send as FormData (not JSON)
        const response = await fetch(`${API_URL}/api/ideas/single`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Submission failed');
        }
        
        const result = await response.json();
        
        // Show success message
        document.getElementById('singleIdeaStatus').style.display = 'block';
        document.getElementById('singleIdeaStatus').style.background = '#d4edda';
        document.getElementById('singleIdeaStatus').style.border = '1px solid #c3e6cb';
        document.getElementById('singleIdeaStatus').style.color = '#155724';
        document.getElementById('singleIdeaStatus').innerHTML = `
            <strong>✅ Success!</strong><br>
            Your idea has been submitted successfully.<br>
            <small>Idea ID: ${result.idea_id}</small>
        `;
        
        // Reset form
        form.reset();
        
        // Reload submissions
        loadSubmissions();
        
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Submit Idea';
    } catch (error) {
        document.getElementById('singleIdeaStatus').style.display = 'block';
        document.getElementById('singleIdeaStatus').style.background = '#f8d7da';
        document.getElementById('singleIdeaStatus').style.border = '1px solid #f5c6cb';
        document.getElementById('singleIdeaStatus').style.color = '#721c24';
        document.getElementById('singleIdeaStatus').innerHTML = `
            <strong>❌ Error</strong><br>
            ${error.message || 'Failed to submit idea'}
        `;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = '🚀 Submit Idea';
    }
}

// Load All Ideas (Admin Dashboard)
async function loadAllIdeas() {
    if (!currentToken) return;
    
    try {
        document.getElementById('allIdeasLoading').style.display = 'block';
        document.getElementById('allIdeasContainer').innerHTML = '';
        
        const data = await apiCall('/api/ideas/all');
        
        document.getElementById('allIdeasLoading').style.display = 'none';
        
        if (!data.ideas || data.ideas.length === 0) {
            document.getElementById('allIdeasContainer').innerHTML = '<p style="color: #666; text-align: center; padding: 40px;">No ideas submitted yet</p>';
            return;
        }
        
        const html = data.ideas.map((idea, index) => `
            <div class="idea-card" onclick="showIdeaDetails(${index})" style="cursor: pointer;">
                <h4 style="color: #667eea; margin: 0 0 10px 0;">${escapeHtml(idea.title)}</h4>
                <p style="color: #666; margin: 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                    ${escapeHtml(idea.brief_summary)}
                </p>
                <div class="idea-meta" style="margin-top: 15px;">
                    ${idea.idea_id ? `<span>ID: ${idea.idea_id}</span>` : ''}
                    <span>📅 ${new Date(idea.created_at).toLocaleDateString()}</span>
                    ${idea.score ? `<span>⭐ ${idea.score}</span>` : ''}
                </div>
            </div>
        `).join('');
        
        document.getElementById('allIdeasContainer').innerHTML = html;
        
        // Store ideas data for modal
        window.allIdeasData = data.ideas;
        
        document.getElementById('allIdeasContainer').innerHTML = html;
    } catch (error) {
        document.getElementById('allIdeasLoading').style.display = 'none';
        document.getElementById('allIdeasContainer').innerHTML = `
            <p style="color: #f44336; text-align: center; padding: 40px;">
                ❌ Failed to load ideas: ${error.message}
            </p>
        `;
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}




// Toast Notification System
function showToast(title, message, type = 'success', duration = 5000) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            ${message ? `<div class="toast-message">${message}</div>` : ''}
        </div>
        <div class="toast-close" onclick="this.parentElement.remove()">×</div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}


// Show Idea Details Modal
function showIdeaDetails(index) {
    const idea = window.allIdeasData[index];
    if (!idea) return;
    
    const modalContent = `
        <div class="modal-header">
            <h2>${escapeHtml(idea.title)}</h2>
            <div class="modal-badges">
                ${idea.idea_id ? `<span class="modal-badge">ID: ${idea.idea_id}</span>` : ''}
                <span class="modal-badge">📅 ${new Date(idea.created_at).toLocaleDateString()}</span>
                ${idea.score ? `<span class="modal-badge">⭐ Score: ${idea.score}</span>` : ''}
            </div>
        </div>
        
        <div class="modal-section">
            <h3>📝 Brief Summary</h3>
            <p>${escapeHtml(idea.brief_summary)}</p>
        </div>
        
        ${idea.challenge_opportunity ? `
            <div class="modal-section">
                <h3>🎯 Challenge/Business Opportunity</h3>
                <p>${escapeHtml(idea.challenge_opportunity)}</p>
            </div>
        ` : ''}
        
        ${idea.novelty_benefits_risks ? `
            <div class="modal-section">
                <h3>💡 Novelty, Benefits & Risks</h3>
                <p>${escapeHtml(idea.novelty_benefits_risks)}</p>
            </div>
        ` : ''}
        
        ${idea.responsible_ai_adherence ? `
            <div class="modal-section">
                <h3>🛡️ Responsible AI Adherence</h3>
                <p>${escapeHtml(idea.responsible_ai_adherence)}</p>
            </div>
        ` : ''}
        
        ${idea.additional_documentation ? `
            <div class="modal-section">
                <h3>📄 Additional Documentation</h3>
                <p>${escapeHtml(idea.additional_documentation)}</p>
            </div>
        ` : ''}
        
        ${idea.second_file_info ? `
            <div class="modal-section">
                <h3>📎 Second File Info</h3>
                <p>${escapeHtml(idea.second_file_info)}</p>
            </div>
        ` : ''}
        
        ${(idea.preferred_week || idea.build_phase_preference || idea.build_method_preference || idea.code_development_preference) ? `
            <div class="modal-section">
                <h3>⚙️ Preferences</h3>
                ${idea.preferred_week ? `<p><strong>Week:</strong> ${escapeHtml(idea.preferred_week)}</p>` : ''}
                ${idea.build_phase_preference ? `<p><strong>Build Phase:</strong> ${escapeHtml(idea.build_phase_preference)}</p>` : ''}
                ${idea.build_method_preference ? `<p><strong>Build Method:</strong> ${escapeHtml(idea.build_method_preference)}</p>` : ''}
                ${idea.code_development_preference ? `<p><strong>Code Development:</strong> ${escapeHtml(idea.code_development_preference)}</p>` : ''}
            </div>
        ` : ''}
    `;
    
    document.getElementById('ideaModalContent').innerHTML = modalContent;
    document.getElementById('ideaModal').classList.add('show');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

// Close Idea Details Modal
function closeIdeaModal(event) {
    if (!event || event.target.id === 'ideaModal' || event.target.className === 'modal-close') {
        document.getElementById('ideaModal').classList.remove('show');
        document.body.style.overflow = 'auto'; // Restore scrolling
    }
}

// Close modal on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeIdeaModal();
    }
});
