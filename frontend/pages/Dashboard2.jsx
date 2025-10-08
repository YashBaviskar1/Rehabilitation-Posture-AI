import axios from "axios";
import {
  Activity,
  Home,
  TrendingUp,
  User,
  Video,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  RotateCcw,
  Calendar,
  Clock,
  Target,
  Award,
  ChevronRight,
  LogOut,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import PatientComponent from "./PatientComponent";
import DoctorComponent from "./DoctorComponent";
const isDev = import.meta.env.MODE == "development";

export default function Dashboard({}) {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user")));
  const [selectedExercise, setSelectedExercise] = useState(null);
  const navigate = useNavigate();
  //   const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    console.log("dashboard", user);

    if (!user) {
      window.alert("No user found");
      navigate("/");
      return;
    }

    // if (user.role != "patient") {
    //   window.alert("You're not a patient");
    //   navigate("/");
    //   return;
    // }

    setUser(user);
  }, []);

  return (
    <div className="min-h-screen p-4 bg-gray-200 text-gray-800">
      {/* Header */}
      <header className="sticky top-0 shadow-md p-4 flex justify-between bg-white">
        <div className="flex items-center gap-3">
          <div className="bg-blue-500 text-white p-2 rounded">
            <Activity />
          </div>
          <div className="">
            <h1 className="font-bold text-lg">PhysioTrack</h1>
            <p className="text-sm text-gray-500">AI-Powered Physical Therapy</p>
          </div>
        </div>

        {/* <nav className="flex gap-2">
          {["dashboard", "exercises", "progress", "profile"].map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 rounded ${
                activeTab === tab
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700"
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {
                {
                  dashboard: <Home className="inline mr-1" />,
                  exercises: <Activity className="inline mr-1" />,
                  progress: <TrendingUp className="inline mr-1" />,
                  profile: <User className="inline mr-1" />,
                }[tab]
              }
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav> */}

        {/* <div className="flex items-center gap-2 ">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-600">
            Today: {new Date().toLocaleDateString()}
          </span>
        </div> */}

        <div className="flex items-center gap-2 ">
          <ProfileDropdown />
        </div>
      </header>

      <main className="mt-6">
        <section className="p-6 rounded-2xl mb-6 shadow-md bg-gradient-to-r from-blue-500 to-cyan-500">
          <h2 className="text-2xl font-bold mb-2 text-white">
            Welcome back, {user && user.name}!
          </h2>
          {/* <p className=" text-white">
                You have 2 exercises remaining today. Keep up the great work!
              </p> */}
          {/* <div className="mt-4 flex gap-6">
                <div className="flex items-center gap-2">
                  <Target className="text-blue-700" />
                  <div>
                    <p className="text-sm text-white">Weekly Goal</p>
                    <p className="font-semibold text-white">5/7 Days</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Award className="text-blue-700" />
                  <div>
                    <p className="text-sm text-white">Current Streak</p>
                    <p className="font-semibold text-white">12 Days</p>
                  </div>
                </div>
              </div> */}
        </section>
        {/* Patient Dashboard */}
        {activeTab === "dashboard" && user.role == "patient" && (
          <>
            <PatientComponent
              selectedExercise={selectedExercise}
              setSelectedExercise={setSelectedExercise}
            />
          </>
        )}
        {/* Doctor Dashboard */}
        {activeTab === "dashboard" && user.role == "doctor" && (
          <>
            <DoctorComponent />
          </>
        )}
      </main>
    </div>
  );
}

const ProfileDropdown = () => {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  // Close dropdown if clicked outside
  //   useEffect(() => {
  //     const handleClickOutside = (e) => {
  //       if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
  //         setOpen(false);
  //       }
  //     };
  //     document.addEventListener("mousedown", handleClickOutside);
  //     return () => document.removeEventListener("mousedown", handleClickOutside);
  //   }, []);

  const handleLogout = async () => {
    await axios
      .get(`${isDev ? "http://localhost:8000" : ""}/api/auth/logout`, {
        withCredentials: true,
      })
      .then((res) => {
        console.log(`Logout result:`);
        console.log(res.data);
        localStorage.removeItem("user");
        navigate("/");
      })
      .catch((error) => {
        console.log(`Logout Error:`);
        console.log(error);
      });
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Avatar Button */}
      <button
        onClick={() => setOpen(!open)}
        className="p-1 bg-blue-500 rounded-full bg-primary text-white flex items-center justify-center hover:opacity-90 transition"
      >
        <User className="text-white  " size={36} />
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded-md shadow-lg z-50">
          <button
            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            onClick={() => console.log("Go to Profile")}
          >
            <User className="w-4 h-4" />
            Profile
          </button>
          <button
            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
            onClick={handleLogout}
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      )}
    </div>
  );
};
