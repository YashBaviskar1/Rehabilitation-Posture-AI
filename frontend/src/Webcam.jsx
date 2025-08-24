import axios from "axios";
import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import tempImg from "./assets/react.svg";

export default function WebcamComponent({
  sendMessage = null,
  processedImage = null,
  processError = null,
  webcamRef = null,
  setProcessedImage = () => {
    console.log("No function");
  },
  setProcessError = () => {
    console.log("No function");
  },
}) {
  const intervalRef = useRef(null);
  const [originaImage, setOriginaImage] = useState(tempImg);
  const [loading, setLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const videoConstraints = {
    width: 480,
    height: 480,
    facingMode: "user",
  };

  async function captureAndProcess() {
    const imageSrc = webcamRef.current.getScreenshot();
    setOriginaImage(imageSrc);
    //Analysis using http POST methods
    // setLoading(true);
    // await axios
    //   .post("/api/analyse/test", {
    //     image: imageSrc,
    //   })
    //   .then((res) => {
    //     setProcessedImage(res.data.processed_image);
    //     setProcessError(res.data.message);
    //   })
    //   .catch((error) => {
    //     console.log("Image process error:\n", error);
    //     setProcessError(`${error}`);
    //   })
    //   .finally(() => {
    //     setLoading(false);
    //   });

    //Analysis using websocket communication
    sendMessage({ type: "image", image: imageSrc });
  }

  useEffect(() => {
    if (isProcessing) {
      // Start interval
      intervalRef.current = setInterval(captureAndProcess, 40);
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
    <div className="flex flex-col mt-[50px]">
      <h2 className="text-white w-full text-center">Live Video</h2>
      <Webcam
        ref={webcamRef}
        audio={false}
        height={videoConstraints.height}
        width={videoConstraints.width}
        videoConstraints={videoConstraints}
        onUserMediaError={(err) => {
          console.error("Webcam error:", err);
        }}
      />
      <button
        onClick={() => {
          setIsProcessing(!isProcessing);
        }}
        className="text-white text-3xl bg-amber-700 mt-6 w-[60%] m-auto rounded-md"
      >
        Analyse
      </button>

      <div className="text-2xl text-red-500 my-10 mx-4">
        Error: {processError}
      </div>

      <div className="flex gap-4 my-10 mx-4">
        {originaImage && (
          <>
            {/* <h2>Original Image</h2> */}
            <img
              src={originaImage}
              alt="Original"
              style={{
                width: `${videoConstraints.width}px`,
                border: "1px solid white",
              }}
            />
          </>
        )}

        {processedImage && (
          <>
            {/* <h2>Processed Image</h2> */}
            <img
              src={processedImage}
              alt="Processed"
              style={{
                width: `${videoConstraints.width}px`,
                border: "1px solid white",
              }}
            />
          </>
        )}
      </div>
    </div>
  );
}
