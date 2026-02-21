import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import random

class PredictiveCortex:
    def __init__(self):
        """
        Initializes the unsupervised ML engine.
        contamination=0.05 tells the model to expect about 5% of edge-case noise in normal data.
        """
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.is_trained = False
        self.feature_names = ['network_latency_ms', 'resource_capacity_pct', 'threat_level']

    def train_baseline(self):
        """Synthesizes historical baseline telemetry and trains the model."""
        print("\n[ML CORTEX] Generating historical baseline telemetry (1,000 epochs)...")
        data = []
        for _ in range(1000):
            # Normal operating parameters for the grid
            latency = random.uniform(10.0, 50.0)
            capacity = random.uniform(80.0, 100.0)
            threat = random.uniform(0.0, 0.1)
            data.append([latency, capacity, threat])
        
        df = pd.DataFrame(data, columns=self.feature_names)
        
        print("[ML CORTEX] Training Isolation Forest algorithm...")
        self.model.fit(df)
        self.is_trained = True
        print("[ML CORTEX] Model weights locked. Ready for sub-millisecond inference.")

    def analyze_live_telemetry(self, node_id: int, telemetry: dict) -> dict:
        """
        Ingests live telemetry from a single node and predicts if it is experiencing a zero-day anomaly.
        """
        if not self.is_trained:
            raise Exception("Critical Error: ML Cortex must be trained before inference.")
        
        # Format the live data into a DataFrame for the model
        live_data = pd.DataFrame([[
            telemetry['network_latency_ms'], 
            telemetry['resource_capacity_pct'], 
            telemetry['threat_level']
        ]], columns=self.feature_names)
        
        # Predict: 1 for normal, -1 for anomaly
        prediction = self.model.predict(live_data)[0]
        
        # Decision function: lower/negative score = highly anomalous
        score = self.model.decision_function(live_data)[0]
        
        is_anomaly = True if prediction == -1 else False
        
        return {
            "node_id": node_id,
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(score), 4)
        }

# --- Quick Lab Test ---
if __name__ == "__main__":
    # 1. Boot and train the model
    cortex = PredictiveCortex()
    cortex.train_baseline()
    
    # 2. Test 1: Normal Telemetry (Should pass)
    normal_data = {
        'status': 'OPERATIONAL', 
        'network_latency_ms': 35.5, 
        'resource_capacity_pct': 92.0, 
        'threat_level': 0.05
    }
    print("\n--- Testing Normal Node Behavior ---")
    print(cortex.analyze_live_telemetry(node_id=0, telemetry=normal_data))
    
    # 3. Test 2: Subtle Zero-Day Threat (Should be flagged BEFORE it hits 999.9ms)
    # Notice the latency is only 140ms and the threat level hasn't spiked yet. 
    # A human rule wouldn't catch this, but the ML will.
    stealth_attack_data = {
        'status': 'OPERATIONAL', 
        'network_latency_ms': 140.0, 
        'resource_capacity_pct': 75.0, 
        'threat_level': 0.15
    }
    print("\n--- Testing Stealth/Zero-Day Threat ---")
    print(cortex.analyze_live_telemetry(node_id=1, telemetry=stealth_attack_data))