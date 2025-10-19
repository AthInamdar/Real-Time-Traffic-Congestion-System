# 🎬 Running the Row-by-Row Traffic Simulation

## ✅ What's Been Fixed

1. **Congestion Detection**: Now uses the actual `Congestion_Level` column from your dataset (1 = Congested, 0 = Free Flow)
2. **True Real-Time Streaming**: Uses Server-Sent Events (SSE) for instant live updates
3. **Row-by-Row Visualization**: Data appears one row at a time as it's produced
4. **Real-time Progress**: Shows current row number and progress bar
5. **Correct Data Mapping**: All CSV columns properly mapped (Traffic_Speed_kmph, Traffic_Density_vpkm, Vehicle_Count, etc.)

## 🚀 How to Run the Simulation

### Step 1: Clear Previous Data (REQUIRED for Live Simulation)
**IMPORTANT**: You MUST clear old data to see the live row-by-row simulation!

Open MongoDB shell and clear old data:
```bash
mongosh
use TrafficDB
db.TrafficData.deleteMany({})
exit
```

Or using PowerShell one-liner:
```powershell
mongosh --eval "use TrafficDB; db.TrafficData.deleteMany({})"
```

### Step 2: Start Services in Order

**Terminal 1 - Start Kafka Consumer:**
```bash
cd i:\BDA\traffic-congestion-project
.\venv\Scripts\activate
python kafka_consumer.py
```
You should see: ✓ Kafka Consumer initialized

**Terminal 2 - Start Flask Web Server:**
```bash
cd i:\BDA\traffic-congestion-project\flask_app
..\venv\Scripts\activate
python app.py
```
You should see: 🚀 Flask API server starting...

**Terminal 3 - Start Kafka Producer (This starts the simulation):**
```bash
cd i:\BDA\traffic-congestion-project
.\venv\Scripts\activate
python kafka_producer.py
```
You'll see: [Row 1] 🔴 CONGESTED or 🟢 FREE FLOW for each row

**Terminal 4 - Open Web Browser:**
Navigate to: **http://localhost:5000**

## 📊 What You'll See

### In the Web Interface:
- **"Stream connected! Waiting for data..."** message in browser console (F12)
- **Simulation Progress**: Shows "Row X / Total" with a progress bar
- **Markers appear INSTANTLY** as producer sends each row (true real-time!)
- **Red markers** = Congested (Congestion_Level = 1)
- **Green markers** = Free Flow (Congestion_Level = 0)
- **Auto-popup** shows details for each new marker
- **Map pans** to follow the latest data point
- **Console logs** show each row as it arrives: "✅ Row X - Status"

### In Terminal 1 (Consumer):
```
🔴 [Row 4] Congested | Lat: 13.0661, Lon: 77.6609 | Speed: 37.6 km/h | Vehicles: 16 | Density: 30.7
🔴 [Row 5] Congested | Lat: 13.0361, Lon: 77.6180 | Speed: 28.2 km/h | Vehicles: 16 | Density: 29.6
```

### In Terminal 3 (Producer):
```
[Row 1] 🟢 FREE FLOW | Lat: 12.9180, Lon: 77.6233 | Speed: 55.2 km/h | Vehicles: 17
[Row 2] 🟢 FREE FLOW | Lat: 13.0887, Lon: 77.5680 | Speed: 52.1 km/h | Vehicles: 20
[Row 3] 🔴 CONGESTED | Lat: 13.0667, Lon: 77.6609 | Speed: 37.6 km/h | Vehicles: 16
```

## ⚙️ Customization

### Change Simulation Speed
Edit `kafka_producer.py` line 70:
```python
producer.stream_csv_data(csv_path, delay=1)  # Change delay value (seconds)
```
- `delay=0.5` = 2 rows per second (faster)
- `delay=1` = 1 row per second (default)
- `delay=2` = 1 row every 2 seconds (slower)

### Change Frontend Update Speed
Edit `flask_app/templates/index.html` line 332:
```javascript
}, 1000); // Change to match producer delay (in milliseconds)
```

## 🎯 Expected Behavior

1. **Open browser first** → See "Stream connected! Waiting for data..." in console
2. **Producer sends** data row by row with 1-second delay
3. **Consumer receives** and stores in MongoDB immediately
4. **Flask SSE streams** new data to browser INSTANTLY (no polling!)
5. **Markers appear** one by one on the map in real-time
6. **Statistics update** automatically with each new row
7. **Progress bar fills** as simulation continues

## 🔥 Key Difference: Server-Sent Events (SSE)

This implementation uses **SSE** instead of polling:
- ✅ **Instant updates** - No delay waiting for next poll
- ✅ **Efficient** - Server pushes data only when available
- ✅ **True real-time** - Browser receives data as soon as it's in MongoDB
- ✅ **Automatic reconnection** - If connection drops, it reconnects automatically

## 🐛 Troubleshooting

**No markers appearing:**
- Check that Kafka and MongoDB are running
- Verify producer is sending data (check Terminal 3)
- Check browser console for errors (F12)

**Markers appear all at once:**
- Clear MongoDB data and restart
- Make sure you start Consumer BEFORE Producer

**"Stream connection error" in console:**
- Make sure Flask app is running (Terminal 2)
- Refresh the browser page
- Check Flask terminal for errors

**Wrong congestion detection:**
- This is now fixed! Uses actual Congestion_Level column
- Verify in Terminal 1 that you see both 🔴 and 🟢 emojis

**Browser console shows "Stream connected" but no markers:**
- Start the producer (Terminal 3) to begin sending data
- Make sure MongoDB is running and accessible

## 📈 Dataset Info

Your dataset has **3,877 rows** with:
- **Congestion_Level = 1**: Congested areas
- **Congestion_Level = 0**: Free flow areas

The simulation will process all rows sequentially, showing real-time traffic conditions across Bangalore.

---

**Enjoy your real-time traffic simulation! 🚦**
