import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import tempImg from "./assets/react.svg";
const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL;

export default function ObjectDetection() {
  const webcamRef = useRef(null);
  const ws = useRef(null);
  const intervalRef = useRef(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedImage, setProcessedImage] = useState(null);

  const videoConstraints = {
    width: 320,
    height: 240,
    facingMode: "user",
  };

  async function captureAndProcess() {
    if (webcamRef.current && ws.current.readyState === WebSocket.OPEN) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        const base64Data = imageSrc.split(",")[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++)
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        const byteArray = new Uint8Array(byteNumbers);
        ws.current.send(byteArray.buffer);
      }
    }
  }

  useEffect(() => {
    ws.current = new WebSocket(WEBSOCKET_URL + "/api/analyse/ws/yolo");

    ws.current.onopen = () => {
      console.log("Object Detection Websocket Established");
    };

    ws.current.onmessage = (event) => {
      const blob = new Blob([event.data], { type: "image/jpeg" });
      const url = URL.createObjectURL(blob);
      setProcessedImage((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
    };

    ws.current.onclose = () => {
      console.log("Websocket connection closed!");
    };

    ws.current.onerror = (error) => {
      console.log(`Websocket error occured!\n ${error}`);
      console.error(error);
    };

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (ws.current) ws.current.close();
      if (processedImage) URL.revokeObjectURL(processedImage);
    };
  }, []);

  useEffect(() => {
    if (isProcessing) {
      // Start interval
      intervalRef.current = setInterval(captureAndProcess, 62);
      console.log("Starting interval");
    } else {
      // Stop interval if it exists
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        console.log("Stopped interval");
      }
    }

    // Cleanup on component unmount or when isProcessing changes
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        console.log("Interval cleared on unmount");
      }
    };
  }, [isProcessing]);

  return (
    <div className="flex flex-col gap-4 items-center p-6">
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        screenshotQuality={0.3}
        width={videoConstraints.width}
        height={videoConstraints.height}
        videoConstraints={videoConstraints}
        className="border-2 border-white"
      />
      <button
        onClick={() => {
          setIsProcessing(!isProcessing);
        }}
        className="text-white text-3xl bg-blue-400 mt-6 py-2 w-[40%] m-auto rounded-md"
      >
        Start Detecting
      </button>
      <div>
        <h4 className="text-white text-2xl text-center mb-8">
          YOLO Object Detection
        </h4>
        {
          <img
            src={processedImage || tempImg}
            alt="YOLO output"
            width={320}
            height={240}
          />
        }
      </div>
    </div>
  );
}
