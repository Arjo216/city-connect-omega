import random
import networkx as nx
from typing import List

class SwarmRouter:
    def __init__(self, graph: nx.Graph, num_ants: int = 20, decay_rate: float = 0.1, alpha: float = 1.0, beta: float = 2.0):
        """
        Ant Colony Optimization (ACO) engine for routing physical assets through the IoT grid.
        - alpha: Importance of the pheromone trail.
        - beta: Importance of the heuristic (visibility/distance).
        - decay_rate: How fast pheromones evaporate over time.
        """
        self.graph = graph
        self.num_ants = num_ants
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.beta = beta

    def _calculate_transition_probability(self, current_node: int, available_neighbors: List[int]) -> int:
        """The core Swarm math: Decides which node an asset should move to next."""
        probabilities = []
        denominator = 0.0

        for neighbor in available_neighbors:
            # Get edge data
            edge_data = self.graph.get_edge_data(current_node, neighbor)
            pheromone = edge_data.get('pheromone_level', 1.0)
            distance = edge_data.get('distance', 10.0)
            
            # Heuristic: Shorter distance is better (1/distance)
            eta = 1.0 / distance 
            
            # Calculate numerator: (tau^alpha) * (eta^beta)
            numerator = (pheromone ** self.alpha) * (eta ** self.beta)
            probabilities.append((neighbor, numerator))
            denominator += numerator

        if denominator == 0:
            return random.choice(available_neighbors)

        # Roulette wheel selection based on calculated probabilities
        rand_val = random.uniform(0, denominator)
        cumulative = 0.0
        for neighbor, prob in probabilities:
            cumulative += prob
            if rand_val <= cumulative:
                return neighbor
                
        return available_neighbors[-1]

    def optimize_route(self, start_node: int, target_node: int, iterations: int = 50) -> List[int]:
        """Runs the Swarm simulation to find the absolute best route bypassing compromised nodes."""
        best_route = []
        best_distance = float('inf')

        print(f"\n[SWARM] Deploying {self.num_ants} micro-agents to find optimal route from Node {start_node} to Node {target_node}...")

        for _ in range(iterations):
            for ant in range(self.num_ants):
                current_node = start_node
                route = [current_node]
                route_distance = 0.0

                # Ant explores until it hits the target or gets stuck
                while current_node != target_node:
                    neighbors = list(self.graph.neighbors(current_node))
                    
                    # Filter out nodes that the AI detected as compromised (Threat Level > 0.8)
                    safe_neighbors = [
                        n for n in neighbors 
                        if n not in route and self.graph.nodes[n]['telemetry']['threat_level'] < 0.8
                    ]

                    if not safe_neighbors:
                        break # Dead end, drop this route

                    next_node = self._calculate_transition_probability(current_node, safe_neighbors)
                    route_distance += self.graph.get_edge_data(current_node, next_node)['distance']
                    current_node = next_node
                    route.append(current_node)

                # If the ant reached the target, evaluate its success
                if current_node == target_node:
                    if route_distance < best_distance:
                        best_distance = route_distance
                        best_route = route
                    
                    # Deposit pheromones on this successful route (shorter route = more pheromone)
                    pheromone_deposit = 100.0 / route_distance
                    for i in range(len(route) - 1):
                        u, v = route[i], route[i+1]
                        current_pheromone = self.graph[u][v].get('pheromone_level', 1.0)
                        self.graph[u][v]['pheromone_level'] = current_pheromone + pheromone_deposit

            # Apply pheromone decay (evaporation) across the entire grid after each iteration
            for u, v in self.graph.edges:
                current_pheromone = self.graph[u][v].get('pheromone_level', 1.0)
                self.graph[u][v]['pheromone_level'] = max(0.1, current_pheromone * (1.0 - self.decay_rate))

        return best_route

# --- Quick Lab Test ---
if __name__ == "__main__":
    from app.simulation.city_grid import CityConnectGrid
    
    # Initialize the grid and inject the DDoS attack on Node 2
    grid_env = CityConnectGrid(num_nodes=5)
    grid_env.inject_anomaly(target_node=2, anomaly_type="DDoS_ATTACK")
    
    # Initialize the Swarm Router
    router = SwarmRouter(graph=grid_env.graph)
    
    # Try to route a supply convoy from Node 0 to Node 4
    optimal_path = router.optimize_route(start_node=0, target_node=4)
    
    print("\n==============================================")
    print("FINAL SWARM ROUTING SOLUTION")
    print("==============================================")
    print(f"Optimal Path Discovered: {optimal_path}")
    print(f"Notice how the Swarm automatically avoids Node 2!")