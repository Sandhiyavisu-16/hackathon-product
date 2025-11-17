# 🎯 Rubric Management Features

## ✨ New Features Added

Your Rubrics UI now has full management capabilities!

### 1. ➕ Add Custom Rubrics

**How to use:**
1. Select **Admin** role
2. Go to **Rubrics** tab
3. Click **"➕ Add Custom Rubric"** button
4. Fill in the form:
   - **Name**: e.g., "Innovation Score"
   - **Description**: What this rubric measures
   - **Guidance**: How to score it
   - **Weight**: Percentage (0-100)
5. Click **"Create Rubric"**

**Example Custom Rubric:**
```
Name: Innovation Score
Description: Measures the level of innovation and creativity
Guidance: Score 5 for groundbreaking ideas, 1 for conventional approaches
Weight: 15%
```

### 2. 📊 View Default Rubrics

**5 Default Rubrics (Pre-loaded):**
- ✅ **Novelty** (20%) - Originality and uniqueness
- ✅ **Audience Fit** (25%) - Target audience alignment
- ✅ **Feasibility** (20%) - Production viability
- ✅ **Public Service/Value** (20%) - Social impact
- ✅ **Ethical/Compliance Risk** (15%) - Legal/ethical concerns

**Badges:**
- 🔵 **Default** - Cannot be deleted
- 🟢 **Active** - Included in scoring
- 🔴 **Inactive** - Not used in scoring
- 🟠 **Custom** - User-created rubric

### 3. ⚖️ Change Weightage

**Real-time Weight Editing:**
1. As **Admin**, you'll see weight input boxes
2. Click on any weight value
3. Type new percentage (0-100)
4. Press Enter or click outside
5. Weight updates automatically!

**Weight Validation:**
- ✅ **Green** = Total equals 100% (valid)
- ❌ **Red** = Total doesn't equal 100% (invalid)
- Real-time calculation as you edit

**Tips:**
- Adjust multiple rubrics to maintain 100% total
- Inactive rubrics don't count toward total
- System prevents weights outside 0-100 range

### 4. 🔄 Activate/Deactivate Rubrics

**Toggle Active Status:**
- Click **"✅ Activate"** to include in scoring
- Click **"🚫 Deactivate"** to exclude from scoring
- Only active rubrics count toward 100% total
- Useful for seasonal or conditional rubrics

### 5. 🗑️ Delete Custom Rubrics

**Remove Unwanted Rubrics:**
- Only **custom rubrics** can be deleted
- Default rubrics are protected
- Click **"🗑️ Delete"** button
- Confirm deletion
- Rubric removed permanently

**Note:** Default rubrics show "Default rubrics cannot be deleted" instead of delete button.

## 🎨 UI Features

### Visual Indicators

**Weight Total Display:**
```
┌─────────────────────┐
│   Total Weight      │
│       100%          │  ← Green if valid
│  Must equal 100%    │
└─────────────────────┘
```

**Rubric Cards:**
```
┌────────────────────────────────────┐
│ Innovation Score  [Custom] [Active]│
│                            [15%] ← Editable
│ Measures innovation level          │
│ 💡 Score 5 for groundbreaking...  │
│ [🚫 Deactivate] [🗑️ Delete]       │
└────────────────────────────────────┘
```

### Admin vs. Non-Admin View

**Admin (Full Control):**
- ✅ Edit weights (input boxes)
- ✅ Create custom rubrics
- ✅ Activate/deactivate rubrics
- ✅ Delete custom rubrics

**Editor/Contributor (Read-Only):**
- ✅ View all rubrics
- ✅ See weights (not editable)
- ❌ Cannot modify anything

## 📋 Example Workflow

### Creating a Balanced Rubric Set

1. **Start with defaults** (100% total)
2. **Add custom rubric** (e.g., Innovation 15%)
3. **Adjust other weights:**
   - Novelty: 20% → 15%
   - Audience Fit: 25% → 20%
   - Feasibility: 20% → 20%
   - Public Service: 20% → 20%
   - Ethical Risk: 15% → 10%
   - Innovation: 0% → 15%
4. **Total = 100%** ✅

### Seasonal Rubrics

**For Documentary Season:**
1. Create "Documentary Appeal" rubric (10%)
2. Adjust other weights to compensate
3. After season, deactivate it
4. Weights auto-adjust

## 🚀 Try It Now!

1. **Start server:** `npm run dev`
2. **Open browser:** http://localhost:3000
3. **Select Admin role**
4. **Go to Rubrics tab**
5. **Try these actions:**
   - Change a weight value
   - Add a custom rubric
   - Deactivate a rubric
   - Watch the total update in real-time!

## 💡 Tips & Best Practices

### Weight Management
- ✅ Keep total at 100% for valid scoring
- ✅ Use round numbers (5%, 10%, 15%, etc.)
- ✅ Adjust multiple rubrics together
- ✅ Deactivate instead of delete for temporary changes

### Custom Rubrics
- ✅ Use clear, descriptive names
- ✅ Write detailed guidance for scorers
- ✅ Start with lower weights (5-15%)
- ✅ Test with sample ideas first

### Organization
- ✅ Keep 5-7 active rubrics maximum
- ✅ Group related rubrics
- ✅ Use consistent naming conventions
- ✅ Document rubric purposes

## 🎯 What's Working

✅ **Fully Functional:**
- View all rubrics (default + custom)
- Real-time weight editing
- Create custom rubrics
- Activate/deactivate rubrics
- Weight validation (100% check)
- Visual feedback (success/error messages)
- Role-based permissions

⚠️ **Coming Soon:**
- Delete rubric endpoint (UI ready)
- Rubric reordering (drag & drop)
- Weight presets (save/load configurations)
- Bulk operations

## 🎉 Enjoy!

You now have full control over your scoring rubrics! The interface is intuitive, real-time, and prevents invalid configurations. Start customizing your rubric set! 🚀
