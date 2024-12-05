import React, { useState } from "react";
import axios from "axios";

function App() {
  const [result, setResult] = useState("");

  const handleUpload = async () => {
    try {
      const response = await axios.post("http://localhost:5000/detect", {
        src_ip: "192.168.1.1",
        dst_ip: "192.168.1.2",
        protocol: 6,
        packet_size: 500,
        flow_duration: 10,
      });
      setResult(response.data.ddos ? "DDoS Detected!" : "Traffic is Normal");
    } catch (err) {
      console.error("Error:", err);
    }
  };

  return (
    <div className="App">
      <h1>DDoS Detection in 5G</h1>
      <button onClick={handleUpload}>Simulate Traffic</button>
      <p>{result}</p>
    </div>
  );
}

export default App;
