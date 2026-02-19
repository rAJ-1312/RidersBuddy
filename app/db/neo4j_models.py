from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    FloatProperty,
)


class RiderNode(StructuredNode):
    pg_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    experience_level = StringProperty(required=True)


class WaypointNode(StructuredNode):
    pg_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    grid_x = IntegerProperty(required=True)
    grid_y = IntegerProperty(required=True)
    lat = FloatProperty(required=True)
    lng = FloatProperty(required=True)
    type = StringProperty(required=True)


class RouteNode(StructuredNode):
    pg_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    difficulty = StringProperty(required=True)
    distance_km = FloatProperty(required=True)
