# 📄 CSV Format Guide for Idea Submission

## 📋 Required Columns

Your CSV file must include these **8 columns** in this exact order:

| Column | Required | Max Length | Description |
|--------|----------|------------|-------------|
| `title` | ✅ Yes | 120 chars | The title of your idea |
| `logline` | ✅ Yes | 300 chars | Short description/pitch |
| `genre` | ✅ Yes | 40 chars | Genre or category |
| `target_audience` | ✅ Yes | 100 chars | Target demographic |
| `duration_or_format` | ✅ Yes | 50 chars | Duration or format |
| `submitter_email` | ✅ Yes | 255 chars | Contact email |
| `reference_urls` | ❌ No | - | Reference links (optional) |
| `notes` | ❌ No | - | Additional notes (optional) |

## 📝 Column Details

### 1. title (Required)
**What:** The title of your idea
**Max Length:** 120 characters
**Examples:**
- "The Last Sunset"
- "Space Odyssey 2050"
- "Love in Paris"

### 2. logline (Required)
**What:** A short, compelling description of your idea (like a movie pitch)
**Max Length:** 300 characters
**Examples:**
- "A detective races against time to solve a murder case before retiring, uncovering a conspiracy that spans decades."
- "Two strangers meet in Paris and fall in love over a weekend, but must return to their separate lives."

**Tips:**
- Keep it concise and engaging
- Include the main conflict or hook
- Make it compelling

### 3. genre (Required)
**What:** The genre or category of your idea
**Max Length:** 40 characters
**Examples:**
- "Mystery Thriller"
- "Romantic Comedy"
- "Science Fiction"
- "Horror"
- "Fantasy Adventure"
- "Action Drama"

### 4. target_audience (Required)
**What:** Who is this idea for?
**Max Length:** 100 characters
**Examples:**
- "Adults 25-54"
- "Teens & Adults 13-35"
- "Adults 18-45"
- "Family (All Ages)"
- "Young Adults 18-30"

### 5. duration_or_format (Required)
**What:** How long or what format
**Max Length:** 50 characters
**Examples:**
- "90 minutes" (for films)
- "60 minutes" (for TV episodes)
- "8 episodes x 45 minutes" (for series)
- "Feature film"
- "Limited series"

### 6. submitter_email (Required)
**What:** Your contact email
**Max Length:** 255 characters
**Format:** Must be valid email (name@domain.com)
**Examples:**
- "john.doe@example.com"
- "jane.smith@company.com"

**Note:** This email will be used to notify you about your submission status

### 7. reference_urls (Optional)
**What:** Links to reference materials, inspiration, or similar works
**Format:** URLs separated by semicolons if multiple
**Examples:**
- "https://example.com/reference1"
- "https://imdb.com/title/tt1234567"
- "https://example.com/ref1;https://example.com/ref2"

**Leave empty if none**

### 8. notes (Optional)
**What:** Any additional notes or context
**Examples:**
- "Inspired by classic noir films"
- "Hard sci-fi with realistic space travel"
- "Light-hearted romantic comedy"
- "Epic fantasy trilogy potential"

**Leave empty if none**

## 📄 Sample CSV File

Here's what your CSV should look like:

```csv
title,logline,genre,target_audience,duration_or_format,submitter_email,reference_urls,notes
The Last Sunset,"A detective races against time to solve a murder case before retiring, uncovering a conspiracy that spans decades.",Mystery Thriller,Adults 25-54,90 minutes,john.doe@example.com,https://example.com/reference1,Inspired by classic noir films
Space Odyssey 2050,"In the year 2050, a crew of astronauts discovers an ancient alien artifact that could change humanity's future forever.",Science Fiction,Adults 18-45,120 minutes,jane.smith@example.com,https://example.com/reference2,Hard sci-fi with realistic space travel
Love in Paris,"Two strangers meet in Paris and fall in love over a weekend, but must return to their separate lives in different countries.",Romantic Comedy,Adults 20-40,95 minutes,mike.johnson@example.com,,Light-hearted romantic comedy
```

## ✅ CSV Formatting Rules

### 1. Header Row
- **First row must be the header** with column names
- Use exact column names (case-sensitive)
- No extra spaces

### 2. Commas
- Columns are separated by commas
- If your text contains commas, wrap it in quotes

### 3. Quotes
- Use double quotes (`"`) for text with commas
- Example: `"A story about love, loss, and redemption"`

### 4. Line Breaks
- Each idea is one row
- No line breaks within a cell
- Use `\n` if you need line breaks in text

### 5. Empty Columns
- Optional columns can be empty
- Just use comma with nothing between
- Example: `...,john@example.com,,Some notes`

### 6. Special Characters
- Avoid special characters like `|`, `~`, `^`
- Use standard punctuation (`.`, `,`, `!`, `?`)
- Emojis are okay but not recommended

## 🚫 Common Mistakes

### ❌ Wrong: Missing header row
```csv
The Last Sunset,A detective races...,Mystery,Adults 25-54,...
```

### ✅ Right: Has header row
```csv
title,logline,genre,target_audience,duration_or_format,submitter_email,reference_urls,notes
The Last Sunset,A detective races...,Mystery,Adults 25-54,...
```

---

### ❌ Wrong: Unquoted text with commas
```csv
title,logline
My Idea,A story about love, loss, and redemption
```

### ✅ Right: Quoted text with commas
```csv
title,logline
My Idea,"A story about love, loss, and redemption"
```

---

### ❌ Wrong: Wrong column order
```csv
logline,title,genre,...
```

### ✅ Right: Correct column order
```csv
title,logline,genre,...
```

---

### ❌ Wrong: Missing required columns
```csv
title,logline,genre
```

### ✅ Right: All 8 columns present
```csv
title,logline,genre,target_audience,duration_or_format,submitter_email,reference_urls,notes
```

## 📥 Download Template

You can download a pre-formatted template:

1. Go to the Ideas tab
2. Click "📥 Download CSV Template"
3. Open in Excel, Google Sheets, or any spreadsheet app
4. Fill in your ideas
5. Save as CSV
6. Upload!

**Template file:** `ideas_template.csv`

## 🔧 Creating Your CSV

### Option 1: Use Excel/Google Sheets
1. Open Excel or Google Sheets
2. Create columns with the header names
3. Fill in your ideas (one per row)
4. Save as CSV format
   - Excel: File → Save As → CSV (Comma delimited)
   - Google Sheets: File → Download → CSV

### Option 2: Use Text Editor
1. Open Notepad or any text editor
2. Copy the header row:
   ```
   title,logline,genre,target_audience,duration_or_format,submitter_email,reference_urls,notes
   ```
3. Add your ideas (one per line)
4. Save with `.csv` extension

### Option 3: Download and Edit Template
1. Download `ideas_template.csv`
2. Open in your preferred app
3. Replace sample data with your ideas
4. Save

## ✅ Validation Checklist

Before uploading, check:

- [ ] File is saved as `.csv` format
- [ ] First row has all 8 column headers
- [ ] Column headers are spelled correctly
- [ ] All required columns have data
- [ ] Email addresses are valid format
- [ ] Text with commas is in quotes
- [ ] No extra blank rows at the end
- [ ] File size is reasonable (< 10MB)

## 📊 Example Ideas

### Idea 1: Film
```csv
The Last Sunset,"A detective races against time to solve a murder case before retiring, uncovering a conspiracy that spans decades.",Mystery Thriller,Adults 25-54,90 minutes,john.doe@example.com,https://example.com/reference1,Inspired by classic noir films
```

### Idea 2: TV Series
```csv
The Heist,"A team of expert thieves plans the ultimate heist to steal a priceless artifact from an impenetrable museum.",Action Thriller,Adults 18-45,8 episodes x 60 minutes,emily.davis@example.com,,Ocean's Eleven meets Mission Impossible
```

### Idea 3: Documentary
```csv
Ocean Mysteries,"Exploring the deepest parts of the ocean to discover new species and underwater phenomena.",Documentary,Adults 25-65,90 minutes,sarah.williams@example.com,https://example.com/ocean-research,Educational nature documentary
```

## 🎯 Tips for Great Ideas

### Title:
- Keep it short and memorable
- Make it intriguing
- Avoid generic names

### Logline:
- Start with the protagonist
- Include the main conflict
- Hint at what's at stake
- Keep it under 300 characters

### Genre:
- Be specific (not just "Drama")
- Can combine genres ("Sci-Fi Thriller")
- Match industry standards

### Target Audience:
- Be realistic about demographics
- Consider age ranges
- Think about who would watch

### Duration/Format:
- Be specific about length
- Indicate if it's a series or film
- Include episode count for series

## 🚀 Ready to Submit?

1. **Create your CSV** using the template or format above
2. **Validate** using the checklist
3. **Go to Ideas tab** in the app
4. **Upload your CSV**
5. **(Optional) Add support file** (PDF, video, etc.)
6. **Enter your email**
7. **Click Submit!**

## 📞 Need Help?

If you have questions about the CSV format:
- Check the sample file: `ideas_template.csv`
- Review this guide
- Make sure all required columns are present
- Verify your email format is correct

Good luck with your submissions! 🎬
