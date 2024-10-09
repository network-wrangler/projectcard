"""Change type models for project card."""

from typing import Annotated, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field

from .selections import SelectFacility, SelectRoadLinks, SelectRoadNodes, SelectTransitTrips
from .structs import (
    RoadLink,
    RoadNode,
    RoadwayPropertyChange,
    TransitPropertyChange_PropertyChanges,
    TransitRoute,
    TransitRoutingChange_Routing,
)


class RoadwayDeletion(BaseModel):
    """Requirements for describing roadway deletion project card (e.g. to delete).

    Attributes:
        links (Optional[SelectRoadLinks]): Roadway links to delete.
        nodes (Optional[SelectRoadNodes]): Roadway nodes to delete.
        clean_shapes (bool): If True, will clean unused roadway shapes associated with the deleted links
            if they are not otherwise being used. Defaults to False.
        clean_nodes (bool): If True, will clean unused roadway nodes associated with the deleted links
            if they are not otherwise being used. Defaults to False.

    !!! Example "Example Roadway Deletion"
        ```yaml
        roadway_deletion:
            links:
                model_link_id:
                - 281
                - 477533
            nodes:
                model_node_id:
                - 314159
            clean_shapes: true
            clean_nodes: false
        ```
    """

    require_any_of: ClassVar = [["links", "nodes"]]
    model_config = ConfigDict(extra="forbid")

    links: Optional[SelectRoadLinks] = None
    nodes: Optional[SelectRoadNodes] = None
    clean_shapes: bool = False
    clean_nodes: bool = False


class RoadwayAddition(BaseModel):
    """Requirements for describing roadway addition project card.

    Attributes:
        links (Optional[list[RoadLink]]): Roadway links to add. Must have at least one link.
        nodes (Optional[list[RoadNode]]): Roadway nodes to add. Must have at least one node.

    !!! Example "Example Roadway Addition"
        ```yaml
        roadway_addition:
            links:
                - A: 269066
                B: 268932
                name: new neighborhood st
                roadway: residential
                lanes: 1
                model_link_id: 404982
                - A: 268932
                B: 269066
                name: new neighborhood st
                roadway: residential
                lanes: 1
                model_link_id: 407042
            nodes:
                - model_node_id: 268932
                    latitude: 37.7749
                    longitude: -122.4194
                - model_node_id: 269066
                    latitude: 37.7749
                    longitude: -122.4194
        ```
    """

    require_any_of: ClassVar = [["links", "nodes"]]
    model_config = ConfigDict(extra="forbid")

    links: Annotated[Optional[list[RoadLink]], Field(min_length=1)]
    nodes: Annotated[Optional[list[RoadNode]], Field(min_length=1)]


class RoadwayPropertyChanges(BaseModel):
    """Value for setting property changes for a time of day and category.

    Attributes:
        facility (SelectFacility): Selection of roadway links to change properties for.
        property_changes (dict[str, RoadwayPropertyChange]): Property changes to apply to the selection. Must have at least one property change.

    !!! Example "Example Roadway Property Change"
        ```yaml
        roadway_property_change:
            facility:
                links:
                    modes: ['drive','bike']
                    osm_link_id:
                        - '1234'
                        - '2345'
                from:
                    osm_node_id: '4321'
                to:
                    osm_node_id: '4322'
            property_changes:
                lanes:
                    existing: 3
                    change: -1
                    existing_value_conflict: error
                bicycle_facility:
                    existing: 1
                    set: 3
                    existing_value_conflict: skip
        ```
    """

    model_config = ConfigDict(extra="forbid")

    facility: SelectFacility
    property_changes: Annotated[dict[str, RoadwayPropertyChange], Field(min_length=1)]


class TransitPropertyChange(BaseModel):
    """Value for setting property change for a time of day and category.

    Attributes:
        service (SelectTransitTrips): Selection of transit trips to change properties for.
        property_changes (dict[str, TransitPropertyChange]): List of property changes to apply.

    !!! Example "Example Transit Property Change"
        ```yaml
        transit_property_change:
            service:
                trip_properties:
                trip_id:
                    - 14940701-JUN19-MVS-BUS-Weekday-01
                timespans:
                - ['06:00:00', '09:00:00']
            property_changes:
                headway_secs:
                    set: 900
        ```
    """

    model_config = ConfigDict(extra="forbid")

    service: SelectTransitTrips
    property_changes: Annotated[
        dict[str, TransitPropertyChange_PropertyChanges], Field(min_length=1)
    ]


class TransitRoutingChange(BaseModel):
    """Value for setting routing change for transit.

    Attributes:
        service (SelectTransitTrips): Selection of transit trips to change routing for.
        transit_routing_change (TransitRoutingChange): Existing and changed routing as denoted as a list of nodes with
            nodes where the route doesn't stop noted as negative integers.

    !!! Example "Example Transit Routing Change"
        ```yaml
        transit_routing_change:
            service:
                trip_properties:
                route_id:
                    - 294-111
                direction_id: 1
            routing:
                existing:
                - 1
                - 2
                set:
                - 1
                - -11
                - -12
                - 2
        ```
    """

    model_config = ConfigDict(extra="forbid")

    service: SelectTransitTrips
    routing: TransitRoutingChange_Routing


class TransitServiceDeletion(BaseModel):
    """Requirements for describing transit service deletion project card (e.g. to delete).

    Attributes:
        service (SelectTransitTrips): Selection of transit trips to delete.
        clean_shapes (Optional[bool]): If True, will clean unused transit shapes associated with the deleted trips
            if they are not otherwise being used. Defaults to False.
        clean_routes (Optional[bool]): If True, will clean unused routes associated with the deleted trips if they
            are not otherwise being used. Defaults to False.

    !!! Example "Example Transit Service Deletion"
        ```yaml
        transit_service_deletion:
            service:
                trip_properties:
                route_short_name: "green"
                timespans:
                - ['06:00:00', '09:00:00']
            clean_shapes: false
            clean_routes: true
        ```
    """

    model_config = ConfigDict(extra="forbid")

    service: SelectTransitTrips
    clean_shapes: Optional[bool] = False
    clean_routes: Optional[bool] = False


class TransitRouteAddition(BaseModel):
    """Requirements for describing transit route addition project card.

    Attributes:
        routes (list[TransitRoute]): List of transit routes to be added. Must have at least one route.

    !!! Example "Example Transit Route Addition"
        ```yaml
        transit_route_addition:
            routes:
                - route_id: abc
                route_long_name: green_line
                route_short_name: green
                route_type: 3
                agency_id: The Bus
                trips:
                    - direction_id: 0
                    headway_secs:
                        - ('6:00','12:00'): 600
                        - ('12:00','13:00'): 900
                    routing:
                        - 1:
                            stop: true #when stop is set to True, defaults to allow both boarding and alighting
                        - 2
                        - 3
                        - 4:
                            stop: true # default to False, specify only when stopping
                            alight: false  # default to True, specify only when not default
                        - 5
                        - 6:
                            stop: true

        ```
    """

    model_config = ConfigDict(extra="forbid")

    routes: Annotated[list[TransitRoute], Field(min_length=1)]


class ChangeTypes(BaseModel):
    """Union of all change types."""

    model_config = ConfigDict(extra="forbid")

    require_one_of: ClassVar = [
        [
            "roadway_property_change",
            "roadway_deletion",
            "roadway_addition",
            "transit_property_change",
            "transit_routing_change",
            "transit_service_deletion",
            "transit_route_addition",
            "pycode",
        ],
    ]

    roadway_property_change: Optional[RoadwayPropertyChanges]
    roadway_deletion: Optional[RoadwayDeletion]
    roadway_addition: Optional[RoadwayAddition]
    transit_property_change: Optional[TransitPropertyChange]
    transit_routing_change: Optional[TransitRoutingChange]
    transit_service_deletion: Optional[TransitServiceDeletion]
    transit_route_addition: Optional[TransitRouteAddition]
    pycode: Optional[str]
