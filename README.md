# 🚦 Real-Time Traffic Congestion Detection System

A complete IoT-based traffic monitoring system using Kafka, MongoDB, Flask, and Leaflet.js for real-time visualization.

## 📋 System Architecture

```
CSV Data → Kafka Producer → Kafka Topic → Kafka Consumer → MongoDB → Flask API → Leaflet.js Map
```

## 🛠️ Prerequisites

- Python 3.8+
- Apache Kafka 3.x
- MongoDB 6.x+
- Modern web browser

## 📦 Installation Steps

### 1. Install Apache Kafka

**Download & Extract:**

```bash
wget https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz
tar -xzf kafka_2.13-3.6.1.tgz
cd kafka_2.13-3.6.1
```

**Start Zookeeper:**

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

**Start Kafka Server (in new terminal):**

```bash
bin/kafka-server-start.sh config/server.properties
```

**Create Topic:**

```bash
bin/kafka-topics.sh --create --topic traffic-data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 2. Install MongoDB

**Ubuntu/Debian:**

```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

**macOS:**

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Verify MongoDB:**

```bash
mongosh
```

### 3. Setup Python Environment

```bash
# Clone or create project directory
mkdir traffic-congestion-project
cd traffic-congestion-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Download Dataset

1. Download from Kaggle: [IoT Traffic Flow Dataset](https://www.kaggle.com/datasets/programmer3/iot-based-traffic-flow-and-congestion-dataset)
2. Place CSV file in project root as `traffic_data.csv`

## 🚀 Running the System

### Terminal 1: Start Kafka Consumer

```bash
python kafka_consumer.py
```

### Terminal 2: Start Flask API

```bash
cd flask_app
python app.py
```

### Terminal 3: Start Kafka Producer

```bash
python kafka_producer.py
```

### Terminal 4: Open Web Browser

Navigate to: **http://localhost:5000**

## 📊 API Endpoints

| Endpoint       | Method | Description                |
| -------------- | ------ | -------------------------- |
| `/`            | GET    | Leaflet.js map interface   |
| `/get_traffic` | GET    | Latest traffic data (JSON) |
| `/stats`       | GET    | Traffic statistics         |

## 🗺️ Map Interface Features

- **Real-time updates** every 5 seconds
- **Color-coded markers:**
  - 🔴 Red = Congested (vehicles > 50 AND speed < 20 km/h)
  - 🟢 Green = Free Flow
- **Interactive popups** with detailed information
- **Live statistics** dashboard

## 🧪 Testing the System

**Check Kafka Topic:**

```bash
bin/kafka-console-consumer.sh --topic traffic-data --from-beginning --bootstrap-server localhost:9092
```

**Query MongoDB:**

```bash
mongosh
use TrafficDB
db.TrafficData.find().limit(5).pretty()
db.TrafficData.countDocuments({status: "Congested"})
```

**Test API:**

```bash
curl http://localhost:5000/get_traffic
curl http://localhost:5000/stats
```

## 🔧 Configuration

### Congestion Detection Rule

Edit in `kafka_consumer.py`:

```python
def detect_congestion(self, vehicle_count, avg_speed):
    if vehicle_count > 50 and avg_speed < 20:
        return "Congested"
    return "Free Flow"
```

### Update Intervals

- Producer delay: `kafka_producer.py` line 54
- Frontend refresh: `index.html` line 221 (5000ms = 5 seconds)

## 📁 Project Structure

```
traffic-congestion-project/
├── kafka_producer.py          # Streams CSV to Kafka
├── kafka_consumer.py          # Processes & stores in MongoDB
├── requirements.txt           # Python dependencies
├── traffic_data.csv           # Dataset (download separately)
├── flask_app/
│   ├── app.py                 # Flask REST API
│   └── templates/
│       └── index.html         # Leaflet.js map interface
└── README.md                  # This file
```

## 🐛 Troubleshooting

**Kafka Connection Error:**

- Ensure Kafka and Zookeeper are running
- Check port 9092 is not blocked

**MongoDB Connection Error:**

- Verify MongoDB is running: `sudo systemctl status mongodb`
- Check port 27017

**No Data on Map:**

- Confirm producer is sending data (check terminal logs)
- Verify consumer is processing messages
- Check browser console for API errors

## 📝 Sample Data Format

**Input CSV:**

```csv
Latitude,Longitude,Vehicle_Count,Average_Speed
28.7041,77.1025,65,15.5
19.0760,72.8777,30,45.2
```

**MongoDB Document:**

```json
{
  "lat": 28.7041,
  "lon": 77.1025,
  "vehicle_count": 65,
  "avg_speed": 15.5,
  "status": "Congested",
  "timestamp": "2025-10-04T10:30:00",
  "location": {
    "type": "Point",
    "coordinates": [77.1025, 28.7041]
  }
}
```

## 🎯 Next Steps

- Add authentication to Flask API
- Implement WebSocket for true real-time updates
- Add historical data analysis
- Deploy to cloud (AWS/GCP/Azure)
- Add alerting system for critical congestion

## 📄 License

MIT License - Feel free to use for educational/commercial purposes

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

**Built with ❤️ for Smart City IoT Solutions**
