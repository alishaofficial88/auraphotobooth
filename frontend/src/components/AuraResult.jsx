import React from "react";

export default function AuraResult({ url, onSave }) {
  return (
    <div className="result-wrap">
      <h3>Your Aura Polaroid</h3>
      <div className="final">
        <img src={url} alt="aura final" className="final-img" />
      </div>
      <div className="result-actions">
        <a className="btn primary" href={url} download="aura-polaroid.jpg">Download</a>
        <button className="btn ghost" onClick={() => { navigator.clipboard.writeText(url); alert("Image link copied!"); }}>Copy Link</button>
      </div>
    </div>
  );
}