# Lyric Meaning Explanation Backend

Backend API untuk aplikasi Lyric Meaning Explanation (LME) yang menyediakan:
- Search lagu via Genius API
- Deteksi emosi dari lirik menggunakan ONNX model (28 emotions - GoEmotions)
- Interpretasi lirik
- User authentication & history
- Playlist management

**Tech Stack:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, ONNX Runtime

---

## Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Redis (optional, untuk caching)

---

## Setup

### 1. Clone & Install Dependencies

```bash
# Clone repository
git clone <repo-url>
cd lme-backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dan sesuaikan:
nano .env
```

**Required environment variables:**
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/lme_db

# JWT Secret (generate random string)
SECRET_KEY=your-super-secret-key-here

# Genius API Token (get from https://genius.com/api-clients)
GENIUS_ACCESS_TOKEN=your-genius-token-here

# Optional
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup

```bash
# Create database
createdb lme_db

# Or dengan psql:
psql -U postgres -c "CREATE DATABASE lme_db;"

# Run migrations
alembic upgrade head
```

---

## Running the Application

### Development Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start server dengan auto-reload
uvicorn app.main:app --reload

# Server will run at: http://localhost:8000
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: `/api/api-spec.yaml`

---

## Database Migrations

```bash
# Create new migration (setelah edit models)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# View migration history
alembic history
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user baru
- `POST /api/v1/auth/login` - Login (JWT cookie)
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token

### Users
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile

### Songs (Main Feature)
- `GET /api/v1/songs/search?q=...` - Search lagu (Genius)
- `POST /api/v1/songs/explain` - Explain lirik + deteksi emosi

### History
- `GET /api/v1/history` - List history
- `POST /api/v1/history` - Create history
- `GET /api/v1/history/{id}` - Get detail
- `DELETE /api/v1/history/{id}` - Delete history
- `GET /api/v1/history/search/?q=...` - Search history

### Playlist
- `GET /api/v1/playlist` - List playlists
- `POST /api/v1/playlist` - Create playlist
- `GET /api/v1/playlist/{id}` - Get playlist with songs
- `PATCH /api/v1/playlist/{id}` - Update playlist
- `DELETE /api/v1/playlist/{id}` - Delete playlist
- `POST /api/v1/playlist/{id}/songs` - Add song
- `DELETE /api/v1/playlist/{id}/songs/{song_id}` - Remove song

---

## Example Usage

### 1. Register & Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' \
  -c cookies.txt
```

### 2. Search & Explain Song

```bash
# Search lagu
curl "http://localhost:8000/api/v1/songs/search?q=bohemian+rhapsody"

# Explain lirik (requires login)
curl -X POST http://localhost:8000/api/v1/songs/explain \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "songs": [
      {"title": "Bohemian Rhapsody", "artist": "Queen"}
    ]
  }'
```

---

## Project Structure

```
lme-backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Config, security, exceptions
│   ├── db/               # Database session
│   ├── dl/models/        # ONNX models
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── alembic/              # Database migrations
├── tests/                # Unit & integration tests
├── api/                  # OpenAPI spec
└── requirements.txt      # Python dependencies
```

---

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -d lme_db -c "SELECT 1;"
```

### Genius API 403 Error
API sudah dilengkapi fallback mechanism. Jika endpoint `/search/multi` kena rate limit, sistem otomatis fallback ke web scraping.

### ONNX Model Error
Model menggunakan **roberta-base** tokenizer. Pastikan transformers sudah terinstall:
```bash
pip install transformers
```
