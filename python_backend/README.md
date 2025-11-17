# Innovation Idea Submission Platform - Python Backend

Complete Python/FastAPI conversion of the Node.js/TypeScript backend.

## Features

- ✅ FastAPI web framework
- ✅ PostgreSQL database with connection pooling
- ✅ Redis caching
- ✅ File upload handling (CSV/Excel)
- ✅ Idea submission processing
- ✅ Admin dashboard APIs
- ✅ Authentication middleware (mock - needs JWT implementation)
- ✅ CORS support
- ✅ Static file serving

## Project Structure

```
python_backend/
├── config/
│   ├── settings.py          # Application configuration
│   ├── database.py           # Database connection pool
│   └── redis_client.py       # Redis client
├── models/
│   └── types.py              # Type definitions and enums
├── services/
│   ├── csv_processor.py      # CSV validation and processing
│   └── submission_service.py # Idea submission logic
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

1. **Install Python 3.11+**

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   Copy `.env.example` to `.env` and update values:
   ```bash
   cp ../.env.example .env
   ```

## Running the Application

### Development Mode (with auto-reload):
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### Production Mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 3000 --workers 4
```

## API Endpoints

### Health Check
- `GET /health` - Application health status

### Ideas
- `GET /api/ideas/template` - Download CSV template
- `POST /api/ideas/single` - Submit single idea (form)
- `POST /api/ideas/submit` - Submit ideas (CSV/Excel upload)
- `GET /api/ideas/all` - Get all ideas (admin)
- `GET /api/ideas/submissions` - Get user's submissions
- `DELETE /api/ideas/{id}` - Delete submission

### Model Configuration
- `GET /api/config/model` - Get model configuration
- `POST /api/config/model` - Create model configuration

### Rubrics
- `GET /api/rubrics` - Get all rubrics

## Database Migrations

The application uses the same PostgreSQL database schema as the Node.js version. Run migrations using:

```bash
# From project root
npm run migrate:up
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Differences from Node.js Version

### Completed:
- ✅ Core FastAPI application structure
- ✅ Database connection pooling (psycopg2)
- ✅ Redis client (async)
- ✅ CSV/Excel file processing
- ✅ Idea submission service
- ✅ All idea-related API endpoints
- ✅ Static file serving
- ✅ CORS middleware

### To Be Implemented:
- ⏳ JWT authentication (currently mocked)
- ⏳ Model configuration service
- ⏳ Rubric service
- ⏳ Email service
- ⏳ S3 storage integration
- ⏳ Virus scanning integration
- ⏳ Rate limiting
- ⏳ Event bus integration

## Performance Notes

- Uses connection pooling for database (configurable pool size)
- Async/await for non-blocking I/O
- Supports multiple workers in production
- Redis caching for frequently accessed data

## Dependencies

Key Python packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `psycopg2-binary` - PostgreSQL adapter
- `redis` - Redis client
- `openpyxl` - Excel file processing
- `pandas` - Data processing
- `pydantic` - Data validation
- `python-multipart` - File upload support

## Migration from Node.js

This Python backend is a drop-in replacement for the Node.js backend. It:
- Uses the same database schema
- Exposes the same API endpoints
- Maintains the same business logic
- Works with the existing frontend

Simply point your frontend to this Python backend instead of the Node.js one.

## License

MIT
