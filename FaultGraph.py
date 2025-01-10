import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import rdflib
from rdflib import URIRef,Literal
from rdflib.namespace import RDF,FOAF

class FaultGraph:
    # Constructor
    def __init__(self,shapefile_path,namespace):
        self.__shapefile_path = shapefile_path
        self.__namespace = namespace
        self.__g = rdflib.Graph()
        self.__EX = rdflib.Namespace(namespace)
        self.__G=nx.DiGraph()
        #Visualization graph
        self.__showG = nx.DiGraph()
    #  Main method to generate the knowledge graph
    def generate(self):
        self.__ridges_gdf = self.load_shapefile(self.__shapefile_path)
        self.generate_knowledge_graph(self.__ridges_gdf,self.__g)
    # Main method to sort the graph
    def sort(self):
        self.sort_knowledge_gragh(self.__g)
    # Main method to export the RDF file
    def export_rdf(self,path):
        self.__g.serialize(destination=path,format="xml")
        print("rdf generation is complete!")
    # Main method to show the sorted result
    def show(self):
        pos = nx.spring_layout(self.__showG)
        for node in self.__showG.nodes:
            x = self.__showG.nodes[node]['x']
            y = self.__showG.nodes[node]['y']
            pos[node] = (y,x*2)
        plt.figure(figsize=(16, 10))
        plt.title("Fault Temporal Sequence Visualization")
        nx.draw(self.__showG,pos, with_labels=True, node_size=65, node_color='lightgreen', font_size=5)
        edge_labels = nx.get_edge_attributes(self.__showG,"relation")
        nx.draw_networkx_edge_labels(self.__showG,pos,edge_labels=edge_labels,font_size=8)
        plt.show()
        print("Drawing is complete!")

    #Check the 'cutting_through' relation
    def is_cutting_through(self,geom1, geom2):
        """
        Check if fault1 is cutting through fault2, adapted for MultiLineString
        """

        # Ensure geom1 and geom2 are LineString or MultiLineString
        geom1_parts = geom1.geoms if isinstance(geom1, MultiLineString) else [geom1]
        geom2_parts = geom2.geoms if isinstance(geom2, MultiLineString) else [geom2]

        # Traverse each part of geom1, as it might contain multiple lines
        for i in range(len(geom1_parts)):
            part1 = geom1_parts[i]
            # Get the start and end coordinates of the segment
            x1_s, y1_s = part1.coords[0]
            x1_e, y1_e = part1.coords[-1]
            for j in range(len(geom1_parts)):
                part2 = geom1_parts[j]
                if i == len(geom1_parts) - 1:
                    break
                # Move to the next line segment
                if j == i + 1:
                    # Get the start and end coordinates of this line segment
                    x2_s, y2_s = part2.coords[0]
                    x2_e, y2_e = part2.coords[-1]
                    # Determine which nodes to use for the start and end points
                    if (x1_s < x2_s and x1_e < x2_e) or (x1_s > x2_s and x1_e > x2_e):
                        if (x1_s > x1_e and x1_s < x2_s and x2_s > x2_e) or (
                                x1_s < x1_e and x1_s > x2_s and x2_s < x2_e):
                            flag1 = flag2 = 1
                        elif (x1_s > x1_e and x1_s < x2_s and x2_s < x2_e) or (
                                x1_s < x1_e and x1_s > x2_s and x2_s > x2_e):
                            flag1 = 1
                            flag2 = 0
                        elif (x1_s > x1_e and x1_s > x2_s and x2_s > x2_e) or (
                                x1_s < x1_e and x1_s < x2_s and x2_s < x2_e):
                            flag1 = 0
                            flag2 = 0
                        elif (x1_s > x1_e and x1_s < x2_s and x2_s > x2_e) or (
                                x1_s < x1_e and x1_s > x2_s and x2_s < x2_e):
                            flag1 = 0
                            flag2 = 1
                        else:
                            break
                    else:
                        if (y1_s < y2_s and y1_e < y2_e) or (y1_s > y2_s and y1_e > y2_e):
                            if (y1_s > y1_e and y1_s < y2_s and y2_s > y2_e) or (
                                    y1_s < y1_e and y1_s > y2_s and y2_s < y2_e):
                                flag1 = flag2 = 1
                            elif (y1_s > y1_e and y1_s < y2_s and y2_s < y2_e) or (
                                    y1_s < y1_e and y1_s > y2_s and y2_s > y2_e):
                                flag1 = 1
                                flag2 = 0
                            elif (y1_s > y1_e and y1_s > y2_s and y2_s > y2_e) or (
                                    y1_s < y1_e and y1_s < y2_s and y2_s < y2_e):
                                flag1 = 0
                                flag2 = 0
                            elif (y1_s > y1_e and y1_s < y2_s and y2_s > y2_e) or (
                                    y1_s < y1_e and y1_s > y2_s and y2_s < y2_e):
                                flag1 = 0
                                flag2 = 1

                            else:
                                break
                        else:
                            break
                    # Select the correct start and end nodes based on the flags
                    if flag1 == 0 and flag2 == 0:
                        start_point = Point(part1.coords[-1])
                        end_point = Point(part2.coords[0])
                    elif flag1 == 1 and flag2 == 1:

                        start_point = Point(part1.coords[0])
                        end_point = Point(part2.coords[-1])
                    elif flag1 == 0 and flag2 == 1:
                        start_point = Point(part1.coords[-1])
                        end_point = Point(part2.coords[-1])
                    elif flag1 == 1 and flag2 == 0:
                        start_point = Point(part1.coords[0])
                        end_point = Point(part2.coords[0])
                    if start_point == end_point:
                        break
                    # Use geographic coordinate system to avoid issues with the map splitting at -180 to 180 degrees
                    if start_point.x * end_point.x < 0 and abs(start_point.x - end_point.x) > 100:
                        break
                    # Check if the line between start_point and end_point intersects part of geom2
                    for part in geom2_parts:
                        line_between = LineString([start_point, end_point])
                        if line_between.intersects(part):
                            return True
                    break
        return False

    # Helper function to check if a point is an endpoint of a geometry
    def is_endpoint(self,geometry, point):
        if isinstance(geometry, LineString):
            return point.equals(Point(geometry.coords[0])) or point.equals(Point(geometry.coords[-1]))
        elif isinstance(geometry, MultiLineString):
            if (point.equals(Point(geometry.geoms[0].coords[0])) or point.equals(Point(geometry.geoms[0].coords[-1]))
                    or point.equals(Point(geometry.geoms[-1].coords[0])) or point.equals(
                        Point(geometry.geoms[-1].coords[-1]))):
                return True
        return False

    # Load shapefile
    def load_shapefile(self,file_path):
        gdf = gpd.read_file(file_path)
        # Filter ridges type faults (can be modified as needed)
        gdf = gdf[gdf["Type"] == "ridges"]
        # Generate unique ID
        gdf["id"] = gdf.index.astype(str)
        return gdf

    # Determine the relationship between faults
    def determine_relation(self,geom1, geom2):
        """
        Determine the geometric relationship between two faults:
        - Mutually cutting: Both faults intersect and terminate at the intersection.
        - Cutting off: One fault is truncated by another fault.
        - Cutting through: One fault passes through another without termination.
        - No cutting: The two faults have no intersection.
        """

        intersection = geom1.intersection(geom2)
        if geom1.geom_type == "MultiLineString" and self.is_cutting_through(geom1, geom2):
            return "CUTTING_THROUGH"
        else:
            if geom1.intersects(geom2):
                if self.is_endpoint(geom1, intersection) and not self.is_endpoint(geom2, intersection):
                    return "CUTTING_OFF"
                elif not self.is_endpoint(geom1, intersection) and not self.is_endpoint(geom2, intersection):
                    return "MUTUALLY_CUTTING"
            else:
                return "NO_CUTTING"

        return "NO_CUTTING"

    # Create fault nodes in the RDF graph
    def create_fault(self,graph, fault_type, fault_id):
        EX = self.__EX
        namespace = self.__namespace
        node_uri = URIRef(namespace+fault_id)
        graph.add((node_uri, RDF.type, URIRef(namespace+"Fault")))  # Add Type
        graph.add((node_uri, EX.name, Literal(fault_id)))  # Adding Properties
        graph.add((node_uri, EX.type, Literal(fault_type)))  # Adding Properties
        graph.add((node_uri, EX.id, Literal(fault_id)))  # Adding Properties

    # Create relations between faults in the RDF graph
    def create_relation(self,graph, fault_id1, fault_id2, relation_type):
        namespace = self.__namespace
        start_node_uri = URIRef(namespace+fault_id1)
        end_node_uri = URIRef(namespace+fault_id2)
        relationship_type = URIRef(namespace+relation_type)
        graph.add((start_node_uri, relationship_type, end_node_uri))
        self.__G.add_edge(fault_id1, fault_id2, relation=relation_type)

    def generate_knowledge_graph(self,gdf, graph):
        """
        Sort the graph by temporal order using topological sorting.
        """
        # Creating a Fault Node
        for _, row in gdf.iterrows():
            self.create_fault(graph, row["Type"], row["id"])

        for i, row1 in self.__ridges_gdf.iterrows():
            for j, row2 in self.__ridges_gdf.iterrows():
                relation_type = self.determine_relation(row1["geometry"], row2["geometry"])
                print(f"Fault {row1['id']} and Fault {row2['id']} have relation: {relation_type}")
                if relation_type != "NO_CUTTING":
                    if relation_type == "MUTUALLY_CUTTING":
                        if i < j:
                            self.create_relation(graph, row1["id"], row2["id"], "equal_to")
                    else:
                        if i != j:
                            # The CUTTING_THROUGH and CUTTING_OFF relationships are unary
                            if (relation_type == "CUTTING_THROUGH"):
                                self.create_relation(graph, row2["id"], row1["id"], "younger_than")
                            elif (relation_type == "CUTTING_OFF"):
                                self.create_relation(graph, row1["id"], row2["id"], "younger_than")

    # Process equal relations in the graph
    def process_equal_to(self,graph):
        """Handling equal_to relationships, merging equal nodes into groups"""
        equal_groups = []  # Save Equivalent Node Groups
        visited = set()

        for node in graph.nodes:
            if node not in visited:
                # Find all nodes connected via equal_to
                group = set()
                stack = [node]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        group.add(current)
                        # Iterate over the equal_to relationships connected to the current node
                        for neighbor in graph.successors(current):
                            if graph.edges[current, neighbor]["relation"] == "equal_to":
                                stack.append(neighbor)
                        for neighbor in graph.predecessors(current):
                            if graph.edges[neighbor, current]["relation"] == "equal_to":
                                stack.append(neighbor)
                if group:
                    equal_groups.append(group)

        # Merge groups of equivalence nodes and replace equivalence relations in the graph
        node_mapping = {}
        for group_id, group in enumerate(equal_groups):
            group_name = f"Group_{group_id}"
            for node in group:
                node_mapping[node] = group_name

        # Create new directed graph, merge equivalent nodes
        new_graph = nx.DiGraph()
        for source, target, data in graph.edges(data=True):
            source_group = node_mapping.get(source, source)
            target_group = node_mapping.get(target, target)
            if source_group != target_group:  # Ignore edges inside the group
                new_graph.add_edge(source_group, target_group, relation=data["relation"])

        return new_graph, node_mapping, equal_groups

    # Assign temporal order to faults
    def assign_temporal_order(self,graph):
        """
        Sort the graph by temporal order using topological sorting.
        """
        temporal_order = {}  # Store the chronological order of each node
        for node in nx.topological_sort(graph):  # Traversing nodes based on topological ordering
            # Get the temporal_order of all predecessor nodes.
            predecessors = list(graph.predecessors(node))
            if predecessors:
                max_order = max(temporal_order[p] for p in predecessors)
                temporal_order[node] = max_order + 1
            else:
                temporal_order[node] = 0  # The temporal_order of the starting point is 0
        return temporal_order

    # Check for conflicts in the graph
    def check_conflicts(self,graph):
        temporal_order = {}  # Store the chronological order of each node (if known)
        equal_groups = []  # Storing groups of nodes through equal_to relationships

        # Handling equal_to relationships, merging equivalence groups
        visited = set()
        for node in graph.nodes:
            if node not in visited:
                group = set()
                stack = [node]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        group.add(current)
                        for neighbor in graph.successors(current):
                            if graph.edges[current, neighbor]["relation"] == "equal_to":
                                stack.append(neighbor)
                        for neighbor in graph.predecessors(current):
                            if graph.edges[neighbor, current]["relation"] == "equal_to":
                                stack.append(neighbor)
                if group:
                    equal_groups.append(group)

        # Check if equal_to and younger_than are in conflict.
        for source, target, data in graph.edges(data=True):
            if data["relation"] == "younger_than":
                # Check if source and target are in the same equivalence group
                for group in equal_groups:
                    if source in group and target in group:
                        return False
        return True

    # There is only one relationship, equal, in the processing map relationship.
    def handle_equal_only(self,graph, node_mapping):
        """If there is only an equal_to relationship, assign each group a default temporal_order"""
        temporal_order = {}
        if len(graph.edges) == 0:  # There are no edges in the diagram
            order = 0
            for group in set(node_mapping.values()):
                for node, group_name in node_mapping.items():
                    if group_name == group:
                        temporal_order[node] = order
                order += 1
        return temporal_order

    # Assign field_order, temporal_order to be the same, sort by id.
    def assign_field_order(self,final_temporal_order):
        """Assign field_order to each temporal_order"""
        field_order = {}
        groups = defaultdict(list)
        for key, value in final_temporal_order.items():
            groups[value].append(key)
        # Sort the keys in each group from smallest to largest.
        sorted_groups = {k: sorted(v, key=int) for k, v in groups.items()}
        max_len = 0
        for group, nodes in sorted_groups.items():
            order = {}
            lens = len(nodes)
            if lens > max_len:
                max_len = lens
            for idx in range(len(nodes)):
                order["temporal_order"] = group
                order["field_order"] = idx
                field_order[nodes[idx]] = {"temporal_order": group, "field_order": idx}
        return field_order, max_len

    #Subgraph ordering
    def sort_subgraph(self,subgraph):
        edges = []
        final_temporal_order = {}
        for source, target, data in subgraph.edges(data=True):
            edges.append((source, target, data.get("relation")))
        G = nx.DiGraph()
        for source, target, relation in edges:
            G.add_edge(source, target, relation=relation)
        processed_G, node_mapping, equal_groups = self.process_equal_to(G)
        if len(processed_G.edges) == 0:  # There are no edges in the diagram
            final_temporal_order = self.handle_equal_only(processed_G, node_mapping)
            # field_order = assign_field_order(equal_groups,final_temporal_order,node_mapping)
        else:
            temporal_order = self.assign_temporal_order(processed_G)

            for node, group in node_mapping.items():
                final_temporal_order[node] = temporal_order[group]
        field_order, max_len = self.assign_field_order(final_temporal_order)

        # # output result
        # print("Node Temporal and Field Orders:")
        # for node, orders in sorted(field_order.items()):
        #     print(f"Node {node}: Temporal Order {orders['temporal_order']}, Field Order {orders['field_order']}")
        return field_order, max_len

    #Adding fields to a node
    def update_kG(self,label, id, field, value, graph):
        namespace = self.__namespace
        node_uri = URIRef(namespace+id)
        graph.add((node_uri, URIRef(namespace+field), Literal(value)))

    #Adding coordinate fields to nodes
    def set_position(self,label, id, x, y, graph):
        namespace = self.__namespace
        node_uri = URIRef(namespace+id)
        graph.add((node_uri, URIRef(namespace+"x"), Literal(x)))
        graph.add((node_uri, URIRef(namespace+"y"), Literal(y)))
        # Add x and y coordinates to the display map
        self.__showG.nodes[id]['x'] = x
        self.__showG.nodes[id]['y'] = y

    # Fault time series master method
    def sort_knowledge_gragh(self,graph):

        undirected_G = self.__G.to_undirected()
        connected_components = list(nx.connected_components(undirected_G))

        # Give each subrelationship a unique group_id
        group_mapping = {}
        for group_id, component in enumerate(connected_components):
            for node in component:
                group_mapping[node] = group_id

        # Add the group_id attribute to each node
        for node in self.__G.nodes:
            self.__G.nodes[node]["group_id"] = group_mapping[node]
        x_append = 0
        for group_id, component in enumerate(connected_components):
            subgraph = self.__G.subgraph(component).copy()  # Get the subgraph corresponding to the subrelational network
            if nx.is_directed_acyclic_graph(subgraph):  # Check if it is a DAG
                if self.check_conflicts(subgraph):
                    self.__showG.add_nodes_from(subgraph.nodes())
                    self.__showG.add_edges_from(subgraph.edges())
                    temporal_order, x_max = self.sort_subgraph(subgraph)
                    for node, order in temporal_order.items():
                        self.update_kG("Fault", node, "temporal_order", order["temporal_order"], graph)
                        self.update_kG("Fault", node, "field_order", order["field_order"] + x_append, graph)
                        self.set_position("Fault", node, order["field_order"] + x_append, order["temporal_order"], graph)
                    x_append += x_max