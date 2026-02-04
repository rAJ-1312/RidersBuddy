# 🏍️ Biker Routes & Ride Network - Full Plan

## Overview

A social platform for bikers to log rides, discover routes, find riding buddies, and plan group rides. **PostgreSQL** handles the structured data (riders, bikes, routes, ride logs), while **Neo4j** powers the social graph and route connections.

---

## 📊 Data Architecture

### PostgreSQL (Structured Data)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `riders` | User profiles | id, name, experience_level, joined_at |
| `bikes` | Motorcycle inventory | id, owner_id, brand, model, year, engine_cc |
| `routes` | Ride routes | id, name, start_location, end_location, distance_km, difficulty, terrain_type |
| `ride_logs` | Individual ride records | id, rider_id, bike_id, route_id, date, duration_mins, fuel_used, notes |
| `locations` | Waypoints/destinations | id, name, lat, lng, type (city, viewpoint, fuel_station, restaurant) |

### Neo4j (Relationships & Graph)

```cypher
(:Rider {pg_id})
    -[:OWNS]-> (:Bike {pg_id})
    -[:RODE_WITH]-> (:Rider)
    -[:FOLLOWS]-> (:Rider)
    -[:COMPLETED]-> (:Route {pg_id})
    -[:WANTS_TO_RIDE]-> (:Route)

(:Route {pg_id})
    -[:STARTS_AT]-> (:Location {pg_id})
    -[:ENDS_AT]-> (:Location {pg_id})
    -[:PASSES_THROUGH]-> (:Location)
    -[:CONNECTS_TO]-> (:Route)  // For multi-route trips

(:Location {pg_id})
    -[:NEAR]-> (:Location)
```

---

## 🎯 Feature Breakdown

### **Phase 1: Core CRUD (PostgreSQL Focus)**

| Feature | Endpoints | What You'll Learn |
|---------|-----------|-------------------|
| Rider Management | `POST/GET /riders` | Basic CRUD, user profiles |
| Bike Garage | `POST/GET /riders/{id}/bikes` | One-to-many relationships |
| Route Catalog | `POST/GET /routes` | Route data modeling |
| Ride Logging | `POST/GET /rides` | Foreign keys, joins |

### **Phase 2: Social Graph (Neo4j Focus)**

| Feature | Neo4j Concepts | What You'll Learn |
|---------|----------------|-------------------|
| Follow riders | `CREATE (:Rider)-[:FOLLOWS]->(:Rider)` | Basic relationships |
| Log riding buddies | `CREATE (:Rider)-[:RODE_WITH {date}]->(:Rider)` | Relationship properties |
| Sync data to Neo4j | Create nodes with `pg_id` property | Hybrid database pattern |

### **Phase 3: Graph Queries (The Fun Part! 🎉)**

| Query | Cypher Concept | Example |
|-------|----------------|---------|
| "Who have I ridden with?" | Direct relationships | `MATCH (me)-[:RODE_WITH]->(buddy)` |
| "Friends of friends" | 2-hop traversal | `MATCH (me)-[:FOLLOWS*2]->(fof)` |
| "Find riders who've done Route X" | Pattern matching | `MATCH (r:Rider)-[:COMPLETED]->(route {name: 'Mountain Loop'})` |
| "Recommend routes" | Based on similar riders | `MATCH (me)-[:FOLLOWS]->(friend)-[:COMPLETED]->(route) WHERE NOT (me)-[:COMPLETED]->(route)` |
| "Plan a multi-route trip" | Path finding | `MATCH path = (start:Location)-[:CONNECTS_TO*]->(end:Location)` |
| "Riding circles" | Community detection | Find clusters of riders who frequently ride together |

---

## 🗂️ File Structure

```
app/
├── main.py              # FastAPI app & endpoints
├── database.py          # PostgreSQL + Neo4j connections (✅ exists)
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py              # PostgreSQL CRUD operations
├── graph.py             # Neo4j operations (NEW)
├── sync.py              # Sync PostgreSQL → Neo4j (NEW)
└── deps.py              # Dependencies (✅ exists)
```

---

## 📋 Implementation Phases

### **Phase 1: PostgreSQL Models**

```python
# Models: Rider, Bike, Route, Location, RideLog
# Relationships: Rider has many Bikes, RideLog links Rider+Bike+Route
```

**Endpoints:**
- `POST /riders` - Create rider profile
- `GET /riders` - List all riders  
- `GET /riders/{id}` - List rider with id={id} 
- `POST /riders/{id}/bikes` - Add bike to garage
- `GET /riders/{id}/bikes` - View garage
- `GET /riders/{id}/bikes/{bike_id}` - View bike
- `DELETE /riders/{id}` - Delete a rider
- `DELETE /riders/{id}/bikes/{bike_id}` - Remove a bike
- `POST /routes` - Create a route
- `GET /routes` - List routes (filter by difficulty, distance)
- `POST /rides` - Log a completed ride
- `GET /riders/{id}/rides` - View ride history

---

### **Phase 2: Neo4j Social Graph**

**Sync Pattern:**
When you create a Rider/Route/Location in PostgreSQL → also create a node in Neo4j with `pg_id` property to link them.

**Endpoints:**
- `POST /riders/{id}/follow/{target_id}` - Follow a rider
- `GET /riders/{id}/following` - Who I follow
- `GET /riders/{id}/followers` - Who follows me
- `POST /rides/{ride_id}/buddies` - Tag riders you rode with
- `GET /riders/{id}/riding-buddies` - All buddies from Neo4j

---

### **Phase 3: Smart Queries (Graph Magic ✨)**

**Endpoints:**
- `GET /riders/{id}/recommended-buddies` - Friends of friends who ride similar routes
- `GET /riders/{id}/recommended-routes` - Routes my network has completed that I haven't
- `GET /routes/{id}/riders` - Who has completed this route?
- `GET /routes/plan?from=LocationA&to=LocationB` - Find connected routes for a trip
- `GET /riders/{id}/six-degrees/{target_id}` - Shortest path between two riders

---

## 🧠 Neo4j Concepts You'll Learn

| Concept | Where You'll Use It |
|---------|---------------------|
| `CREATE` nodes | Syncing riders/routes from PostgreSQL |
| `MATCH` patterns | Finding riders, routes, relationships |
| `CREATE` relationships | Following, rode-with, completed |
| Relationship properties | `[:RODE_WITH {date: '2026-01-21'}]` |
| Variable-length paths | `[:FOLLOWS*1..3]` for friends of friends |
| `WHERE NOT` | Recommendations (routes I haven't done) |
| `shortestPath()` | Six degrees between riders |
| `RETURN` aggregations | `count()`, `collect()` for stats |
| Indexes & constraints | `CREATE CONSTRAINT ON (r:Rider) ASSERT r.pg_id IS UNIQUE` |

---

## 🚀 Example User Journey

1. **Raj signs up** → Rider created in PostgreSQL + Neo4j
2. **Adds his bike** → Bike in PostgreSQL, `(:Rider)-[:OWNS]->(:Bike)` in Neo4j
3. **Discovers "Coastal Highway" route** → Browses routes from PostgreSQL
4. **Logs the ride** → RideLog in PostgreSQL, `(:Rider)-[:COMPLETED]->(:Route)` in Neo4j
5. **Tags his buddy Amit** → `(:Raj)-[:RODE_WITH]->(:Amit)` in Neo4j
6. **Follows Amit** → `(:Raj)-[:FOLLOWS]->(:Amit)` in Neo4j
7. **Gets recommendations** → Neo4j returns routes Amit completed that Raj hasn't
8. **Plans a trip** → Neo4j finds connected routes from City A to City B

---

## 📈 Stretch Goals (When You're Ready)

- **Leaderboards** - Most routes completed, most km ridden
- **Route reviews/ratings** - Store in PostgreSQL, aggregate in queries
- **Group ride planning** - Event scheduling with RSVP
- **Fuel tracking** - MPG calculations per bike
- **Maintenance reminders** - Based on km ridden
- **Heat maps** - Popular routes visualization

---

## 🛠️ Getting Started

1. Start with Phase 1 - Build PostgreSQL models and basic CRUD
2. Test with sample data
3. Move to Phase 2 - Add Neo4j sync and social features
4. Phase 3 - Implement graph-powered recommendations

**Ready to ride! 🏍️💨**