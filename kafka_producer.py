"""
Kafka Producer - Streams CSV data row by row to Kafka topic
"""
import csv
import json
import time
from kafka import KafkaProducer
from datetime import datetime

class TrafficDataProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='traffic-data'):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"✓ Kafka Producer initialized for topic: {self.topic}")
    
    def stream_csv_data(self, csv_file_path, delay=1):
        """
        Read CSV file and stream each row to Kafka
        Args:
            csv_file_path: Path to the traffic CSV file
            delay: Delay between messages in seconds (simulates real-time)
        """
        try:
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                row_count = 0
                
                for row in csv_reader:
                    try:
                        # Safe parsing helpers
                        def to_float(v, default=0.0):
                            try:
                                return float(v)
                            except (TypeError, ValueError):
                                return default

                        def to_int(v, default=0):
                            try:
                                # Handle floats stored as strings for integer fields
                                return int(float(v))
                            except (TypeError, ValueError):
                                return default

                        # Prepare message payload with correct column names (no dataset Congestion_Level)
                        message = {
                            'row_number': row_count + 1,
                            'lat': to_float(row.get('Latitude', 0)),
                            'lon': to_float(row.get('Longitude', 0)),
                            'traffic_speed': to_float(row.get('Traffic_Speed_kmph', 0)),
                            'traffic_density': to_float(row.get('Traffic_Density_vpkm', 0)),
                            'vehicle_count': to_int(row.get('Vehicle_Count', 0)),
                            'time_of_day': to_int(row.get('Time_of_Day_min', 0)),
                            'timestamp': datetime.utcnow().isoformat()
                        }

                        # Send to Kafka
                        self.producer.send(self.topic, value=message)
                        row_count += 1

                        print(
                            f"[Row {row_count}] Sent | Lat: {message['lat']:.4f}, Lon: {message['lon']:.4f} | "
                            f"Speed: {message['traffic_speed']:.1f} km/h | Vehicles: {message['vehicle_count']} | "
                            f"Density: {message['traffic_density']:.1f} vpkm"
                        )

                        time.sleep(delay)
                    except Exception as row_err:
                        # Log and continue with next row
                        print(f"⚠️ Skipping bad row {row_count + 1}: {row_err}")
                
                self.producer.flush()
                print(f"\n✓ Streaming complete! Total records sent: {row_count}")
                
        except FileNotFoundError:
            print(f"❌ Error: CSV file not found at {csv_file_path}")
        except Exception as e:
            print(f"❌ Error streaming data: {str(e)}")
        finally:
            self.producer.close()

if __name__ == "__main__":
    # Initialize producer
    producer = TrafficDataProducer()
    
    # Start streaming (adjust path to your CSV file)
    csv_path = "traffic_data.csv"  # Update with your CSV path
    producer.stream_csv_data(csv_path, delay=1)  # 1 second delay for row-by-row simulation