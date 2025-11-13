import React from "react";
import { QRCodeSVG } from "qrcode.react";

export default function ResultDisplay({ result }) {
  const { imageUrl, analysis, message } = result;

  const downloadImage = async () => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'my-aura-polaroid.jpg';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
      alert('✨ Download failed. Please try again!');
    }
  };

  const shareImage = async () => {
    if (navigator.share) {
      try {
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const file = new File([blob], 'my-aura.jpg', { type: 'image/jpeg' });
        
        await navigator.share({
          title: 'My Aura Reading',
          text: 'Check out my magical aura reading! ✨',
          files: [file]
        });
      } catch (error) {
        console.log('Sharing failed or was cancelled');
      }
    } else {
      // Fallback: copy link to clipboard
      try {
        await navigator.clipboard.writeText(window.location.href);
        alert('✨ Link copied! Share your magic with friends.');
      } catch (err) {
        alert('✨ Share this URL: ' + window.location.href);
      }
    }
  };

  return (
    <div className="result-card">
      <div className="result-header">
        <h2>✨ Your Aura Revealed ✨</h2>
        {message && <p className="result-message">{message}</p>}
      </div>

      <div className="final-wrap">
        <div className="polaroid-container">
          <img 
            src={imageUrl} 
            alt="Your magical aura polaroid" 
            className="final-img"
            onLoad={() => console.log('Image loaded successfully')}
            onError={(e) => {
              console.error('Image failed to load');
              e.target.style.display = 'none';
            }}
          />
        </div>
        
        <div className="analysis">
          <h3>🌈 Your Energy Reading</h3>
          <div className="colors">
            {analysis.map((color, index) => (
              <div key={index} className="color-chip">
                <div 
                  className="swatch"
                  style={{ 
                    background: `linear-gradient(135deg, var(--${color.aura}-light, var(--${color.aura}-dark))`,
                    boxShadow: `0 4px 15px var(--${color.aura}-shadow)`
                  }}
                />
                <div className="color-info">
                  <div className="aura-name">{color.aura}</div>
                  <div className="aura-meaning">{color.meaning}</div>
                  {index === 0 && (
                    <div className="primary-badge">Primary Energy</div>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          <div className="interpretation-tip">
            <p>💡 <strong>Tip:</strong> Your primary color represents your dominant energy, while secondary colors show supporting energies.</p>
          </div>
        </div>
      </div>

      <div className="result-actions">
        <div className="action-buttons">
          <button className="btn primary" onClick={downloadImage}>
            📥 Download Polaroid
          </button>
          <button className="btn secondary" onClick={shareImage}>
            🌟 Share Magic
          </button>
        </div>
        
        <div className="qr-container">
          <QRCodeSVG 
            value={imageUrl} 
            size={80}
            level="M"
            includeMargin
          />
          <span>Scan to save</span>
        </div>
      </div>

      <div className="energy-tips">
        <h4>🌿 Energy Tips</h4>
        <div className="tips-grid">
          <div className="tip-card">
            <strong>Meditate</strong>
            <p>Spend 5 minutes daily to balance your energy</p>
          </div>
          <div className="tip-card">
            <strong>Hydrate</strong>
            <p>Water helps maintain clear energy flow</p>
          </div>
          <div className="tip-card">
            <strong>Nature</strong>
            <p>Connect with nature to recharge your aura</p>
          </div>
        </div>
      </div>
    </div>
  );
}