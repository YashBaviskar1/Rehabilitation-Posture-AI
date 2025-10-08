import { useEffect, useRef, useState } from "react";
import WebcamComponent from "./Webcam";
import tempImg from "./assets/react.svg";
const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL;

export default function App() {
  const websocketRef = useRef(null);

  const [text, setText] = useState("");
  const [processedImage, setProcessedImage] = useState(tempImg);
  const [processError, setProcessError] = useState("");
  const webcamRef = useRef(null);

  //Function to send message to websocket
  async function sendMessage(msg) {
    if (
      websocketRef.current &&
      websocketRef.current.readyState === WebSocket.OPEN
    ) {
      if (msg.type == "image") {
        // console.log("Creating blob message");

        // Convert base64 to binary to send efficiently
        const base64Data = msg.image.split(",")[1]; // Remove data prefix
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);

        websocketRef.current.send(byteArray.buffer); // Send as ArrayBuffer
        // console.log("Blob message sent");
      }
    }
  }

  //Setup websocket connection on mounting of component and clear on unmount
  useEffect(() => {
    console.log("Running effect to setup WebSocket");

    websocketRef.current = new WebSocket(
      `${WEBSOCKET_URL}/api/analyse/ws/test`
    );
    websocketRef.current.onopen = () => {
      console.log("Websocket connected!");
      if (websocketRef.current) {
        // websocketRef.current.send("Hello from frontend");

        // Convert base64 to binary to send efficiently
        const imageSrc = webcamRef.current.getScreenshot();
        console.log("Getting getScreenshot");
        const base64Data = imageSrc.split(",")[1]; // Remove data prefix
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);

        websocketRef.current.send(byteArray.buffer); // Send as ArrayBuffer
        console.log("Initial photo sent");
      }
    };

    websocketRef.current.onclose = () => {
      console.log("Websocket connection closed!");
    };

    websocketRef.current.onerror = (error) => {
      console.log(`Websocket error occured!\n ${error}`);
      console.error(error);
    };

    websocketRef.current.onmessage = (event) => {
      if (event.data instanceof Blob) {
        // console.log("Blob recieved");
        const blob = new Blob([event.data], { type: "image/jpeg" });
        const url = URL.createObjectURL(blob);
        setProcessedImage((prev) => {
          if (prev) URL.revokeObjectURL(prev); // free old URL
          return url;
        });
        // console.log("Blob set...");
      }
    };

    console.log("Setup complete");

    return () => {
      websocketRef.current.close();
      console.log("Socket closed");
    };
  }, []);

  return (
    <div>
      <WebcamComponent
        sendMessage={sendMessage}
        processedImage={processedImage}
        processError={processError}
        webcamRef={webcamRef}
        setProcessError={setProcessError}
        setProcessedImage={setProcessedImage}
      />
    </div>
  );
}
