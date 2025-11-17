# 🎨 UI Guide - How to Use the Web Interface

## 🚀 Quick Start

### Step 1: Install the New Dependency

```bash
npm install
```

### Step 2: Start the Server

```bash
npm run dev
```

### Step 3: Open Your Browser

Go to: **http://localhost:3000**

You should see a beautiful purple gradient interface! 🎉

## 📖 Using the UI

### 1. Select Your Role

First, click one of the role buttons:

- **👑 Admin** - Full access to everything
- **📖 Editor** - Read-only access
- **✍️ Contributor** - Can submit ideas

This sets your authentication token automatically.

### 2. View Rubrics

Click the **📊 Rubrics** tab to see:
- All 5 default rubrics
- Their weights (should total 100%)
- Descriptions and guidance
- Active/Default badges

### 3. Manage Model Configurations

Click the **🤖 Model Config** tab to:
- View active configuration
- See configuration history
- Create new configurations (as Admin)

**To create a new config:**
1. Click "➕ Create New Configuration"
2. Fill in the form:
   - Provider (Azure OpenAI, Gemini, or Gemma)
   - Configuration name
   - Endpoint URL
   - Deployment/Model name
3. Click "Create Configuration"

### 4. Submit Ideas

Click the **💡 Submit Ideas** tab to:
- Download the CSV template
- Upload your ideas CSV file

**To submit ideas:**
1. Click "📥 Download CSV Template"
2. Fill in the template with your ideas
3. Click the upload zone to select your CSV
4. File will be validated and processed

## 🎨 UI Features

### Real-Time API Status
- Green dot = API is running
- Red dot = API is offline
- Updates every 5 seconds

### Role-Based Access
- Different roles see different features
- Admin can create configurations
- Contributors can submit ideas
- Editors can only view

### Visual Feedback
- Success messages (green)
- Error messages (red)
- Loading indicators
- Hover effects on buttons

### Responsive Design
- Works on desktop and tablet
- Clean, modern interface
- Easy to navigate

## 🔧 Troubleshooting

### "API Offline" Message

**Solution:** Make sure the server is running
```bash
npm run dev
```

### Can't See Rubrics

**Solution:** Select a role first (click one of the role buttons)

### Create Configuration Button Doesn't Work

**Solution:** Make sure you're logged in as Admin

### File Upload Not Working

**Solution:** 
- Make sure you selected a role first
- Currently shows UI flow (full S3 integration needed for production)

## 🎯 What Works Right Now

✅ **Fully Functional:**
- Role selection and authentication
- View all rubrics with weights
- View model configurations
- Create new model configurations
- Download CSV template
- Beautiful, responsive UI

⚠️ **Demo Mode:**
- File upload (shows UI, needs S3 for full functionality)
- Some advanced features

## 📱 Screenshots

### Home Screen
- Purple gradient background
- Three role selection buttons
- Clean, modern design

### Rubrics Tab
- Weight total indicator (green if 100%, red if not)
- List of all rubrics with badges
- Descriptions and guidance

### Model Config Tab
- Active configuration highlighted in green
- Configuration history
- Create new configuration form

### Ideas Tab
- Download template button
- Drag-and-drop upload zone
- Upload status display

## 🚀 Next Steps

1. **Start the server:** `npm run dev`
2. **Open browser:** http://localhost:3000
3. **Select a role:** Click Admin, Editor, or Contributor
4. **Explore the tabs:** Try viewing rubrics and creating configs

## 💡 Tips

- **Use Admin role** to see all features
- **Refresh the page** if data doesn't load
- **Check the console** (F12) for detailed error messages
- **API status indicator** shows if backend is running

## 🎉 Enjoy!

You now have a fully functional web UI for your platform! The interface is clean, modern, and easy to use. Start exploring and managing your configurations! 🚀

---

**Need help?** Check that:
1. Server is running (`npm run dev`)
2. You selected a role
3. Browser is at http://localhost:3000
