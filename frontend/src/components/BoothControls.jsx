import React, { useState } from "react";
import CountdownCamera from "./CountdownCamera";
import UploadSection from "./UploadSection";

export default function BoothControls({ onResult }) {
  const [mode, setMode] = useState(null);
  const [filter, setFilter] = useState("none");
  const [caption, setCaption] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendToBackend = async (dataUrl) => {
    setIsLoading(true);
    try {
      const blob = await (await fetch(dataUrl)).blob();
      const form = new FormData();
      form.append("file", blob, "capture.jpg");
      form.append("filter_name", filter);
      form.append("caption", caption);
      
      const res = await fetch("http://127.0.0.1:8000/api/generate/", {
        method: "POST",
        body: form,
      });
      
      const json = await res.json();
      
      if (json.success) {
        const imageUrl = `http://127.0.0.1:8000${json.image}`;
        onResult({ 
          imageUrl, 
          analysis: json.analysis,
          message: json.message 
        });
      } else {
        throw new Error(json.error || "Magic failed!");
      }
    } catch (err) {
      alert("✨ Oops! The magic needs a moment. Please check if the backend is running.");
      console.error("Backend error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`controls fade-in ${isLoading ? 'loading' : ''}`}>
      <div className="mode-selection">
        <h3>Choose Your Magic</h3>
        <div className="modes">
          <button
            className={`mode-btn ${mode === "camera" ? "active" : ""}`}
            onClick={() => setMode("camera")}
            disabled={isLoading}
          >
            📷 Live Capture
          </button>
          <button
            className={`mode-btn ${mode === "upload" ? "active" : ""}`}
            onClick={() => setMode("upload")}
            disabled={isLoading}
          >
            📁 Upload Photo
          </button>
        </div>
      </div>

      <div className="options">
        <label>
          ✨ Aura Filter
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            disabled={isLoading}
          >
            <option value="none">Natural Aura</option>
            <option value="vintage">Vintage Charm</option>
            <option value="dreamy">Dreamy Glow</option>
            <option value="golden">Golden Hour</option>
          </select>
        </label>
        <label>
          💫 Caption
          <input
            placeholder="e.g., 'My magical aura!'"
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            disabled={isLoading}
            maxLength={50}
          />
        </label>
      </div>

      {mode === "camera" && (
        <CountdownCamera 
          onCapture={sendToBackend} 
          disabled={isLoading}
        />
      )}
      
      {mode === "upload" && (
        <UploadSection 
          onSend={sendToBackend} 
          disabled={isLoading}
        />
      )}
      
      {!mode && (
        <div className="blank-tip">
          ✨ Choose how you'd like to capture your energy
        </div>
      )}

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Reading your energy... ✨</p>
        </div>
      )}
    </div>
  );
}