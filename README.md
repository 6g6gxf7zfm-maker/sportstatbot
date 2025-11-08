# SportStatBot - Advanced Sports Analytics Platform

A comprehensive sports analytics platform with real-time data ingestion, advanced metrics, and predictive modeling.

## Features

### Core Data & Analytics
- **Live Play-by-Play Ingestion**: Second-by-second game updates
- **Advanced Team Metrics**: EPA/play, xG, CPOE, Success Rate, etc.
- **Player Analytics**: Chemistry scores, similarity clusters, clutch performance
- **Momentum Engine**: Real-time swing tracking and momentum shifts
- **Predictive Models**: Form trajectory forecasting, injury impact simulation
- **Environmental Factors**: Weather, stadium conditions, referee bias
- **Game Context**: Intensity index, rest/fatigue analysis
- **Coaching Analytics**: Style profiles, tempo, substitution patterns
- **Roster Management**: Trade impact prediction, depth chart evolution
- **Schedule Analysis**: Strength of schedule, opponent difficulty

## Architecture

### Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 15+ with TimescaleDB extension
- **Cache**: Redis 7+
- **Analytics**: pandas, numpy, scikit-learn, scipy
- **Real-time**: WebSockets for live updates
- **Container**: Docker & docker-compose

### Project Structure
```
sportstatbot/
├── app/
│   ├── api/                  # API endpoints
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   │   ├── ingestion/       # Data ingestion services
│   │   ├── analytics/       # Analytics engines
│   │   └── predictions/     # Predictive models
│   ├── core/                 # Core configuration
│   └── utils/                # Utilities
├── tests/                    # Test suite
├── docker/                   # Docker configurations
└── scripts/                  # Utility scripts
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sportstatbot
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

5. Access the API:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Development

### Local Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

### Running Tests
```bash
pytest tests/ -v
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

## License

MIT License
