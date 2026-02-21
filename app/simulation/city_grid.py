import networkx as nx
import random
import math

class CityConnectGrid:
    def __init__(self, num_nodes: int = 5):
        self.num_nodes = num_nodes
        self.graph = nx.complete_graph(num_nodes)
        self.grid_size = 1000.0 # 1000x1000 meter grid
        self._initialize_iot_sensors()

    def _initialize_iot_sensors(self):
        """Initializes nodes with dynamic physical coordinates and velocity."""
        for node in self.graph.nodes:
            self.graph.nodes[node]['telemetry'] = {
                'status': 'OPERATIONAL',
                'network_latency_ms': random.uniform(10.0, 50.0),
                'resource_capacity_pct': random.uniform(80.0, 100.0),
                'threat_level': 0.0,
                'x': random.uniform(0, self.grid_size),
                'y': random.uniform(0, self.grid_size),
                'velocity_x': random.uniform(-5.0, 5.0), # Moving up to 5 m/s
                'velocity_y': random.uniform(-5.0, 5.0)
            }
        self._update_edge_distances()

    def _update_edge_distances(self):
        """Calculates exact Euclidean distance between moving nodes."""
        for u, v in self.graph.edges:
            x1, y1 = self.graph.nodes[u]['telemetry']['x'], self.graph.nodes[u]['telemetry']['y']
            x2, y2 = self.graph.nodes[v]['telemetry']['x'], self.graph.nodes[v]['telemetry']['y']
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.graph.edges[u, v]['distance'] = max(1.0, distance)
            self.graph.edges[u, v].setdefault('pheromone_level', 1.0)

    def tick_physics_engine(self):
        """Moves all nodes by their velocity vector for one second of time."""
        for node in self.graph.nodes:
            t = self.graph.nodes[node]['telemetry']
            # Update position, bounce off grid walls
            t['x'] += t['velocity_x']
            t['y'] += t['velocity_y']
            if t['x'] <= 0 or t['x'] >= self.grid_size: t['velocity_x'] *= -1
            if t['y'] <= 0 or t['y'] >= self.grid_size: t['velocity_y'] *= -1
        
        self._update_edge_distances()

    def inject_anomaly(self, target_node: int, anomaly_type: str):
        t = self.graph.nodes[target_node]['telemetry']
        if anomaly_type == "DDoS_ATTACK":
            t['network_latency_ms'] = 999.9
            t['threat_level'] = 0.95
            t['status'] = 'COMPROMISED'
            t['velocity_x'] = 0.0 # Disabled node stops moving
            t['velocity_y'] = 0.0

    def fetch_live_telemetry(self) -> dict:
        return dict(self.graph.nodes(data=True))