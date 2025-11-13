import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";

const videoConstraints = { 
  width: 720, 
  height: 540, 
  facingMode: "user",
  aspectRatio: 1.777
};

export default function CountdownCamera({ onCapture, disabled }) {
  const webcamRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);

  useEffect(() => {
    setIsCameraActive(true);
    return () => setIsCameraActive(false);
  }, []);

  const takePhoto = () => {
    if (!webcamRef.current) return;
    
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      setPreview(imageSrc);
    } catch (error) {
      console.error('Error capturing photo:', error);
      alert('✨ Unable to capture photo. Please check camera permissions.');
    }
  };

  const startCountdown = () => {
    if (disabled) return;
    
    let count = 3;
    setCountdown(count);
    
    const timer = setInterval(() => {
      count -= 1;
      if (count < 0) {
        clearInterval(timer);
        takePhoto();
        setCountdown(null);
      } else {
        setCountdown(count);
      }
    }, 1000);
  };

  const retake = () => {
    setPreview(null);
    setCountdown(null);
  };

  const usePhoto = () => {
    if (preview && !disabled) {
      onCapture(preview);
    }
  };

  return (
    <div className="camera-block">
      {!preview && (
        <>
          <div className="relative">
            {isCameraActive && (
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                videoConstraints={videoConstraints}
                className="webcam-mini"
                screenshotQuality={0.9}
                onUserMedia={() => console.log('Camera active')}
                onUserMediaError={() => {
                  console.error('Camera error');
                  alert('✨ Camera access required for live capture.');
                }}
              />
            )}
            
            {countdown !== null && (
              <div className="overlay-countdown">
                {countdown > 0 ? countdown : "😊"}
              </div>
            )}
          </div>
          
          <div className="camera-actions">
            <button 
              className="btn primary" 
              onClick={startCountdown}
              disabled={disabled}
            >
              🎬 Start Countdown
            </button>
            <button 
              className="btn secondary" 
              onClick={takePhoto}
              disabled={disabled}
            >
              📸 Capture Now
            </button>
          </div>
          
          <div className="camera-tips">
            <p>💡 <strong>Tips for best results:</strong></p>
            <ul>
              <li>Ensure good lighting</li>
              <li>Position yourself in the center</li>
              <li>Show your beautiful smile! 😊</li>
            </ul>
          </div>
        </>
      )}

      {preview && (
        <div className="preview fade-in">
          <div className="preview-header">
            <h4>✨ Perfect! Here's your photo</h4>
          </div>
          <img 
            src={preview} 
            alt="Preview capture" 
            className="preview-image"
          />
          <div className="camera-actions">
            <button 
              className="btn secondary" 
              onClick={retake}
              disabled={disabled}
            >
              🔁 Retake
            </button>
            <button 
              className="btn primary" 
              onClick={usePhoto}
              disabled={disabled}
            >
              ✨ Reveal My Aura
            </button>
          </div>
        </div>
      )}
    </div>
  );
}