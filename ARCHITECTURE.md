# SportStatBot Architecture

## Overview

SportStatBot is a comprehensive sports analytics platform built with modern Python technologies. It provides real-time data ingestion, advanced metrics calculation, and predictive analytics for sports teams, players, and games.

## Technology Stack

### Backend
- **FastAPI**: Async web framework for high-performance APIs
- **Python 3.11+**: Modern Python with type hints
- **SQLAlchemy 2.0**: Async ORM for database operations
- **Pydantic v2**: Data validation and serialization

### Database
- **PostgreSQL 15+**: Primary relational database
- **TimescaleDB**: Extension for time-series data (play-by-play)
- **Redis 7+**: Caching and real-time data storage

### Analytics & ML
- **NumPy**: Numerical computations
- **pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning and clustering
- **SciPy**: Statistical analysis

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Alembic**: Database migrations
- **uvicorn**: ASGI server

## Architecture Layers

### 1. API Layer (`app/api/`)
RESTful API endpoints organized by domain:
- **Teams** (`/api/v1/teams`): Team CRUD operations
- **Players** (`/api/v1/players`): Player management and stats
- **Games** (`/api/v1/games`): Game data and live scores
- **Analytics** (`/api/v1/analytics`): Advanced analytics endpoints
- **Metrics** (`/api/v1/metrics`): Performance metrics calculation

### 2. Service Layer (`app/services/`)
Business logic and analytics engines:

#### Ingestion Services (`app/services/ingestion/`)
- **LiveDataIngestion**: Real-time play-by-play ingestion
- Handles second-by-second game updates
- Triggers momentum and win probability calculations

#### Analytics Services (`app/services/analytics/`)
- **MetricsEngine**: Advanced team and player metrics
  - EPA (Expected Points Added)
  - xG (Expected Goals)
  - CPOE (Completion Percentage Over Expected)
  - Success Rate
  - Offensive/Defensive Ratings
  - Pythagorean Win Expectation

- **MomentumEngine**: Real-time momentum tracking
  - Swing detection and magnitude
  - Excitement index calculation
  - Game leverage analysis

- **WinProbabilityCalculator**: Live win probability
  - Score-based probability
  - Time-adjusted calculations
  - Leverage index

- **PlayerChemistryAnalyzer**: Player synergy analytics
  - Chemistry scores between players
  - Lineup combination analysis
  - Player similarity clustering

- **FormTrajectoryPredictor**: Performance forecasting
  - Trend analysis (improving/declining/stable)
  - 5-game performance projections
  - Win probability forecasting

- **InjuryImpactSimulator**: Injury analysis
  - Player value calculation
  - Team performance impact
  - Replacement player analysis

### 3. Data Layer (`app/models/`)

#### Core Entities
- **Team**: Team information, venue details, standings
- **Player**: Player profiles, contracts, injury status
- **Game**: Game information, scores, environmental conditions
- **GameEvent**: Significant in-game events
- **PlayByPlay**: Second-by-second play tracking (TimescaleDB)

#### Analytics Models
- **TeamMetrics**: Advanced team performance metrics
- **PlayerMetrics**: Advanced player performance metrics
- **PlayerChemistry**: Player synergy and chemistry scores
- **MomentumEvent**: Real-time momentum tracking data
- **FormTrajectory**: Team form and projections
- **InjuryImpact**: Injury impact analysis
- **RefereeStats**: Referee bias and statistics
- **CoachingProfile**: Coaching style and strategy
- **TeamIdentity**: Team playing style classification

### 4. Schema Layer (`app/schemas/`)
Pydantic models for API validation:
- Request validation (Create, Update)
- Response serialization
- Type safety and documentation

### 5. Core Infrastructure (`app/core/`)
- **config.py**: Application configuration management
- **database.py**: Async database connection and session handling
- **cache.py**: Redis cache manager

## Key Features Implementation

### Live Play-by-Play Ingestion
```python
# Real-time data flow:
External API → LiveDataIngestion → PlayByPlay Model → Database
                     ↓
              MomentumEngine → MomentumEvent
                     ↓
         WinProbabilityCalculator → Cache
```

### Advanced Metrics Calculation
Metrics are calculated on-demand or scheduled:
1. Retrieve recent games/performances
2. Apply sport-specific formulas
3. Calculate derived metrics (EPA, xG, etc.)
4. Store in metrics tables
5. Cache frequently accessed data

### Momentum Tracking
Real-time momentum calculation based on:
- Score differential trends
- Win probability changes
- Play significance
- Time remaining
- Game leverage

### Form Trajectory
Forecasting pipeline:
1. Analyze last N games (default 10)
2. Calculate trend direction (linear regression)
3. Project performance metrics
4. Generate win/loss probabilities
5. Provide confidence intervals

### Player Chemistry
Analysis components:
- Shared playing time tracking
- Plus/minus when together
- Assist connections
- Offensive/defensive synergy
- Lineup optimization

### Injury Impact Simulation
Impact calculation:
1. Calculate player value (WAR-like metric)
2. Identify replacement player
3. Calculate value differential
4. Project team win% change
5. Analyze offensive/defensive impact

## Data Flow

### Ingestion Flow
```
External API/Feed
      ↓
LiveDataIngestion Service
      ↓
PlayByPlay/GameEvent Models
      ↓
Database + Cache
      ↓
Analytics Engines (triggered)
      ↓
Metrics/Analytics Models
```

### Query Flow
```
API Request
      ↓
Cache Check
      ↓ (if miss)
Database Query
      ↓
Analytics Calculation (if needed)
      ↓
Cache Update
      ↓
API Response
```

## Caching Strategy

### Cache Keys
- `game:{game_id}:score` - Live scores (TTL: 10s)
- `game:{game_id}:latest_play` - Latest play (TTL: 60s)
- `game:{game_id}:tracking` - Game tracking status (TTL: 4h)
- `team:{team_id}:metrics` - Team metrics (TTL: 5m)
- `player:{player_id}:metrics` - Player metrics (TTL: 5m)

### Cache Invalidation
- Time-based expiration (TTL)
- Event-based invalidation (on updates)
- Pattern-based flush for related data

## Performance Optimizations

1. **Async Operations**: All I/O operations are async
2. **Database Indexing**: Indexes on frequently queried columns
3. **Connection Pooling**: Reuse database connections
4. **Caching**: Redis for frequently accessed data
5. **Batch Processing**: Bulk operations where possible
6. **Lazy Loading**: Load relationships only when needed

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers (can run multiple instances)
- Shared PostgreSQL and Redis instances
- Load balancer for distribution

### Vertical Scaling
- Database optimization (indexes, partitioning)
- Redis cluster for large datasets
- TimescaleDB for efficient time-series queries

### Future Enhancements
- Message queue (RabbitMQ/Kafka) for async processing
- Separate analytics workers
- Read replicas for heavy read loads
- Microservices architecture for independent scaling

## Security

### Current Implementation
- Input validation (Pydantic)
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration
- Environment-based secrets

### Production Recommendations
- API authentication (JWT tokens)
- Rate limiting
- HTTPS/TLS encryption
- Database connection encryption
- API key management for external services
- Role-based access control (RBAC)

## Testing Strategy

### Unit Tests
- Service layer logic
- Analytics calculations
- Utility functions

### Integration Tests
- API endpoints
- Database operations
- Cache interactions

### Performance Tests
- Load testing for live ingestion
- Query optimization validation
- Cache hit rate analysis

## Deployment

### Development
```bash
docker-compose up -d
```

### Production
- Use production-grade ASGI server (Gunicorn + uvicorn)
- Configure environment variables securely
- Set up monitoring and logging
- Implement health checks
- Database backups and replication

## Monitoring & Observability

### Recommended Tools
- **Logging**: Structured logging with JSON
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Error Tracking**: Sentry
- **Performance**: APM tools (DataDog, New Relic)

### Key Metrics to Monitor
- API response times
- Database query performance
- Cache hit/miss rates
- Live ingestion throughput
- Error rates
- Resource utilization (CPU, memory)

## Future Enhancements

### Planned Features
1. **ML Models**: Train predictive models on historical data
2. **WebSocket Support**: Real-time updates to clients
3. **Data Visualization**: Built-in chart generation
4. **Multi-Sport Support**: Sport-specific metric implementations
5. **Historical Analysis**: Deep dive into historical trends
6. **Automated Insights**: AI-generated game summaries
7. **Betting Integration**: Odds comparison and value detection
8. **Social Features**: User predictions and leaderboards

### Technical Debt
- Placeholder implementations to be replaced with real calculations
- External API integration (ESPN, SportsRadar, etc.)
- Comprehensive test coverage
- Documentation for all endpoints
- Performance benchmarking

## Contributing

### Code Organization
- Follow existing patterns
- Add type hints
- Write docstrings
- Update tests
- Run linters (black, flake8, mypy)

### Database Changes
1. Create Alembic migration
2. Test upgrade/downgrade
3. Update models and schemas
4. Document changes

## License

MIT License - See LICENSE file for details
