import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

const videoConstraints = {
  width: 720,
  height: 540,
  facingMode: "user",
};

export default function CameraCapture({ onCapture, preview, setPreview, onSendToServer, onResult }) {
  const webcamRef = useRef(null);
  const [captured, setCaptured] = useState(false);
  const [sending, setSending] = useState(false);

  const capture = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setPreview(imageSrc);
    setCaptured(true);
    onCapture(imageSrc);
  };

  const retake = () => {
    setPreview(null);
    setCaptured(false);
  };

  const send = async () => {
    if (!preview) return;
    setSending(true);
    try {
      const blob = await (await fetch(preview)).blob();
      const form = new FormData();
      form.append("file", blob, "capture.jpg");
      const res = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error("Upload failed");
      const outBlob = await res.blob();
      const url = URL.createObjectURL(outBlob);
      onResult(url);
    } catch (err) {
      alert("Upload failed. Check backend or network.");
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="camera-wrap">
      {!captured && (
        <>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="webcam"
          />
          <div className="cam-controls">
            <button className="btn primary" onClick={capture}>Capture</button>
          </div>
        </>
      )}

      {captured && preview && (
        <div className="preview-box">
          <img src={preview} className="preview-img" alt="preview" />
          <div className="preview-actions">
            <button className="btn ghost" onClick={retake}>Retake</button>
            <button className="btn primary" onClick={send} disabled={sending}>
              {sending ? "Sending..." : "Use Photo"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
