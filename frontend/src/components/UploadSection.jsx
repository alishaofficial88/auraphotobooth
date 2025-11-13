import React, { useState } from "react";

export default function UploadSection({ onSend, disabled }) {
  const [preview, setPreview] = useState(null);
  const [isReady, setIsReady] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file type
    if (!file.type.startsWith('image/')) {
      alert('✨ Please select an image file (JPEG, PNG, etc.)');
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('✨ Please select an image smaller than 10MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
      setIsReady(true);
    };
    reader.onerror = () => {
      alert('✨ Error reading file. Please try another image.');
    };
    reader.readAsDataURL(file);
  };

  const handleSend = () => {
    if (!preview || disabled) return;
    onSend(preview);
  };

  const clearSelection = () => {
    setPreview(null);
    setIsReady(false);
    // Reset file input
    const fileInput = document.getElementById('uploader');
    if (fileInput) fileInput.value = '';
  };

  return (
    <div className="upload-block">
      <div className="upload-header">
        <h3>📁 Upload Your Photo</h3>
        <p>Choose a clear photo for the best aura reading</p>
      </div>

      <input 
        id="uploader" 
        type="file" 
        accept="image/*" 
        onChange={handleFileSelect}
        style={{ display: "none" }}
        disabled={disabled}
      />
      
      <label 
        className="upload-btn" 
        htmlFor="uploader"
        style={{ opacity: disabled ? 0.6 : 1 }}
      >
        📸 Choose Photo
      </label>

      <div className="status">
        {isReady ? (
          <span className="green">✅ Ready for magic!</span>
        ) : (
          <span className="muted">No photo selected</span>
        )}
        
        <button 
          className="btn primary" 
          disabled={!isReady || disabled}
          onClick={handleSend}
        >
          {disabled ? "Working Magic..." : "✨ Reveal My Aura"}
        </button>
        
        {isReady && (
          <button 
            className="btn secondary" 
            onClick={clearSelection}
            disabled={disabled}
          >
            Clear
          </button>
        )}
      </div>

      {preview && (
        <div className="preview-section">
          <div className="preview-small">
            <img src={preview} alt="Upload preview" />
          </div>
          <div className="preview-tips">
            <p>💫 <strong>Great choice!</strong> Your aura reading will be ready in moments.</p>
          </div>
        </div>
      )}

      <div className="upload-tips">
        <h4>📝 Tips for best results:</h4>
        <ul>
          <li>Use clear, well-lit photos</li>
          <li>Portrait orientation works best</li>
          <li>Ensure your face is visible</li>
          <li>File types: JPEG, PNG, WebP</li>
          <li>Max file size: 10MB</li>
        </ul>
      </div>
    </div>
  );
}