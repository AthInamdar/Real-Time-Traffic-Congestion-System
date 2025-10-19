"""
Kafka Consumer - Processes traffic data and stores in MongoDB
"""
import json
from kafka import KafkaConsumer
from pymongo import MongoClient, GEOSPHERE
from datetime import datetime

class TrafficDataConsumer:
    def __init__(self, 
                 bootstrap_servers='localhost:9092',
                 topic='traffic-data',
                 mongo_uri='mongodb://localhost:27017/'):
        
        # Kafka Consumer
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='traffic-consumer-group'
        )
        # MongoDB Connection
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client['TrafficDB']
        self.collection = self.db['TrafficData']
        
        # Create geospatial index
        self.collection.create_index([("location", GEOSPHERE)])
        print("✓ Kafka Consumer initialized")
        print("✓ MongoDB connected: TrafficDB.TrafficData")
        
        # Clear previous data for a fresh run (keeps indexes)
        deleted = self.collection.delete_many({}).deleted_count
        print(f"✓ Cleared previous records: {deleted}")
    
    def detect_congestion(self, vehicle_count: int, speed_kmph: float, density_vpkm: float):
        """
        Decide congestion based on traffic metrics (no dataset label).
        Rule (tunable):
          - Congested if any of:
              • vehicle_count >= 25 AND speed_kmph <= 30
              • density_vpkm >= 35 AND speed_kmph <= 40
        Returns: (numeric_level: 1|0, status: 'Congested'|'Free Flow')
        """
        is_congested = (
            (vehicle_count >= 25 and speed_kmph <= 30) or
            (density_vpkm >= 35 and speed_kmph <= 40)
        )
        return (1, "Congested") if is_congested else (0, "Free Flow")
    
    def process_messages(self):
        """
        Consume messages from Kafka and store in MongoDB
        """
        print("\n🔄 Listening for traffic data...\n")
        try:
            for message in self.consumer:
                try:
                    data = message.value

                    # Compute congestion based on incoming metrics
                    numeric_level, status = self.detect_congestion(
                        int(data.get('vehicle_count', 0)),
                        float(data.get('traffic_speed', 0.0)),
                        float(data.get('traffic_density', 0.0))
                    )

                    # Prepare MongoDB document
                    traffic_record = {
                        'row_number': data.get('row_number', 0),
                        'lat': data.get('lat'),
                        'lon': data.get('lon'),
                        'location': {
                            'type': 'Point',
                            'coordinates': [data.get('lon'), data.get('lat')]  # GeoJSON: [lng, lat]
                        },
                        'traffic_speed': data.get('traffic_speed', 0.0),
                        'traffic_density': data.get('traffic_density', 0.0),
                        'vehicle_count': data.get('vehicle_count', 0),
                        'time_of_day': data.get('time_of_day', 0),
                        'congestion_level': numeric_level,
                        'status': status,
                        'timestamp': datetime.fromisoformat(data['timestamp']) if isinstance(data.get('timestamp'), str) else datetime.utcnow()
                    }

                    # Insert into MongoDB
                    self.collection.insert_one(traffic_record)

                    status_emoji = "🔴" if status == "Congested" else "🟢"
                    print(
                        f"{status_emoji} [Row {traffic_record['row_number']}] {status} | Lat: {traffic_record['lat']:.4f}, Lon: {traffic_record['lon']:.4f} | "
                        f"Speed: {traffic_record['traffic_speed']:.1f} km/h | Vehicles: {traffic_record['vehicle_count']} | Density: {traffic_record['traffic_density']:.1f}"
                    )
                except Exception as msg_err:
                    # Log error and continue with next message
                    print(f"⚠️ Skipping bad message: {msg_err}")
                
        except KeyboardInterrupt:
            print("\n⏹ Consumer stopped by user")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            self.consumer.close()
            self.mongo_client.close()

if __name__ == "__main__":
    consumer = TrafficDataConsumer()
    consumer.process_messages()