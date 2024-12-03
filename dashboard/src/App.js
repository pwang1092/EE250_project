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
        // Fetch both sensor and face detection data
        const response = await fetch('http://52.38.44.83/api/sensors');
        const facesResponse = await fetch('http://52.38.44.83/api/faces');
        
        if (!response.ok || !facesResponse.ok) {
          throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        const facesData = await facesResponse.json();
        
        // Get latest readings if there are any
        if (data) {
          setSensorData(data);
          
          // Check for intruder conditions
          const isIntruder = 
            data.ultrasonic_reading < ultrasonicThreshold || 
            data.light_level > lightThreshold;
            
          setIntruderDetected(isIntruder);
        }

        // Check if we have valid face data with high confidence
        const hasFaceWithHighConfidence = 
          facesData?.faces?.[0]?.confidence > 0.7;

        if (hasFaceWithHighConfidence) {
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

  // Helper function to check for valid face detection
  const hasFaceDetected = () => {
    return faceData?.faces?.[0]?.confidence > 0.7;
  };

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
          {hasFaceDetected() ? (
            <div className="camera-feed">
              <div className="image-container">
                {faceData?.image && (
                  <img 
                    src={`data:image/jpeg;base64,${faceData.image}`}
                    alt="Camera feed"
                  />
                )}
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
