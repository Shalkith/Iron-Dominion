# War Game - Multiplayer Strategy Game MVP

A persistent online multiplayer strategy war game where players spawn on a grid map, claim territory, generate resources, attack enemies, and form alliances.

## Tech Stack

- **Frontend**: Next.js 14 (React, App Router) + TailwindCSS
- **Backend**: Python FastAPI
- **Database**: PostgreSQL (async via asyncpg)
- **Cache/Realtime**: Redis
- **Auth**: Session-based (cookies)

## Project Structure

```
war-game/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── game/         # Game tick system
│   │   ├── config.py     # Settings
│   │   ├── database.py   # DB configuration
│   │   ├── main.py       # FastAPI app entry
│   │   └── ...
│   ├── seed.py           # Map generation script
│   └── requirements.txt
├── frontend/           # Next.js frontend
│   ├── app/            # Pages (App Router)
│   ├── components/     # React components
│   ├── lib/            # Utilities
│   └── ...
├── database/           # Database migrations
│   ├── migrations/
│   └── alembic.ini
└── README.md
```

## Quick Start (One Command)

The easiest way to get started is using the automated setup script:

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh

# Or use Python directly
python setup.py
```

This will:
1. Check all prerequisites
2. Set up Python virtual environment
3. Install all dependencies
4. Create the database
5. Generate the 50x50 game map
6. Start both backend and frontend servers

Then open http://localhost:3000 in your browser!

### Subsequent Runs

After the initial setup, just run:

```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Or
python start.py
```

---

## Manual Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### 1. Database Setup

Create PostgreSQL database:

```bash
createdb wargame
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Initialize database tables
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

# Generate the map
python seed.py

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new player |
| POST | `/auth/login` | Login player |
| POST | `/auth/logout` | Logout player |
| GET | `/auth/me` | Get current player info |

**Register/Login Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

### Game

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/game/map` | Get all tiles |
| GET | `/game/map/with-owners` | Get tiles with owner details |
| GET | `/game/my-tiles` | Get player's tiles |
| POST | `/game/claim` | Claim a tile |
| POST | `/game/attack` | Attack a tile |
| POST | `/game/spawn` | Spawn player on map |
| GET | `/game/attack-logs` | Get battle history |
| GET | `/game/leaderboard` | Get player rankings |

**Claim/Attack Request:**
```json
{
  "x": 10,
  "y": 20
}
```

### Alliances

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alliances/my` | Get my alliances |
| GET | `/alliances/requests/pending` | Get pending requests |
| POST | `/alliances/request` | Send alliance request |
| POST | `/alliances/accept/{id}` | Accept request |
| POST | `/alliances/reject/{id}` | Reject request |
| GET | `/alliances/players` | List all players |

**Alliance Request:**
```json
{
  "to_player_id": 123
}
```

## Game Mechanics

### Territory & Resources

- **Map Size**: 50x50 grid (2,500 tiles)
- **Resources**: Each tile has a resource value (1-5)
- **Income**: Gold generated every 10 seconds based on owned tiles
- **Spawn**: Players spawn on a random unclaimed tile

### Combat

- **Attack**: Requires adjacent territory
- **Win Condition**: Attacker army > Defender army
- **Cooldown**: 30 seconds between attacks
- **Casualties**: Attackers lose 20% army on win, 33% on loss

### Alliances

- Allied players cannot attack each other
- Requests must be accepted to form alliance
- One-way requests only (no auto-confirmation)

## Example API Requests

### Register a new player

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "warlord", "password": "secret123"}' \
  -c cookies.txt
```

### Claim a tile

```bash
curl -X POST http://localhost:8000/game/claim \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"x": 25, "y": 25}'
```

### Attack an enemy tile

```bash
curl -X POST http://localhost:8000/game/attack \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"x": 26, "y": 25}'
```

### Send alliance request

```bash
curl -X POST http://localhost:8000/alliances/request \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"to_player_id": 2}'
```

## UI Overview

### Login/Register Page
- Simple tabbed interface for authentication
- Session persisted via HTTP-only cookies

### Dashboard

**Header**: Shows player name, gold, army size, and tile count

**Tabs**:
1. **Map**: Interactive 50x50 grid
   - Blue = Your tiles
   - Red = Enemy tiles
   - Gray = Neutral
   - Click to claim (neutral) or attack (enemy)

2. **Alliances**: Manage alliances
   - View active alliances
   - Send/accept/reject requests

3. **Attack Logs**: Battle history
   - Shows attacks you've made and received

4. **Leaderboard**: Player rankings
   - Sorted by gold
   - Shows army size and tile count

## Extending the System

### Adding New Buildings

1. Add building types to `app/models/building.py`
2. Create migration to add buildings table
3. Add building routes in `app/routes/buildings.py`
4. Include building effects in game tick system

### Implementing Fog of War

```python
# In tile_service.py
async def get_visible_tiles(db: AsyncSession, player_id: int) -> List[Tile]:
    player_tiles = await get_player_tiles(db, player_id)
    visible = set()

    for tile in player_tiles:
        # Add surrounding tiles
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                visible.add((tile.x + dx, tile.y + dy))

    return [t for t in all_tiles if (t.x, t.y) in visible]
```

### Adding Unit Types

1. Create `Unit` model with type, attack, defense stats
2. Modify combat resolution to use unit stats
3. Add unit recruitment endpoints

### WebSocket Support (Real-time)

```python
# In app/websocket.py
from fastapi import WebSocket

@app.websocket("/ws/game")
async def game_websocket(websocket: WebSocket):
    await websocket.accept()
    # Subscribe to Redis pub/sub for tick updates
    # Broadcast to connected clients
```

### Battle Replay System

Store battle events as JSON and replay:

```python
class BattleReplay(Base):
    __tablename__ = "battle_replays"

    id = Column(Integer, primary_key=True)
    attack_log_id = Column(Integer, ForeignKey("attack_logs.id"))
    events = Column(JSON)  # [{"tick": 1, "action": "move", ...}]
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection string |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection string |
| `SECRET_KEY` | dev-secret | Session encryption key |
| `MAP_SIZE` | 50 | Grid size (NxN) |
| `TICK_INTERVAL` | 10 | Seconds between resource ticks |
| `STARTING_GOLD` | 100 | Initial player gold |
| `STARTING_ARMY` | 10 | Initial army size |
| `ATTACK_COOLDOWN` | 30 | Seconds between attacks |

## Architecture Notes

### Why Session-based Auth?

- Simpler than JWT for MVP
- Cookies work well with browser same-origin policy
- Easy to invalidate (server-side)

### Why Polling over WebSockets?

- Simpler implementation
- Works behind restrictive proxies
- Easy to scale horizontally
- For MVP, 5-second polling is sufficient

### Database Design

- **Async SQLAlchemy** for non-blocking I/O
- **Selectinload** for relationship eager loading
- **Indexes** on frequently queried columns (x, y, owner_id)

### Game Tick System

- Runs as async background task
- Uses `AsyncSessionLocal` for independent sessions
- Redis for tick state persistence
- Commits in bulk for performance

## Troubleshooting

### Database connection issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Redis connection issues

```bash
# Test Redis
redis-cli ping
```

### Frontend proxy errors

Ensure backend is running on port 8000:
```bash
curl http://localhost:8000/health
```

## License

MIT - Feel free to use and extend!

## Future Ideas

- [ ] Fog of war
- [ ] Unit types (infantry, cavalry, archers)
- [ ] Buildings (barracks, farms, walls)
- [ ] Tech tree
- [ ] Trading between allies
- [ ] Clans/guilds
- [ ] Real-time WebSocket updates
- [ ] Mobile app (React Native)
- [ ] AI opponents
- [ ] Tournament system
