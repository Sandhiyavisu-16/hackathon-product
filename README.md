# Innovation Idea Submission Platform

A full-stack web application for submitting and managing innovation ideas with AI-powered scoring using configurable rubrics and LLM models.

## Features

### For Contributors
- **Single Idea Submission**: Submit ideas via an intuitive form
- **Track Submissions**: View your submission history and status

### For Administrators
- **Bulk Upload**: Upload multiple ideas via CSV or Excel files
- **All Ideas Dashboard**: View all submitted ideas in a card-based interface
- **Model Configuration**: Configure and test AI models (Azure OpenAI, Gemini, Gemma)
- **Rubric Management**: Create and manage scoring rubrics
- **Idea Details**: Click any idea card to view full details in a modal

## Tech Stack

### Backend
- **Node.js** with **TypeScript**
- **Fastify** - Fast web framework
- **PostgreSQL** - Database
- **Redis** - Caching (optional)
- **XLSX** - Excel file processing

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Modern CSS** - Responsive design with animations
- **Toast Notifications** - Clean user feedback

### AI/LLM Support
- **LiteLLM Integration** - Unified gateway for 100+ providers
- Azure OpenAI
- Google Gemini
- Gemma (local/self-hosted)
- OpenAI
- Anthropic Claude
- And 100+ more via LiteLLM

## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Redis (optional)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd model-rubric-idea-submission
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run database migrations**
```bash
npm run migrate:up
```

5. **Start the development server**
```bash
npm run dev
```

6. **Open the application**
```
http://localhost:3000
```

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Server
PORT=3000
NODE_ENV=development

# AI Models (configure as needed)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
GEMINI_API_KEY=your_key
```

## Project Structure

```
├── src/
│   ├── config/          # Configuration files
│   ├── middleware/      # Auth and other middleware
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   │   ├── providers/   # AI model adapters
│   │   ├── CSVProcessor.ts
│   │   ├── RubricService.ts
│   │   └── SubmissionService.ts
│   └── types/           # TypeScript types
├── public/              # Frontend files
│   ├── index.html
│   ├── app.js
│   ├── help.html
│   └── ideas_template.csv
├── migrations/          # Database migrations
└── docs/               # Documentation

```

## API Endpoints

### Ideas
- `POST /api/ideas/single` - Submit single idea
- `POST /api/ideas/submit` - Bulk upload (CSV/Excel)
- `GET /api/ideas/all` - Get all ideas (admin)
- `GET /api/ideas/submissions` - Get user submissions
- `GET /api/ideas/:id` - Get submission details
- `DELETE /api/ideas/:id` - Delete submission

### Rubrics
- `GET /api/rubrics` - List rubrics
- `POST /api/rubrics` - Create rubric
- `PUT /api/rubrics/:id` - Update rubric
- `DELETE /api/rubrics/:id` - Delete rubric

### Models
- `GET /api/models` - List model configurations
- `POST /api/models` - Create model config
- `PUT /api/models/:id` - Update model config
- `POST /api/models/:id/test` - Test model connection
- `POST /api/models/:id/activate` - Activate model

## User Roles

### Contributor
- Submit single ideas via form
- View own submissions
- Access to "Submit Ideas" tab only

### Admin
- All contributor permissions
- Bulk upload via CSV/Excel
- View all submitted ideas
- Manage rubrics and model configurations
- Access to all tabs

## File Upload Formats

### CSV/Excel Template
Download the template from the UI or use this structure:

```csv
Idea Id,Your idea title,Brief summary of your Idea,Challenge/Business opportunity...,Novelty of the idea benefits and risks,...
```

**Required Fields:**
- Your idea title (5-500 characters)
- Brief summary of your Idea (min 10 characters)

**Optional Fields:**
- Idea Id
- Challenge/Business opportunity
- Novelty, benefits and risks
- Responsible AI adherence
- Additional documentation
- Second file info
- Preferred week of participation
- Build phase preference
- Build method preference
- Code development preference

## Development

### Run in development mode
```bash
npm run dev
```

### Build for production
```bash
npm run build
npm start
```

### Run tests
```bash
npm test
```

### Database migrations
```bash
# Create new migration
npm run migrate:create migration-name

# Run migrations
npm run migrate:up

# Rollback migration
npm run migrate:down
```

## Features in Detail

### Toast Notifications
- Success, error, and info messages
- Auto-dismiss after 5-6 seconds
- Smooth animations
- Stack multiple notifications

### Idea Cards
- Clean, minimal design
- Shows title and summary
- Click to view full details in modal
- Hover effects

### Modal Popup
- Full idea details
- Organized sections
- Close with × button, outside click, or Escape key
- Smooth animations

### Role-Based UI
- Dynamic tab visibility
- Automatic default views
- Permission-based features

## Documentation

### Quick Links
- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [Project Summary](PROJECT_SUMMARY.md) - Complete feature overview

### Detailed Guides (in `/docs` folder)
- [API Key Flow](docs/API_KEY_FLOW.md) - **Important!** How API keys are managed
- [Database Schema Guide](docs/DATABASE_SCHEMA_GUIDE.md) - Database structure and tables
- [CSV Format Guide](docs/CSV_FORMAT_GUIDE.md) - File upload format specifications
- [Roles & Permissions](docs/ROLES_AND_PERMISSIONS.md) - User access control
- [UI Guide](docs/UI_GUIDE.md) - Frontend features and components
- [Rubric Features](docs/RUBRIC_FEATURES.md) - Scoring rubric system
- [Model Configuration](docs/MODEL_CONFIG_GUIDE.md) - AI model setup
- [Performance Tips](docs/PERFORMANCE_TIPS.md) - Optimization guidelines

### Setup Guides (in `/docs` folder)
- [LiteLLM Integration](docs/LITELLM_INTEGRATION.md) - **NEW!** Unified LLM gateway setup
- [Gemini Setup](docs/GEMINI_SETUP_GUIDE.md) - Google Gemini API configuration
- [Gemma Setup](docs/GEMMA_FREE_SETUP_GUIDE.md) - Local Gemma model setup
- [Email Setup](docs/EMAIL_SETUP_GUIDE.md) - SendGrid configuration

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
