import React, { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";

export default function App() {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  const displayRef = useRef(null);
  const [score, setScore] = useState(null);
  const [ws, setWs] = useState(null);
  const camDim = {
    height: 640,
    width: 640,
  };

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/api/pose/ws/analyze");
    setWs(socket);

    socket.onmessage = (event) => {
      if (typeof event.data === "string" && event.data.startsWith("SCORE:")) {
        const finalScore = parseFloat(event.data.replace("SCORE:", ""));
        setScore(finalScore);
      } else {
        const blob = new Blob([event.data], { type: "image/jpeg" });
        const url = URL.createObjectURL(blob);
        displayRef.current.src = url;
      }
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;

      const canvas = canvasRef.current;
      // const ctx = canvas.getContext("2d");
      const img = imgRef.current;

      // ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // canvas.toBlob(
      //   (blob) => {
      //     if (blob) {
      //       blob.arrayBuffer().then((buffer) => {
      //         ws.send(buffer);
      //       });
      //     }
      //   },
      //   "image/jpeg",
      //   0.9
      // );

      const imageSrc = imgRef.current.getScreenshot(); // base64 JPEG

      if (imageSrc) {
        // Convert base64 to binary and send over WebSocket
        fetch(imageSrc)
          .then((res) => res.blob())
          .then((blob) => blob.arrayBuffer())
          .then((buffer) => ws.send(buffer));
      }
    }, 100); // ~10 FPS

    return () => clearInterval(interval);
  }, [ws]);

  return (
    <div>
      <h2>DroidCam Live Analysis</h2>
      <p>Score: {score !== null ? `${score.toFixed(2)}%` : "Processing..."}</p>

      <div className="flex justify-center">
        {/* MJPEG Stream */}
        {/* <img
        ref={imgRef}
        src="http://192.168.0.101:4747/video"
        alt="DroidCam Feed"
        onLoad={() => {
          const img = imgRef.current;
          const canvas = canvasRef.current;
          canvas.width = img.width;
          canvas.height = img.height;
        }}
        style={{ width: 640, display: "none" }}
      /> */}
        <Webcam
          audio={false}
          ref={imgRef}
          mirrored={true}
          screenshotFormat="image/jpeg"
          screenshotQuality={0.7}
          width={camDim.width}
          height={camDim.height}
          videoConstraints={{
            ...camDim,
            facingMode: "user", // use "environment" for rear camera on mobile
          }}
          style={{
            position: "absolute",
            top: "0", // way off-screen
            left: "0",
            opacity: 0,
          }}
        />

        {/* Canvas used to extract frames */}
        {/* <canvas ref={canvasRef} style={{ display: "none" }} /> */}

        {/* Processed output from backend */}
        <img
          ref={displayRef}
          alt="Processed Frame"
          style={{ width: camDim.width }}
        />
      </div>
    </div>
  );
}
