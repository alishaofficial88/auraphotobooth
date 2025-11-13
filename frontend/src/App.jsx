import React, { useState } from "react";
import BoothControls from "./components/BoothControls";
import ResultDisplay from "./components/ResultDisplay";
import "./App.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [started, setStarted] = useState(false);

  if (!started) {
    return (
      <div className="app-wrap">
        <div className="card hero-card">
          <div className="hero-content">
            <div className="logo-container">
              <h1 className="logo">Aura Polaroid Booth</h1>
              <div className="sparkle">✨</div>
            </div>
            <p className="subtitle">Discover the colors of your soul</p>
            
            <div className="story-section">
              <div className="story-card">
                <h3>Your Magical Journey</h3>
                <div className="story-content">
                  <p>✨ <strong>Welcome to a world of energy and color!</strong> Just like the mystical aura booths of Thailand, we capture the beautiful energy that surrounds you.</p>
                  
                  <p>💫 <strong>How it works:</strong> Your photo reveals your current energy state. We analyze the colors around you and translate them into insights about your emotional and spiritual being.</p>
                  
                  <p>🌿 <strong>Your privacy matters:</strong> No login required. No data stored. Your magical moment stays with you forever.</p>
                  
                  <p>🌈 <strong>Ready to discover your aura?</strong> Each reading is unique, just like you!</p>
                </div>
              </div>
            </div>

            <button 
              className="start-btn magic-pulse" 
              onClick={() => setStarted(true)}
            >
              🌟 Begin Your Aura Reading
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-wrap">
      <div className="card main-card">
        <header className="app-header">
          <div className="header-content">
            <h1 className="logo-small">Aura Polaroid Booth</h1>
            <button 
              className="back-btn" 
              onClick={() => {
                setResult(null);
                setStarted(false);
              }}
            >
              ← New Reading
            </button>
          </div>
        </header>

        {!result ? (
          <BoothControls onResult={setResult} />
        ) : (
          <ResultDisplay result={result} />
        )}

        <footer className="app-footer">
          <p>Made with 💫 • Your energy never leaves your device</p>
        </footer>
      </div>
    </div>
  );
}