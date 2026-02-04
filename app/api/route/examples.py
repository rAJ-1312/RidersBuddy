"""
Example data for route types to be used in API documentation (Swagger/OpenAPI)
"""

# Scenic Route Example
scenic_route_example = {
    "name": "Pacific Coast Highway",
    "route_type": "scenic",
    "start_location": "San Francisco, CA",
    "end_location": "Los Angeles, CA",
    "distance_km": 655.5,
    "difficulty": "EASY",
    "description": "One of the most beautiful coastal drives in the world with stunning ocean views",
    "scenic_points": [
        "Big Sur Coastline",
        "Bixby Bridge",
        "McWay Falls",
        "Monterey Bay",
        "Santa Barbara"
    ],
    "best_season": "Spring/Fall",
    "photography_spots": 15
}

# Highway Route Example
highway_route_example = {
    "name": "Interstate 95 North",
    "route_type": "highway",
    "start_location": "Miami, FL",
    "end_location": "New York, NY",
    "distance_km": 2145.0,
    "difficulty": "MODERATE",
    "description": "Major interstate highway connecting the East Coast cities",
    "speed_limit": 120,
    "toll_cost": 45.50,
    "rest_stops": [
        "Fort Pierce Service Plaza",
        "Port Orange Rest Area",
        "Georgia Welcome Center",
        "South Carolina I-95 Rest Stop",
        "Virginia Welcome Center",
        "Maryland House Travel Plaza"
    ],
    "lanes": 4
}

# Offroad Route Example
offroad_route_example = {
    "name": "Moab Slickrock Trail",
    "route_type": "offroad",
    "start_location": "Moab, UT",
    "end_location": "Moab, UT",
    "distance_km": 19.3,
    "difficulty": "EXTREME",
    "description": "Legendary technical trail on exposed slickrock requiring advanced skills",
    "terrain_type": "rocks",
    "min_bike_cc": 250,
    "technical_difficulty": 9,
    "requires_experience": True
}

# Mountain Route Example
mountain_route_example = {
    "name": "Stelvio Pass",
    "route_type": "mountain",
    "start_location": "Bormio, Italy",
    "end_location": "Prato allo Stelvio, Italy",
    "distance_km": 24.3,
    "difficulty": "HARD",
    "description": "One of the highest paved mountain passes in the Alps with 48 hairpin turns",
    "elevation_gain": 1533.0,
    "max_altitude": 2757.0,
    "hairpin_turns": 48,
    "oxygen_required": False
}

# Coastal Route Example
coastal_route_example = {
    "name": "Great Ocean Road",
    "route_type": "coastal",
    "start_location": "Torquay, Australia",
    "end_location": "Allansford, Australia",
    "distance_km": 243.0,
    "difficulty": "EASY",
    "description": "Spectacular coastal route featuring the famous Twelve Apostles rock formations",
    "beach_stops": [
        "Bells Beach",
        "Apollo Bay",
        "Loch Ard Gorge",
        "Port Campbell"
    ],
    "lighthouse_count": 3,
    "seafood_spots": [
        "Apollo Bay Fishermen's Co-op",
        "12 Rocks Cafe",
        "Chris's Beacon Point Restaurant"
    ],
    "ocean_view_percentage": 85
}

# Additional examples for variety

scenic_route_example_2 = {
    "name": "Blue Ridge Parkway",
    "route_type": "scenic",
    "start_location": "Cherokee, NC",
    "end_location": "Waynesboro, VA",
    "distance_km": 755.0,
    "difficulty": "MODERATE",
    "description": "America's favorite drive through the Appalachian Highlands",
    "scenic_points": [
        "Clingmans Dome",
        "Graveyard Fields",
        "Looking Glass Rock",
        "Grandfather Mountain",
        "Linn Cove Viaduct"
    ],
    "best_season": "Fall",
    "photography_spots": 22
}

highway_route_example_2 = {
    "name": "Autobahn A7",
    "route_type": "highway",
    "start_location": "Hamburg, Germany",
    "end_location": "Füssen, Germany",
    "distance_km": 963.0,
    "difficulty": "EASY",
    "description": "Longest German autobahn, some sections with no speed limit",
    "speed_limit": 0,  # No speed limit on certain sections
    "toll_cost": 0.0,  # No tolls in Germany
    "rest_stops": [
        "Raststätte Seevetal",
        "Raststätte Göttingen",
        "Raststätte Würzburg",
        "Raststätte Augsburg"
    ],
    "lanes": 3
}

offroad_route_example_2 = {
    "name": "Trans-Labrador Trail",
    "route_type": "offroad",
    "start_location": "Happy Valley-Goose Bay, NL",
    "end_location": "Churchill Falls, NL",
    "distance_km": 500.0,
    "difficulty": "HARD",
    "description": "Remote gravel road through the Labrador wilderness",
    "terrain_type": "gravel",
    "min_bike_cc": 650,
    "technical_difficulty": 6,
    "requires_experience": True
}

mountain_route_example_2 = {
    "name": "Grossglockner High Alpine Road",
    "route_type": "mountain",
    "start_location": "Bruck, Austria",
    "end_location": "Heiligenblut, Austria",
    "distance_km": 48.0,
    "difficulty": "MODERATE",
    "description": "Stunning alpine route with 36 hairpin bends and breathtaking views",
    "elevation_gain": 1985.0,
    "max_altitude": 2504.0,
    "hairpin_turns": 36,
    "oxygen_required": False
}

coastal_route_example_2 = {
    "name": "Amalfi Coast Road",
    "route_type": "coastal",
    "start_location": "Sorrento, Italy",
    "end_location": "Salerno, Italy",
    "distance_km": 50.0,
    "difficulty": "MODERATE",
    "description": "Dramatic coastal road carved into cliffs overlooking the Mediterranean",
    "beach_stops": [
        "Positano Beach",
        "Atrani Beach",
        "Maiori Beach"
    ],
    "lighthouse_count": 1,
    "seafood_spots": [
        "La Tagliata",
        "Ristorante Marina Grande",
        "Da Adolfo",
        "Il Pirata Restaurant"
    ],
    "ocean_view_percentage": 95
}

# Dictionary for easy access
ROUTE_EXAMPLES = {
    "scenic": [scenic_route_example, scenic_route_example_2],
    "highway": [highway_route_example, highway_route_example_2],
    "offroad": [offroad_route_example, offroad_route_example_2],
    "mountain": [mountain_route_example, mountain_route_example_2],
    "coastal": [coastal_route_example, coastal_route_example_2],
}

# Combined examples for general route creation endpoint
ALL_ROUTE_EXAMPLES = {
    "scenic_route": scenic_route_example,
    "highway_route": highway_route_example,
    "offroad_route": offroad_route_example,
    "mountain_route": mountain_route_example,
    "coastal_route": coastal_route_example,
}
