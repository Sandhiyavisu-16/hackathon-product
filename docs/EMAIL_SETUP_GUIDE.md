# 📧 Email Notifications Setup Guide

## 🎯 Current Status

**Right now:** Emails are just logged to console
```
Email notification would be sent to: user@example.com
```

**To actually send emails**, you need to configure an email service.

---

## 📋 Email Service Options

### Option 1: Gmail (Easiest for Testing)
**Cost:** Free
**Best for:** Development/testing
**Limit:** 500 emails/day

### Option 2: SendGrid
**Cost:** Free tier (100 emails/day)
**Best for:** Production
**Limit:** 100/day free, then paid

### Option 3: AWS SES
**Cost:** $0.10 per 1,000 emails
**Best for:** Production at scale
**Limit:** No free tier, but very cheap

### Option 4: Mailgun
**Cost:** Free tier (5,000 emails/month)
**Best for:** Production
**Limit:** 5,000/month free

---

## 🚀 Quick Setup: Gmail (For Testing)

### Step 1: Enable Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Security → 2-Step Verification (enable if not already)
3. Security → App passwords
4. Generate app password for "Mail"
5. Copy the 16-character password

### Step 2: Add to .env File

```env
# Email Configuration
EMAIL_SERVICE=gmail
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_FROM=your.email@gmail.com
EMAIL_FROM_NAME=Idea Submission Platform
```

### Step 3: Install Nodemailer

```bash
npm install nodemailer
npm install --save-dev @types/nodemailer
```

### Step 4: Restart Server

```bash
npm run build
npm run dev
```

### Step 5: Test!

Upload a CSV and check your email! 📧

---

## 🚀 Production Setup: SendGrid

### Step 1: Create SendGrid Account

1. Go to https://sendgrid.com/
2. Sign up for free account
3. Verify your email
4. Create API key

### Step 2: Get API Key

1. Settings → API Keys
2. Create API Key
3. Give it "Full Access"
4. Copy the API key

### Step 3: Add to .env File

```env
# Email Configuration
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=SG.your-api-key-here
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=Idea Submission Platform
```

### Step 4: Install SendGrid

```bash
npm install @sendgrid/mail
```

### Step 5: Verify Sender

1. SendGrid → Settings → Sender Authentication
2. Verify your email or domain
3. Must verify before sending emails

---

## 📝 What Emails Are Sent

### 1. Submission Received
**When:** Immediately after CSV upload
**To:** Submitter email
**Subject:** "Your Ideas Have Been Received"
**Content:**
- Submission ID
- Number of ideas submitted
- What happens next

### 2. Validation Complete
**When:** After CSV validation
**To:** Submitter email
**Subject:** "Your Ideas Have Been Validated"
**Content:**
- Total ideas
- Valid ideas
- Invalid ideas (if any)
- Next steps

### 3. Scoring Complete (Future)
**When:** After AI scoring
**To:** Submitter email
**Subject:** "Your Ideas Have Been Scored"
**Content:**
- Scores for each idea
- Rankings
- Feedback

---

## 🔧 Implementation

I'll create the email service for you. The code will:

1. ✅ Check if email is configured
2. ✅ Use Gmail or SendGrid based on config
3. ✅ Send HTML emails
4. ✅ Handle errors gracefully
5. ✅ Log to console if email fails

---

## ⚠️ Important Notes

### Gmail Limitations:
- **500 emails/day limit**
- **Not recommended for production**
- **Good for testing only**
- **May be marked as spam**

### SendGrid Benefits:
- **Reliable delivery**
- **Better spam scores**
- **Email analytics**
- **Professional**

### For Production:
- **Use SendGrid or AWS SES**
- **Verify your domain**
- **Set up SPF/DKIM records**
- **Monitor bounce rates**

---

## 🧪 Testing Email

### Test 1: Check Configuration
```bash
# Check .env file has email settings
cat .env | grep EMAIL
```

### Test 2: Submit Ideas
1. Upload CSV
2. Check server logs for "Email sent to..."
3. Check your inbox
4. Check spam folder if not in inbox

### Test 3: Check Errors
If email fails, check logs for:
```
Error sending email: [error message]
```

---

## 🔍 Troubleshooting

### "Invalid login" (Gmail)
- **Cause:** Wrong password or not using app password
- **Fix:** Generate new app password, use that

### "Sender not verified" (SendGrid)
- **Cause:** Email not verified in SendGrid
- **Fix:** Verify sender email in SendGrid dashboard

### "Connection timeout"
- **Cause:** Firewall blocking SMTP
- **Fix:** Check firewall, try different network

### Emails go to spam
- **Cause:** No SPF/DKIM records
- **Fix:** Set up domain authentication

### No error but no email
- **Cause:** Email service not configured
- **Fix:** Check .env file has all required fields

---

## 📊 Email Templates

### Submission Received Email:
```
Subject: Your Ideas Have Been Received ✅

Hi there!

We've received your idea submission!

Submission Details:
- Submission ID: abc-123-def-456
- Total Ideas: 10
- Status: Processing

We're now validating your ideas. You'll receive another email once validation is complete.

Thank you for your submission!

Best regards,
Idea Submission Platform
```

### Validation Complete Email:
```
Subject: Your Ideas Have Been Validated ✅

Hi there!

Your ideas have been validated!

Results:
- Total Ideas: 10
- Valid Ideas: 9 ✅
- Invalid Ideas: 1 ❌

Your valid ideas are now queued for scoring. We'll notify you once scoring is complete.

View your submission: [link]

Best regards,
Idea Submission Platform
```

---

## 🎯 Quick Start

**For Testing (Gmail):**
1. Get Gmail app password
2. Add to .env file
3. Install nodemailer
4. Restart server
5. Test!

**For Production (SendGrid):**
1. Create SendGrid account
2. Get API key
3. Verify sender email
4. Add to .env file
5. Install @sendgrid/mail
6. Restart server
7. Test!

---

## 💡 Next Steps

1. **Choose email service** (Gmail for testing, SendGrid for production)
2. **Get credentials** (app password or API key)
3. **Add to .env file**
4. **Install packages**
5. **Restart server**
6. **Test submission**
7. **Check email!**

---

## 🆘 Need Help?

**Gmail Setup Issues:**
- Make sure 2FA is enabled
- Use app password, not regular password
- Check "Less secure app access" is OFF (use app password instead)

**SendGrid Setup Issues:**
- Verify sender email first
- API key needs "Full Access"
- Check API key is correct in .env

**Still Not Working:**
- Check server logs for errors
- Verify .env file is loaded
- Try sending test email manually
- Check spam folder

---

## 🎉 Summary

**Current:** Emails logged to console only

**To Enable:**
1. Choose email service
2. Get credentials
3. Configure .env
4. Install packages
5. Restart server

**Recommended:**
- **Testing:** Gmail (free, easy)
- **Production:** SendGrid (reliable, professional)

Let me know which service you want to use and I'll help you set it up! 📧
