# 🤖 Gemini API Setup Guide

## ✨ What's Fixed

Gemini now supports **both API options**:
1. **Google AI Studio API** (Simpler) - Works with `gemini-2.0-flash-exp`, `gemini-1.5-flash`, etc.
2. **Vertex AI API** (Advanced) - For GCP enterprise users

## 🎯 Two Ways to Use Gemini

### Option 1: Google AI Studio (Recommended for Most Users)

**Best for:**
- Individual developers
- Quick prototyping
- Models like `gemini-2.0-flash-exp`, `gemini-1.5-flash`, `gemini-pro`

**What you need:**
- ✅ API Key from Google AI Studio
- ✅ Model name

**Steps:**

1. **Get API Key:**
   - Go to https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy your key (starts with `AIzaSy...`)

2. **Create Configuration:**
   ```
   Name: Gemini Flash
   Provider: gemini
   API Key: AIzaSy... (your key)
   Model: gemini-2.0-flash-exp
   Temperature: 0.7
   Max Tokens: 2048
   Rate Limit: 60
   ```

3. **Leave these empty:**
   - Project ID (not needed)
   - Location (not needed)

4. **Test Connection** - Should work immediately!

### Option 2: Vertex AI (Advanced)

**Best for:**
- Enterprise GCP users
- Need VPC/private networking
- Require GCP IAM controls

**What you need:**
- ✅ GCP Project ID
- ✅ Location (region)
- ✅ OAuth Bearer Token
- ✅ Model name

**Steps:**

1. **Enable Vertex AI:**
   - Go to GCP Console
   - Enable Vertex AI API
   - Set up authentication

2. **Get Bearer Token:**
   ```bash
   gcloud auth print-access-token
   ```

3. **Create Configuration:**
   ```
   Name: Gemini Vertex
   Provider: gemini
   API Key: ya29... (Bearer token)
   Model: gemini-pro
   Project ID: your-gcp-project-123
   Location: us-central1
   Temperature: 0.7
   Max Tokens: 2048
   Rate Limit: 60
   ```

4. **Test Connection**

## 📋 Available Models

### Google AI Studio Models:
- `gemini-2.5-flash` - Latest Gemini 2.5 Flash model ⭐
- `gemini-2.0-flash-exp` - Gemini 2.0 experimental flash model
- `gemini-1.5-flash` - Fast, efficient Gemini 1.5 model
- `gemini-1.5-pro` - More capable Gemini 1.5 model
- `gemini-pro` - Original Gemini Pro

### Vertex AI Models:
- `gemini-pro`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- Check GCP docs for latest available models

## 🚀 Quick Start Example

### Using gemini-2.0-flash-exp:

1. **Get API Key:**
   - Visit: https://aistudio.google.com/app/apikey
   - Create API key

2. **Configure:**
   ```
   Name: Gemini 2.0 Flash
   Provider: gemini
   API Key: [Your API key from AI Studio]
   Model: gemini-2.0-flash-exp
   Temperature: 0.7
   Max Tokens: 2048
   Rate Limit: 60
   
   [Leave Project ID and Location empty]
   ```

3. **Test:**
   - Click "🧪 Test Connection"
   - Should see: ✅ Connection successful!

4. **Activate:**
   - Click "✅ Activate"
   - Ready to use!

## 🔍 How It Works

### API Detection:
The adapter automatically detects which API to use:

```typescript
// If Project ID + Location provided → Use Vertex AI
if (settings.project_id && settings.location) {
    useVertexAI = true;
}

// Otherwise → Use Google AI Studio API
else {
    useGenerativeLanguageAPI = true;
}
```

### Google AI Studio API:
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}
```

### Vertex AI API:
```
POST https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent
Authorization: Bearer {token}
```

## ⚠️ Common Issues

### Issue 1: "Invalid API key"
**Cause:** Wrong API key or not from Google AI Studio
**Solution:** 
- Get key from https://aistudio.google.com/app/apikey
- Make sure it starts with `AIzaSy...`
- Don't use GCP service account keys

### Issue 2: "Model not found"
**Cause:** Model name incorrect or not available
**Solution:**
- For AI Studio: Use `gemini-2.0-flash-exp`, `gemini-1.5-flash`, or `gemini-pro`
- Check spelling and case sensitivity
- Try `gemini-pro` as a fallback

### Issue 3: "API key invalid or Gemini API not enabled"
**Cause:** Gemini API not enabled in your Google Cloud project
**Solution:**
- Go to https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
- Click "Enable"

### Issue 4: "Invalid Bearer token" (Vertex AI)
**Cause:** OAuth token expired or invalid
**Solution:**
- Regenerate token: `gcloud auth print-access-token`
- Tokens expire after ~1 hour
- Consider using service account for production

## 🔐 Security Notes

### API Key Storage:
- ✅ Keys stored securely in secrets manager
- ✅ Never logged or displayed
- ✅ Redacted in API responses
- ✅ Transmitted over HTTPS only

### Best Practices:
- **Don't commit API keys** to version control
- **Rotate keys regularly** in production
- **Use environment variables** for keys
- **Monitor usage** in Google AI Studio dashboard

## 💡 Tips

### For Development:
- **Start with Google AI Studio** - It's simpler
- **Use gemini-2.0-flash-exp** - Latest and fastest
- **Test with low rate limits** first
- **Monitor quota** in AI Studio dashboard

### For Production:
- **Consider Vertex AI** for enterprise features
- **Set appropriate rate limits** based on quota
- **Monitor costs** in GCP billing
- **Use service accounts** for authentication
- **Enable logging** for debugging

## 📊 Comparison

| Feature | Google AI Studio | Vertex AI |
|---------|-----------------|-----------|
| **Setup** | Very Easy | Complex |
| **Auth** | API Key | OAuth Token |
| **Cost** | Free tier available | Pay per use |
| **Models** | Latest experimental | Stable releases |
| **Networking** | Public internet | VPC support |
| **IAM** | Basic | Full GCP IAM |
| **Best for** | Development, prototyping | Enterprise, production |

## 🧪 Testing Your Setup

### Test 1: Basic Connection
1. Create config with API key + model
2. Click "Test Connection"
3. Should see: ✅ Success with sample response

### Test 2: Different Models
Try these models to verify they work:
- `gemini-2.0-flash-exp`
- `gemini-1.5-flash`
- `gemini-pro`

### Test 3: Invalid Key
1. Use wrong API key
2. Should see: ❌ "Invalid API key"
3. Confirms error handling works

### Test 4: Wrong Model
1. Use non-existent model name
2. Should see: ❌ "Model not found"
3. Shows helpful model suggestions

## 🎉 Benefits

### Before:
- ❌ Only supported Vertex AI
- ❌ Required GCP project setup
- ❌ Complex authentication
- ❌ Didn't work with `gemini-2.0-flash-exp`

### Now:
- ✅ **Supports both APIs**
- ✅ **Simple API key option**
- ✅ **Works with latest models**
- ✅ **Automatic API detection**
- ✅ **Better error messages**
- ✅ **Flexible configuration**

## 🔗 Useful Links

- **Get API Key:** https://aistudio.google.com/app/apikey
- **Model Documentation:** https://ai.google.dev/models/gemini
- **Vertex AI Docs:** https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini
- **Pricing:** https://ai.google.dev/pricing
- **API Reference:** https://ai.google.dev/api/rest

## 🎯 Next Steps

1. **Get your API key** from Google AI Studio
2. **Create a configuration** with `gemini-2.0-flash-exp`
3. **Test the connection**
4. **Start using Gemini** in your application!

Your Gemini integration now works with the latest models! 🚀
