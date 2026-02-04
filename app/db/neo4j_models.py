from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    FloatProperty,
    RelationshipTo,
    RelationshipFrom,
)


class RiderNode(StructuredNode):
    postgres_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(unique_index=True, required=True)
    experience_level = StringProperty(required=True)
    joined_at = DateTimeProperty(required=True)
    
    bikes = RelationshipTo('BikeNode', 'OWNS')
    rides = RelationshipTo('RideNode', 'COMPLETED')


class BikeNode(StructuredNode):
    postgres_id = IntegerProperty(unique_index=True, required=True)
    model = StringProperty(required=True)
    brand = StringProperty(required=True)
    year = IntegerProperty(required=True)
    engine_cc = IntegerProperty(required=True)


class RouteNode(StructuredNode):
    postgres_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(unique_index=True, required=True)
    start_location = StringProperty(required=True)
    end_location = StringProperty(required=True)
    distance_km = FloatProperty(required=True)
    difficulty = StringProperty(required=True)
    created_at = DateTimeProperty(required=True)
    
    rides = RelationshipFrom('RideNode', 'ON_ROUTE')


class RideNode(StructuredNode):
    postgres_id = IntegerProperty(unique_index=True, required=True)
    completed_at = DateTimeProperty(required=True)
    duration_minutes = IntegerProperty()
    
    rider = RelationshipFrom('RiderNode', 'COMPLETED')
    route = RelationshipTo('RouteNode', 'ON_ROUTE')
    bike = RelationshipTo('BikeNode', 'USED_BIKE')
