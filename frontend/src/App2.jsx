import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard2";
import AuthPage from "../pages/Auth";
import { useState } from "react";

export default function App() {
  // const [user, setUser] = useState({ username: "" });

  return (
    <div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AuthPage />}></Route>
          <Route path="/dashboard" element={<Dashboard />}></Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}
