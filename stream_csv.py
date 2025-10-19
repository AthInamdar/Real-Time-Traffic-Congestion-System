"""
Helper script to stream a CSV to Kafka row-by-row.
Usage (Windows PowerShell):
  python stream_csv.py --csv traffic_data.csv --delay 1 --bootstrap localhost:9092 --topic traffic-data
"""
import argparse
from kafka_producer import TrafficDataProducer


def main():
    parser = argparse.ArgumentParser(description="Stream a CSV to Kafka row-by-row")
    parser.add_argument("--csv", dest="csv_path", default="traffic_data.csv", help="Path to CSV file")
    parser.add_argument("--delay", dest="delay", type=float, default=1.0, help="Delay between rows in seconds")
    parser.add_argument("--bootstrap", dest="bootstrap", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", dest="topic", default="traffic-data", help="Kafka topic name")

    args = parser.parse_args()

    producer = TrafficDataProducer(bootstrap_servers=args.bootstrap, topic=args.topic)
    producer.stream_csv_data(args.csv_path, delay=args.delay)


if __name__ == "__main__":
    main()
