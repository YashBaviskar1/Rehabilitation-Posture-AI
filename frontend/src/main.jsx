import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App2.jsx";
// import ObjectDetection from "./ObjectDetection.jsx";
import Dashboard from "../pages/Dashboard2.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    {/* <ObjectDetection /> */}
    {/* <Dashboard /> */}
    <App />
  </StrictMode>
);
