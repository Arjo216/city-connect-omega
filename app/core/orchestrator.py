from app.simulation.city_grid import CityConnectGrid
from app.ml.predictive_cortex import PredictiveCortex
from app.core.veto_protocol import VetoProtocol

class OmegaOrchestrator:
    def __init__(self):
        self.grid = CityConnectGrid(num_nodes=5)
        self.ml_cortex = PredictiveCortex()
        self.governance = VetoProtocol()
        
        # Pre-train the ML model on boot
        self.ml_cortex.train_baseline()

    def run_cycle(self):
        """A single operational second in the city grid."""
        # 1. Update Physics
        self.grid.tick_physics_engine()
        
        # 2. Ingest Telemetry
        telemetry = self.grid.fetch_live_telemetry()
        
        # 3. ML Anomaly Detection Loop
        alerts = []
        for node_id, data in telemetry.items():
            analysis = self.ml_cortex.analyze_live_telemetry(node_id, data['telemetry'])
            if analysis['is_anomaly']:
                alerts.append(analysis)
        
        return telemetry, alerts