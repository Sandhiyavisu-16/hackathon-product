# 🤖 Model Configuration Guide

## ✨ Enhanced Features

Your Model Config UI now supports complete configuration management with connection testing!

### 🎯 What's New

1. **✅ Complete Provider Settings** - All required fields for each provider
2. **🧪 Test Connection** - Verify configuration before activation
3. **🔄 Activate/Rollback** - Manage active configurations
4. **📝 Detailed Forms** - Provider-specific fields with validation
5. **🔐 Secure API Keys** - Password fields for sensitive data

## 📋 Supported Providers

### 1. Azure OpenAI

**Required Fields:**
- **Configuration Name** - Friendly name (e.g., "Production GPT-4")
- **Endpoint URL** - Your Azure resource endpoint
  - Example: `https://your-resource.openai.azure.com/`
- **API Key** - Your Azure OpenAI API key
- **Deployment Name** - Your deployment name (e.g., "gpt-4")
- **API Version** - API version (default: 2024-08-01)

**Optional Fields:**
- Temperature (0-2, default: 0.7)
- Max Tokens (1-32000, default: 2048)
- Rate Limit (requests/min, default: 120)
- Notes

### 2. Gemini (Google)

**Required Fields:**
- **Configuration Name** - Friendly name
- **Project ID** - Your GCP project ID
- **Location** - Region (e.g., "us-central1")
- **API Key** - Your Gemini API key
- **Model Name** - Model to use (e.g., "gemini-pro")

**Optional Fields:**
- Temperature, Max Tokens, Rate Limit, Notes

### 3. Gemma (Self-Hosted)

**Required Fields:**
- **Configuration Name** - Friendly name
- **Endpoint URL** - Your Gemma endpoint
- **Model ID** - Model identifier (e.g., "gemma-7b")

**Optional Fields:**
- Authentication Token (if required)
- Temperature, Max Tokens, Rate Limit, Notes

## 🚀 How to Use

### Step 1: Create Configuration

1. **Select Admin role**
2. **Go to Model Config tab**
3. **Click "➕ Create New Configuration"**
4. **Select Provider** from dropdown
5. **Fill in all required fields**
   - Form updates based on provider selection
   - Required fields marked with *
6. **Click "Create Configuration"**

### Step 2: Test Connection

1. **Find your configuration** in the history list
2. **Status shows "DRAFT"** (orange badge)
3. **Click "🧪 Test Connection"** button
4. **Wait for test results:**
   - ✅ **Success**: Shows latency and sample response
   - ❌ **Failure**: Shows error message
5. **If successful**, status changes to "TESTED" (blue badge)

### Step 3: Activate Configuration

1. **After successful test**, configuration is ready
2. **Status shows "TESTED"** (blue badge)
3. **Click "✅ Activate"** button
4. **Confirm activation**
5. **Configuration becomes active** (green badge)
6. **Previous active config** becomes inactive

## 📊 Configuration States

### Draft (🟠 Orange)
- Newly created configuration
- Not yet tested
- **Action**: Test Connection

### Tested (🔵 Blue)
- Connection test passed
- Ready to activate
- **Actions**: Activate, Re-test

### Active (🟢 Green)
- Currently in use
- Only one can be active
- **No actions** (already active)

### Inactive (⚫ Gray)
- Previously active
- Deactivated by new activation
- **Action**: Rollback & Activate

## 🧪 Test Connection Details

### What It Tests:
- ✅ Endpoint reachability
- ✅ API key validity
- ✅ Model/deployment availability
- ✅ Response time (latency)
- ✅ Sample completion

### Test Results:

**Success:**
```
✅ Connection Test Successful!
Latency: 245ms
Sample Response: This is a test...
Status: Configuration is now marked as "tested"
```

**Failure:**
```
❌ Connection Test Failed
Error: Invalid API key
Please check your configuration settings.
```

## 💡 Example Workflows

### Azure OpenAI Setup

1. **Create Configuration:**
   ```
   Name: Production GPT-4
   Provider: Azure OpenAI
   Endpoint: https://mycompany.openai.azure.com/
   API Key: sk-abc123...
   Deployment: gpt-4
   API Version: 2024-08-01
   Temperature: 0.7
   Max Tokens: 2048
   Rate Limit: 120
   ```

2. **Test Connection:**
   - Click "Test Connection"
   - Wait 2-3 seconds
   - See success message with latency

3. **Activate:**
   - Click "Activate"
   - Confirm
   - Configuration is now live!

### Gemini Setup

1. **Create Configuration:**
   ```
   Name: Gemini Pro Production
   Provider: Gemini
   Project ID: my-gcp-project
   Location: us-central1
   API Key: AIza...
   Model: gemini-pro
   Temperature: 0.8
   ```

2. **Test & Activate** (same as above)

## 🔐 Security Notes

### API Keys
- ✅ Stored securely in secrets manager
- ✅ Never displayed in UI after creation
- ✅ Password fields hide input
- ✅ Not returned in API responses

### Best Practices
- ✅ Use separate configs for dev/staging/prod
- ✅ Test before activating
- ✅ Add descriptive notes
- ✅ Monitor rate limits
- ✅ Rotate API keys regularly

## 🎨 UI Features

### Provider-Specific Forms
- Form fields change based on provider selection
- Only relevant fields shown
- Helpful placeholders and hints
- Validation before submission

### Visual Status Indicators
- Color-coded badges (Orange/Blue/Green/Gray)
- Clear action buttons
- Success/error messages
- Loading states during tests

### Smart Actions
- Test button only on draft configs
- Activate button only on tested configs
- Rollback button on inactive configs
- No actions on active config

## 🔧 Troubleshooting

### Test Connection Fails

**Azure OpenAI:**
- ✅ Check endpoint URL format
- ✅ Verify API key is correct
- ✅ Confirm deployment name exists
- ✅ Check API version is supported

**Gemini:**
- ✅ Verify project ID
- ✅ Check API key permissions
- ✅ Confirm location is valid
- ✅ Ensure model name is correct

**Gemma:**
- ✅ Check endpoint is reachable
- ✅ Verify authentication if required
- ✅ Confirm model ID is correct

### Can't Activate

**Possible Reasons:**
- ❌ Configuration not tested yet
- ❌ Test failed
- ❌ Not logged in as Admin

**Solution:**
1. Test connection first
2. Fix any errors
3. Re-test until successful
4. Then activate

### Configuration Not Showing

**Check:**
- ✅ Selected Admin role
- ✅ Refreshed the page
- ✅ Configuration was created successfully

## 📈 Advanced Features

### Multiple Configurations
- Create multiple configs for different use cases
- Switch between them easily
- Keep dev/staging/prod separate
- Test new configs without affecting active one

### Version History
- All configurations saved
- See creation dates
- Track which was active when
- Rollback to previous configs

### Configuration Notes
- Add context about each config
- Document purpose or restrictions
- Note rate limits or quotas
- Track who should use it

## 🎉 Summary

You now have complete control over your LLM configurations:

✅ **Create** - All provider types with full settings
✅ **Test** - Verify before activation
✅ **Activate** - Make live with one click
✅ **Manage** - Multiple configs, easy switching
✅ **Secure** - API keys protected
✅ **Track** - Full history and status

Start by creating your first configuration and testing it! 🚀
