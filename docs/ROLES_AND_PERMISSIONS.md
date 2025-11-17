# 👥 Roles and Permissions Guide

## 🎯 Quick Fix for "Insufficient Permissions"

**Problem:** Getting "Insufficient permissions" when uploading CSV?

**Solution:** Make sure you've selected a role! Click one of the role buttons at the top:
- **Admin** (recommended - has all permissions)
- **Editor** (can submit ideas)
- **Contributor** (can submit ideas)

---

## 👥 Available Roles

### 1. Admin 🔑
**Full access to everything**

**Can do:**
- ✅ Configure AI models
- ✅ Manage rubrics (create, edit, activate, deactivate)
- ✅ Submit ideas
- ✅ View all submissions
- ✅ Access all features

**Use when:**
- Setting up the system
- Managing configurations
- Full administrative access needed

---

### 2. Editor ✏️
**Can view and submit, but not configure**

**Can do:**
- ✅ View model configurations (read-only)
- ✅ View rubrics (read-only)
- ✅ Submit ideas
- ✅ View submissions

**Cannot do:**
- ❌ Create/edit model configurations
- ❌ Create/edit rubrics

**Use when:**
- Reviewing ideas
- Submitting ideas
- Don't need admin access

---

### 3. Contributor 📝
**Can only submit and view ideas**

**Can do:**
- ✅ Submit ideas
- ✅ View own submissions

**Cannot do:**
- ❌ View/edit model configurations
- ❌ View/edit rubrics
- ❌ View other users' submissions

**Use when:**
- Just submitting ideas
- Don't need access to configurations

---

## 📋 Permission Matrix

| Feature | Admin | Editor | Contributor |
|---------|-------|--------|-------------|
| **Model Config** |
| View configurations | ✅ | ✅ | ❌ |
| Create/edit configurations | ✅ | ❌ | ❌ |
| Test connections | ✅ | ❌ | ❌ |
| Activate configurations | ✅ | ❌ | ❌ |
| **Rubrics** |
| View rubrics | ✅ | ✅ | ❌ |
| Create custom rubrics | ✅ | ❌ | ❌ |
| Edit rubric weights | ✅ | ❌ | ❌ |
| Activate/deactivate rubrics | ✅ | ❌ | ❌ |
| **Ideas** |
| Submit ideas | ✅ | ✅ | ✅ |
| View own submissions | ✅ | ✅ | ✅ |
| View all submissions | ✅ | ✅ | ❌ |

---

## 🔐 How Authentication Works

### Mock Authentication (Current)
The app uses simple token-based authentication for demo purposes:

**Tokens:**
- `admin-token` → Admin role
- `editor-token` → Editor role
- `contributor-token` → Contributor role

**How it works:**
1. You select a role (Admin, Editor, or Contributor)
2. Frontend sends requests with `Bearer {role}-token`
3. Backend checks the token and assigns permissions
4. Routes verify you have required permissions

### In Production
You would replace this with:
- Real JWT tokens
- User authentication (login/password)
- Database-backed user management
- OAuth/SSO integration

---

## 🚀 How to Select a Role

### Step 1: Open the App
```
http://localhost:3000
```

### Step 2: Select a Role
At the top of the page, you'll see three buttons:
```
┌─────────┐ ┌─────────┐ ┌─────────────┐
│  Admin  │ │ Editor  │ │ Contributor │
└─────────┘ └─────────┘ └─────────────┘
```

### Step 3: Click Your Role
- Click **Admin** for full access
- Click **Editor** to submit ideas
- Click **Contributor** to just submit ideas

### Step 4: See Confirmation
You'll see:
```
Logged in as: ADMIN
Token: Bearer admin-token
```

---

## ❓ Common Issues

### Issue 1: "Insufficient permissions"
**Cause:** You haven't selected a role, or selected wrong role

**Solution:**
1. Look at the top of the page
2. Click one of the role buttons
3. Make sure you see "Logged in as: [ROLE]"
4. Try your action again

---

### Issue 2: "Missing or invalid authorization header"
**Cause:** No role selected

**Solution:**
1. Select a role (Admin, Editor, or Contributor)
2. The app will automatically add the auth header

---

### Issue 3: Can't see Model Config tab
**Cause:** Selected Contributor role (doesn't have access)

**Solution:**
1. Click "Admin" or "Editor" role
2. Model Config tab will appear

---

### Issue 4: Can't edit rubrics
**Cause:** Selected Editor or Contributor role

**Solution:**
1. Click "Admin" role
2. Now you can edit rubrics

---

## 🎯 Recommended Roles for Tasks

### Setting Up the System
**Use:** Admin
**Why:** Need to configure models and rubrics

### Submitting Ideas
**Use:** Any role (Admin, Editor, or Contributor)
**Why:** All roles can submit ideas

### Reviewing Submissions
**Use:** Admin or Editor
**Why:** Can view all submissions

### Testing Features
**Use:** Admin
**Why:** Full access to test everything

---

## 🔧 Technical Details

### Permission Enum
```typescript
enum Permission {
  MODEL_CONFIG_READ = 'model_config:read',
  MODEL_CONFIG_WRITE = 'model_config:write',
  RUBRIC_READ = 'rubric:read',
  RUBRIC_WRITE = 'rubric:write',
  IDEA_READ = 'idea:read',
  IDEA_SUBMIT = 'idea:submit',
}
```

### Role Permissions Mapping
```typescript
{
  ADMIN: [
    'model_config:read',
    'model_config:write',
    'rubric:read',
    'rubric:write',
    'idea:read',
    'idea:submit'
  ],
  EDITOR: [
    'model_config:read',
    'rubric:read',
    'idea:read',
    'idea:submit'
  ],
  CONTRIBUTOR: [
    'idea:submit',
    'idea:read'
  ]
}
```

### Route Protection
```typescript
// Example: Idea submission route
fastify.post('/api/ideas/submit', {
  preHandler: [
    authenticateJWT,              // Check if user is logged in
    requirePermission(IDEA_SUBMIT) // Check if user can submit
  ]
})
```

---

## 🎉 Summary

**To submit ideas:**
1. ✅ Select any role (Admin, Editor, or Contributor)
2. ✅ Go to Ideas tab
3. ✅ Upload CSV + support file
4. ✅ Enter email
5. ✅ Click Submit!

**Recommended:** Use **Admin** role for testing - it has all permissions!

---

## 💡 Quick Tip

**Always select a role first!**

Look for this at the top of the page:
```
┌─────────────────────────────────────┐
│ Select Your Role:                   │
│ [Admin] [Editor] [Contributor]      │
└─────────────────────────────────────┘
```

If you don't see "Logged in as: [ROLE]", click a role button!

That's it! 🚀
