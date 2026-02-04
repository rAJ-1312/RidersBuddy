from contextlib import asynccontextmanager
from .db.database import engine, close_neo4j_driver, close_postgres_engine, get_neo4j_session
from .db import postgres_models as models
from neo4j import Session as Neo4jSession
from fastapi import FastAPI, Depends
from app.api.routes import api_router
from app.db.neo4j_models import RiderNode, BikeNode


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    close_postgres_engine()
    close_neo4j_driver()


app = FastAPI(lifespan=lifespan)

models.Base.metadata.create_all(bind=engine)

app.include_router(api_router)


# Neo4j test endpoints
@app.get("/neo4j/health", tags=["Neo4j Learn Basics"])
def neo4j_health(neo4j_session: Neo4jSession = Depends(get_neo4j_session)):
    """Test Neo4j connection by running a simple query."""
    result = neo4j_session.run("RETURN 'Neo4j connection successful!' AS message")
    record = result.single()
    return {"status": "ok", "message": record["message"]}


@app.post("/neo4j/nodes", tags=["Neo4j Learn Basics"])
def create_test_node(
    name: str,
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Create a test node in Neo4j."""
    result = neo4j_session.run(
        "CREATE (n:TestNode {name: $name, created_at: datetime()}) RETURN n",
        name=name,
    )
    record = result.single()
    node = record["n"]
    return {"id": node.element_id, "labels": list(node.labels), "properties": dict(node)}


@app.get("/neo4j/nodes", tags=["Neo4j Learn Basics"])
def get_test_nodes(neo4j_session: Neo4jSession = Depends(get_neo4j_session)):
    """Get all test nodes from Neo4j."""
    result = neo4j_session.run("MATCH (n:TestNode) RETURN n")
    nodes = []
    for record in result:
        node = record["n"]
        nodes.append({
            "id": node.element_id,
            "labels": list(node.labels),
            "properties": dict(node),
        })
    return {"nodes": nodes, "count": len(nodes)}


@app.post("/neo4j/relationships", tags=["Neo4j Learn Basics"])
def create_relationship(
    from_node_name: str,
    to_node_name: str,
    relationship_type: str = "CONNECTED_TO",
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Create a relationship between two nodes by their names."""
    result = neo4j_session.run(
        """
        MATCH (from:TestNode {name: $from_name})
        MATCH (to:TestNode {name: $to_name})
        CREATE (from)-[r:%s]->(to)
        RETURN from, r, to
        """ % relationship_type,
        from_name=from_node_name,
        to_name=to_node_name,
    )
    record = result.single()
    
    if not record:
        return {"error": "One or both nodes not found"}
    
    from_node = record["from"]
    relationship = record["r"]
    to_node = record["to"]
    
    return {
        "from_node": {"id": from_node.element_id, "name": dict(from_node)["name"]},
        "relationship": {"type": relationship.type, "id": relationship.element_id},
        "to_node": {"id": to_node.element_id, "name": dict(to_node)["name"]},
    }


@app.get("/neo4j/relationships", tags=["Neo4j Learn Basics"])
def get_relationships(neo4j_session: Neo4jSession = Depends(get_neo4j_session)):
    """Get all relationships between TestNodes."""
    result = neo4j_session.run(
        "MATCH (from:TestNode)-[r]->(to:TestNode) RETURN from, r, to"
    )
    
    relationships = []
    for record in result:
        from_node = record["from"]
        relationship = record["r"]
        to_node = record["to"]
        
        relationships.append({
            "from_node": {"id": from_node.element_id, "name": dict(from_node)["name"]},
            "relationship": {"type": relationship.type, "id": relationship.element_id},
            "to_node": {"id": to_node.element_id, "name": dict(to_node)["name"]},
        })
    
    return {"relationships": relationships, "count": len(relationships)}




