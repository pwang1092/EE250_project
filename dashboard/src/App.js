import { useState, useEffect } from 'react';
import './App.css';

function App({ 
  ultrasonicThreshold = 50,
  lightThreshold = 700,    
  pollInterval = 1000
}) {
  const [sensorData, setSensorData] = useState(null);
  const [faceData, setFaceData] = useState(null);
  const [intruderDetected, setIntruderDetected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://52.38.44.83/api/sensors');
        const facesResponse = await fetch('http://52.38.44.83/api/faces');
        
        if (!response.ok || !facesResponse.ok) {
          throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        const facesData = await facesResponse.json();
        
        // Update sensor data if available
        if (data) {
          setSensorData(data);
          
          // Check for intruder conditions
          const isIntruder = 
            data.ultrasonic_reading < ultrasonicThreshold || 
            data.light_level > lightThreshold;
            
          setIntruderDetected(isIntruder);
        }

        // Update face data if faces are detected
        if (facesData && facesData.faces && facesData.faces.length > 0) {
          setFaceData(facesData);
        } else {
          setFaceData(null);
        }

      } catch (err) {
        setError(err.message);
      }
    };

    const interval = setInterval(fetchData, pollInterval);
    return () => clearInterval(interval);
  }, [ultrasonicThreshold, lightThreshold, pollInterval]);

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Security Dashboard</h1>
        
        {intruderDetected && (
          <div className="alert">
            ⚠️ INTRUDER DETECTED ⚠️
          </div>
        )}

        <div className="dashboard-content">
          {faceData && faceData.faces && faceData.faces.length > 0 ? (
            <div className="camera-feed">
              <h2>Camera Feed</h2>
              <div className="image-container">
                <img 
                  src={`data:image/jpeg;base64,${faceData.image}`}
                  alt="Camera feed"
                />
                <div className="face-detected">Face Detected!</div>
              </div>
              <div className="timestamp">
                {new Date(faceData.timestamp).toLocaleString()}
              </div>
            </div>
          ) : (
            <div className="camera-feed">
              <h2>Camera Feed</h2>
              <div>No faces detected</div>
            </div>
          )}


          {sensorData && (
            <div className="sensor-data">
              <h2>Sensor Readings</h2>
              <div className="reading">
                <label>Distance:</label>
                <span>{sensorData.ultrasonic_reading} cm</span>
              </div>
              <div className="reading">
                <label>Light Level:</label>
                <span>{sensorData.light_level}</span>
              </div>
              <div className="reading">
                <label>Timestamp:</label>
                <span>{new Date(sensorData.timestamp).toLocaleString()}</span>
              </div>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
