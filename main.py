from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import osmnx as ox
import networkx as nx
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="AccessibleRouteAPI",
    description="Routing + accessibility scoring for Kochi",
    version="1.0"
)

# -----------------------------------------------------
# CORS FIX — REQUIRED FOR FRONTEND TO CALL BACKEND
# -----------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows OPTIONS, GET, POST, etc.
    allow_headers=["*"],
)

# -----------------------------------------------------
# Data Models
# -----------------------------------------------------

class Coord(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Coord
    end: Coord

class RoutePoint(BaseModel):
    lat: float
    lng: float

class RouteResponse(BaseModel):
    distance_m: float
    distance_km: float
    accessibility_score: float
    accessibility_label: str
    points: List[RoutePoint]

# -----------------------------------------------------
# Load OSM Graph
# -----------------------------------------------------

print("Loading Kochi map graph, please wait...")
G = ox.graph_from_place("Kochi, India", network_type="walk")
G = ox.distance.add_edge_lengths(G)
print("Graph loaded with:", len(G.nodes), "nodes,", len(G.edges), "edges")

def nearest_node(lat, lng):
    return ox.distance.nearest_nodes(G, X=[lng], Y=[lat])[0]

def compute_mock_score(distance):
    if distance <= 1000:
        return 0.95, "Excellent"
    elif distance <= 2500:
        return 0.85, "Good"
    elif distance <= 4000:
        return 0.70, "Moderate"
    else:
        return 0.55, "Challenging"

# -----------------------------------------------------
# API Routes
# -----------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/route", response_model=RouteResponse)
def get_route(req: RouteRequest):
    # Find nearest nodes
    start_node = nearest_node(req.start.lat, req.start.lng)
    end_node = nearest_node(req.end.lat, req.end.lng)

    # Shortest path
    path_nodes = nx.shortest_path(G, start_node, end_node, weight="length")

    # Extract coordinates + compute distance
    points = []
    total_dist = 0

    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        edge_data = G.get_edge_data(u, v)[0]
        total_dist += float(edge_data.get("length", 0.0))

    for node in path_nodes:
        points.append(RoutePoint(
            lat=G.nodes[node]["y"],
            lng=G.nodes[node]["x"]
        ))

    score, label = compute_mock_score(total_dist)

    return RouteResponse(
        distance_m=total_dist,
        distance_km=round(total_dist / 1000, 2),
        accessibility_score=score,
        accessibility_label=label,
        points=points
    )

