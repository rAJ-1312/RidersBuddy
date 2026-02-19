# 🏍️ RidersBuddy - Technical Design Document

**Version:** 1.0  
**Date:** February 18, 2026  
**Status:** Active Development

---

## 1. What is RidersBuddy?

**RidersBuddy** is a motorcycle route planning and social networking platform that helps riders finds paths as per their preference, discover scenic routes, find riding buddies, and plan multi-leg journeys. The system uses a **hybrid database architecture**:

**Key Innovation**: Uses Neo4j's graph database for intelligent pathfinding while PostgreSQL handles transactional data.


## 2. Use Case: Smart Route Discovery & Social Riding

### 2.1 Primary Use Case

**Scenario:** A rider wants to plan a journey from Point A to Point B, discovering the best route based on:
- Scenic waypoints (viewpoints, cafes, landmarks)
- Difficulty level matching their experience
- Recommendations from riders they follow
- Multi-leg journeys with interesting stops

**Example Flow:**
```
1. Rider opens app: "I want to ride from Grid(10,20) to Grid(50,80)"
2. System queries Neo4j graph:
   - Find shortest path through waypoints
   - Filter by difficulty and route type
   - Boost routes taken by followed riders
3. Returns: 3 route options with waypoints, distance, estimated time
4. Rider selects a route and logs the ride
5. System updates social graph (completed route, riding buddies)
```

### 2.2 Secondary Use Cases

1. **Social Discovery:** "Show me routes my friends have completed"
2. **Buddy Matching:** "Find riders near me who want to ride Route X"
3. **Progressive Exploration:** "Recommend routes slightly harder than what I've done"
4. **Group Rides:** "Plan a multi-day trip hitting 5 specific waypoints"

---

## 3. Data Architecture

### 3.1 Spatial System Design (Grid → OSM Migration Path)

**Design Philosophy:** Use a **simple grid system initially**, but architect the system so it can seamlessly migrate to **OpenStreetMap (OSM)** road networks later.

#### Current Implementation: Grid System

**Concept:** The riding area is divided into a square grid (e.g., 100x100 cells). Each cell can contain waypoints (locations of interest).


**Grid Coordinates:**
```
(0,0) = Northwest corner
(99,99) = Southeast corner
Each waypoint has: (grid_x, grid_y, lat, lng)
```

#### Future Implementation: OSM Road Network

When migrating to OSM:
- **Waypoints** become actual POIs (cafes, viewpoints, fuel stations) from OSM data
- **Grid connections** (`GRID_ADJACENT`) become actual **road segments** from OSM
- **Distance calculations** use actual road distances instead of grid-based estimates
- Neo4j relationships: `(:Waypoint)-[:ROAD_SEGMENT {osm_way_id, distance_km, road_type}]->(:Waypoint)`


### 3.2 PostgreSQL Schema

**Phase 1 Schema:**

```sql
-- Core entities for Phase 1

TABLE riders {
    id SERIAL PRIMARY KEY
    name VARCHAR(100) UNIQUE NOT NULL
    experience_level VARCHAR(20) DEFAULT 'beginner'
    created_at TIMESTAMP DEFAULT NOW()
}

TABLE waypoints {
    id SERIAL PRIMARY KEY
    name VARCHAR(200) NOT NULL
    grid_x INT NOT NULL  -- 0-99
    grid_y INT NOT NULL  -- 0-99
    lat DECIMAL(10, 7) NOT NULL
    lng DECIMAL(10, 7) NOT NULL
    type VARCHAR(50)  -- viewpoint, cafe, fuel_station, rest_area
    created_at TIMESTAMP DEFAULT NOW()
    
    INDEX idx_grid_coords (grid_x, grid_y)
}

TABLE routes {
    id SERIAL PRIMARY KEY
    name VARCHAR(200) UNIQUE NOT NULL
    difficulty VARCHAR(20)  -- easy, moderate, hard
    distance_km DECIMAL(8, 2)
    start_waypoint_id INT REFERENCES waypoints(id)
    end_waypoint_id INT REFERENCES waypoints(id)
    created_at TIMESTAMP DEFAULT NOW()
}

TABLE route_waypoints {
    -- Ordered list of waypoints in a route
    id SERIAL PRIMARY KEY
    route_id INT REFERENCES routes(id) ON DELETE CASCADE
    waypoint_id INT REFERENCES waypoints(id) ON DELETE CASCADE
    sequence_order INT NOT NULL
    
    UNIQUE(route_id, sequence_order)
}

TABLE rides {
    -- Completed ride logs
    id SERIAL PRIMARY KEY
    rider_id INT REFERENCES riders(id) ON DELETE CASCADE
    route_id INT REFERENCES routes(id) ON DELETE SET NULL
    completed_at TIMESTAMP DEFAULT NOW()
    rating INT CHECK (rating >= 1 AND rating <= 5)
}
```

### 3.3 Neo4j Graph Schema

```cypher
// Node Types (Phase 1)

(:Rider {
    pg_id: INT,
    name: STRING,
    experience_level: STRING
})

(:Waypoint {
    pg_id: INT,
    name: STRING,
    grid_x: INT,
    grid_y: INT,
    lat: FLOAT,
    lng: FLOAT,
    type: STRING
})

(:Route {
    pg_id: INT,
    name: STRING,
    difficulty: STRING,
    distance_km: FLOAT
})

// Relationships (Phase 1)

// 1. SPATIAL GRID
(:Waypoint)-[:GRID_ADJACENT {distance_km: FLOAT}]->(:Waypoint)
// Connects waypoints in adjacent grid cells

// 2. ROUTE STRUCTURE
(:Route)-[:STARTS_AT]->(:Waypoint)
(:Route)-[:ENDS_AT]->(:Waypoint)
(:Route)-[:PASSES_THROUGH {sequence: INT}]->(:Waypoint)

// 3. RIDE LOGS
(:Rider)-[:COMPLETED {completed_at: DATETIME, rating: INT}]->(:Route)
```

**Future Relationships (Post Phase 1):**
- `(:Waypoint)-[:GRID_NEARBY]->(:Waypoint)` - Alternative paths
- `(:Rider)-[:FOLLOWS]->(:Rider)` - Social graph
- `(:Rider)-[:RODE_WITH]->(:Rider)` - Group rides
- `(:Rider)-[:OWNS]->(:Bike)` - Bike ownership
- OSM: `(:Waypoint)-[:CONNECTED_BY]->(:Waypoint)` - Road segments


**Abstracted Python Implementation:**
```python
from app.spatial import get_spatial_provider

def discover_routes(start_coords, end_coords, filters):
    """
    Route discovery that works with any spatial provider
    """
    spatial = get_spatial_provider()
    
    paths = spatial.find_path(
        start=start_coords,
        end=end_coords,
        filters={
            'difficulties': filters.get('difficulties', ['easy', 'moderate']),
            'max_waypoints': filters.get('max_waypoints', 20),
            'road_types': filters.get('road_types', [])
    )
    
    return paths
```


## 4. Phase 1 System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         PHASE 1 FLOW                            │
└─────────────────────────────────────────────────────────────────┘

1. SETUP & DATA GENERATION
   ┌──────────────┐
   │ Run Factory  │ → Generate waypoints on 100x100 grid
   │   Scripts    │ → Create riders
   └──────┬───────┘ → Generate routes
          │
          ↓
   ┌──────────────────────────────────────────────────────┐
   │ PostgreSQL                    Neo4j                   │
   │ ┌─────────────┐              ┌──────────────┐       │
   │ │  waypoints  │ ────sync──→  │  :Waypoint   │       │
   │ │  (grid)     │              │  nodes       │       │
   │ └─────────────┘              └──────┬───────┘       │
   │                                     │                │
   │                              Create │ GRID_ADJACENT  │
   │                              relationships           │
   └──────────────────────────────────────────────────────┘

2. ROUTE DISCOVERY (Core Feature)
   ┌──────────────┐
   │ User Request │
   │ "Route from  │
   │ (10,20) to   │
   │ (50,80)"     │
   └──────┬───────┘
          │
          ↓
   ┌──────────────────────────────────────────────────────┐
   │ Neo4j Pathfinding                                     │
   │                                                       │
   │ MATCH path = shortestPath(                           │
   │   (start:Waypoint {grid_x:10, grid_y:20})            │
   │   -[:GRID_ADJACENT*1..15]->                          │
   │   (end:Waypoint {grid_x:50, grid_y:80})              │
   │ )                                                     │
   │ RETURN waypoints, total_distance                     │
   └──────┬───────────────────────────────────────────────┘
          │
          ↓
   ┌──────────────┐
   │ Response:    │
   │ [waypoint1,  │
   │  waypoint2,  │
   │  ...,        │
   │  waypointN]  │
   └──────────────┘

3. SAVE & LOG RIDE
   ┌──────────────┐
   │ User saves   │
   │ route as     │
   │ "Epic Ride"  │
   └──────┬───────┘
          │
          ↓
   ┌──────────────────────────────────────────────────────┐
   │ PostgreSQL              Neo4j                         │
   │ ┌──────────┐           ┌────────────────┐           │
   │ │ routes   │ ────→     │ :Route node    │           │
   │ │ INSERT   │           │ CREATE         │           │
   │ └──────────┘           └────────────────┘           │
   │                        Create relationships:         │
   │                        - [:STARTS_AT]                │
   │                        - [:ENDS_AT]                  │
   │                        - [:PASSES_THROUGH]           │
   └──────────────────────────────────────────────────────┘
          │
          ↓
   User completes ride
          │
          ↓
   ┌──────────────────────────────────────────────────────┐
   │ PostgreSQL              Neo4j                         │
   │ ┌──────────┐           ┌────────────────┐           │
   │ │ rides    │ ────→     │ (:Rider)       │           │
   │ │ INSERT   │           │   -[:COMPLETED {           │
   │ └──────────┘           │      rating:5   ]→         │
   │                        │   (:Route)     │           │
   │                        └────────────────┘           │
   └──────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ KEY OPERATIONS IN PHASE 1                                       │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Create waypoints with grid coordinates                        │
│ ✓ Auto-connect waypoints to adjacent cells (Neo4j)             │
│ ✓ Pathfinding: Grid(x1,y1) → Grid(x2,y2)                       │
│ ✓ Save discovered routes                                        │
│ ✓ Log completed rides                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Phase 1 API Endpoints

```python
POST /waypoints
{
    "name": "Sunset Point",
    "grid_x": 45,
    "grid_y": 67,
    "lat": 37.7749,
    "lng": -122.4194,
    "type": "viewpoint"
}

GET /waypoints?grid_x=45&grid_y=67
GET /waypoints/{id}
```

### 5.2 Route Discovery (Neo4j Pathfinding)

```python
POST /routes/discover
{
    "start_grid": [10, 20],
    "end_grid": [50, 80],
    "max_waypoints": 10
}

Response:
{
    "waypoints": [
        {"id": 1, "name": "Start", "grid": [10, 20]},
        {"id": 23, "name": "Cafe", "grid": [25, 35]},
        {"id": 89, "name": "End", "grid": [50, 80]}
    ],
    "total_distance_km": 245.6
}
```

### 5.3 Route Management

```python
POST /routes
{
    "name": "Coastal Loop",
    "waypoint_ids": [1, 23, 45, 89],
    "difficulty": "moderate"
}

GET /routes
GET /routes/{id}
```

### 5.4 Ride Logging

```python
POST /rides
{
    "rider_id": 1,
    "route_id": 5,
    "rating": 5
}

GET /riders/{id}/rides
```

---

## 6. Factory & Data Generation

### 6.1 Grid Population

Factories generate test data to populate the grid system:

- **GridFactory**: Creates waypoints scattered across the 100x100 grid
- **RiderFactory**: Creates test riders with random experience levels

### 6.2 CLI Seeding

```bash
python -m app.cli seed --waypoints 500 --riders 20
```

Result: 500 waypoints auto-connected via GRID_ADJACENT in Neo4j, ready for route discovery.

---

## 7. Why Grid System First, OSM Later?

**Grid System Benefits (Current):**
- Zero external dependencies
- Fast development and testing
- Predictable performance
- Focus on Neo4j graph queries

**OSM Migration (Future):**
- Real roads and distances
- Actual POIs from OpenStreetMap
- Seamless transition via abstraction layer

---

## 8. Why Hybrid Database?

**PostgreSQL:**
- ACID transactions for critical data
- Complex queries with JOINs
- Structured data storage

**Neo4j:**
- Native graph traversal
- Efficient pathfinding algorithms
- Pattern matching for recommendations

**Synchronization:** Both databases updated in same API transaction. PostgreSQL ID stored as `pg_id` in Neo4j for linking.

---

## 9. Future Enhancements

- Real-time GPS tracking during rides
- Weather-based route recommendations
- Social features (follow riders, group rides)
- OpenStreetMap integration for real roads
- Gamification (badges, leaderboards)
- Mobile app with offline support

---

## 10. Getting Started

### 10.1 Prerequisites

```bash
# Install dependencies
python >= 3.11
postgresql >= 15
neo4j >= 5.0
```

### 10.2 Setup

```bash
# Clone and install
git clone <repo>
cd RidersBuddy
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml

# Setup databases
# PostgreSQL: Create database 'ridersbuddy'
# Neo4j: Start instance on bolt://localhost:7687

# Run migrations
alembic upgrade head

# Seed data
python -m app.cli seed-database --grid-density medium --riders 100 --rides 1000

# Start server
uvicorn app.main:app --reload --port 8005
```

### Quick Test

```bash
# Discover route
curl -X POST http://localhost:8005/api/routes/discover \
  -H "Content-Type: application/json" \
  -d '{"start_grid": [10, 20], "end_grid": [50, 80], "max_waypoints": 15}'
```

---

## 13. Technology Stack

- **FastAPI** (Python 3.11+)
- **PostgreSQL** 15+ with SQLAlchemy 2.0
- **Neo4j** 5.x with official Python driver
- **Alembic** for migrations
- **Click** for CLI

---

## 14. Future Phases

### Phase 2: Social Features
- Follow system and riding buddies
- Route recommendations based on social graph

### Phase 3: Advanced Routing
- Multi-criteria pathfinding (scenic vs fast)
- Alternative route suggestions
- Waypoint type filters

### Phase 4: OSM Migration
- Real road data from OpenStreetMap
- Actual distances and road metadata

### Phase 5: Production Features
- Authentication, GPS tracking, mobile app

---

**Document Status:** Active Development  
**Last Updated:** February 19, 2026