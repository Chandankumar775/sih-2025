# WatchTower Backend

AI-Powered Cyber Incident Portal for Defence  
**Smart India Hackathon 2025 | Team Urban Dons**

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `JWT_SECRET_KEY` - A secure random string (min 32 characters)
- `GOOGLE_API_KEY` - Google Gemini API key (for AI analysis)

### 3. Run the Server

**Development:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Access the API

- API Root: http://localhost:8000/api
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/logout` | Logout user |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user info |

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/incidents` | Submit new incident |
| GET | `/api/incidents` | List incidents (paginated) |
| GET | `/api/incidents/{id}` | Get incident details |
| GET | `/api/incidents/{id}/analysis` | Get incident analysis |
| POST | `/api/incidents/{id}/escalate` | Escalate to CERT |

### Analytics (Admins only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/stats` | Get incident statistics |
| GET | `/api/analytics/trends` | Get incident trends |
| GET | `/api/analytics/risk-distribution` | Get risk distribution |

## Demo Accounts

For hackathon demonstration:

| Email | Password | Role |
|-------|----------|------|
| reporter@army.mil | demo123 | Reporter |
| admin@rakshanetra.mil | demo123 | Admin |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Settings & configuration
│   │   ├── database.py      # Supabase client
│   │   └── security.py      # JWT & authentication
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routes/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── incidents.py     # Incident endpoints
│   │   └── analytics.py     # Analytics endpoints
│   └── services/
│       ├── ai_analyzer.py   # AI threat analysis
│       ├── incident_service.py
│       └── analytics_service.py
├── requirements.txt
├── .env.example
└── README.md
```

## Deployment

### Railway

1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Render

1. Create a new Web Service
2. Connect repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Technology Stack

- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database & auth
- **Google Gemini** - AI-powered threat analysis
- **Pydantic** - Data validation
- **JWT** - Secure authentication

## License

Built for Smart India Hackathon 2025
