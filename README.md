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
- **Python 3.11+** with **FastAPI**
- **PostgreSQL** - Database with integer primary keys
- **Redis** - Caching (optional)
- **Pandas & OpenPyXL** - Excel/CSV file processing
- **Psycopg2** - PostgreSQL adapter
- **Uvicorn** - ASGI server

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Modern CSS** - Responsive design with animations
- **Toast Notifications** - Clean user feedback

### AI/LLM Support
- **LiteLLM** - Unified interface for 100+ LLM providers
- Azure OpenAI
- Google Gemini
- Anthropic Claude
- OpenAI
- And 100+ more providers via LiteLLM

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd innovation-idea-platform
```

2. **Install Python dependencies**
```bash
cd python_backend
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run database migrations**
```bash
# Using psql or pgAdmin, run:
psql -U postgres -d your_database -f migrations/1763200000000_convert-uuid-to-integer-ids.sql
```

5. **Start the Python backend**
```bash
python main.py
```

6. **Open the application**
```
http://localhost:3000
```

## Environment Variables

```env
# Server
PORT=3000
NODE_ENV=development

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres
DATABASE_POOL_SIZE=20

# Redis (optional)
REDIS_URL=redis://localhost:6379

# File Limits
MAX_CSV_ROWS=500
MAX_MP4_SIZE=104857600  # 100MB
MAX_DOC_SIZE=104857600  # 100MB

# JWT Authentication
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60
```

**Note:** LLM API keys are stored in the database per model configuration, not in environment variables.

## Project Structure

```
├── python_backend/          # Python FastAPI backend
│   ├── config/             # Configuration files
│   │   ├── database.py     # PostgreSQL connection pooling
│   │   ├── redis_client.py # Redis caching
│   │   └── settings.py     # Environment settings
│   ├── services/           # Business logic
│   │   ├── llm_service.py  # LiteLLM integration
│   │   ├── model_config_service.py
│   │   ├── submission_service.py
│   │   └── csv_processor.py
│   ├── models/             # Pydantic models
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── public/                 # Frontend files
│   ├── index.html
│   ├── app.js
│   ├── help.html
│   └── ideas_template.csv
├── migrations/             # Database migrations
└── docs/                   # Documentation
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
cd python_backend
python main.py
```

### Production deployment
```bash
cd python_backend
uvicorn main:app --host 0.0.0.0 --port 3000 --workers 4
```

### Database migrations
```bash
# Run migrations using psql
psql -U postgres -d your_database -f migrations/migration-file.sql

# Or use pgAdmin to execute SQL files
```

### API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`

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

### Setup Guides
- [LiteLLM Integration](python_backend/LITELLM_INTEGRATION.md) - **NEW!** Unified LLM provider integration
- [Python Backend README](python_backend/README.md) - Backend-specific documentation

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
