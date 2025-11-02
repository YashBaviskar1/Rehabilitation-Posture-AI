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
import axios from "axios";
import ScoreLineChart from "./GraphComponent";
import Webcam from "react-webcam";
const isDev = import.meta.env.MODE == "development";

export default function PatientComponent({
  selectedExercise,
  setSelectedExercise,
}) {
  const todayExercises = [
    {
      id: 1,
      name: "Shoulder Flexion",
      duration: "3 min",
      sets: 3,
      reps: 10,
      completed: false,
      difficulty: "Medium",
      lastScore: 85,
    },
    {
      id: 2,
      name: "Knee Extension",
      duration: "5 min",
      sets: 2,
      reps: 15,
      completed: true,
      difficulty: "Easy",
      lastScore: 92,
    },
    {
      id: 3,
      name: "Hip Abduction",
      duration: "4 min",
      sets: 3,
      reps: 12,
      completed: false,
      difficulty: "Hard",
      lastScore: 78,
    },
  ];

  const [isExercising, setIsExercising] = useState(false);
  const [patient, setPatient] = useState(null);
  const [scores, setScores] = useState([]);
  const [exercise, setExercise] = useState(null);

  const handleStartExercise = (id) => {
    setSelectedExercise(id);
    setIsExercising(true);
  };

  const handleStopExercise = () => {
    setIsExercising(false);
  };

  async function getScores() {
    const monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];

    await axios
      .get(
        `${isDev ? "http://localhost:8000" : ""}/api/scores/patient/${
          patient.id
        }`,
        {
          withCredentials: true,
        }
      )
      .then((res) => {
        console.log("Get Scores:\n");
        console.log(res.data);
        let tempScores = res.data;
        tempScores.forEach((__, i) => {
          const dateObj = new Date(__.timestamp);

          const date = dateObj.getDate(); // day of the month (1-31)
          const hours = dateObj.getHours();
          const minutes = dateObj.getMinutes().toString().padStart(2, "0");

          const formatted = `${date} ${
            monthNames[dateObj.getMonth()]
          }: ${hours}:${minutes}, ${__.exercise}`;

          __.timestamp = formatted;
        });
        setScores(tempScores);
      })
      .catch((error) => {
        console.log("Get Scores:\n");
        console.log(error);
      });
  }

  useEffect(() => {
    const tempUser = JSON.parse(localStorage.getItem("user"));
    setPatient(tempUser);
  }, []);

  useEffect(() => {
    if (!patient) return;
    getScores();
  }, [patient]);

  return (
    <>
      {exercise && (
        <PatientExercise
          exercise={exercise}
          setExercise={setExercise}
          patient={patient}
        />
      )}
      {!selectedExercise && (
        <>
          {/* Exercises List */}
          <section className="mb-8">
            <h3 className="text-xl font-bold mb-4">Exercises Assigned</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {patient &&
                patient.exercises.map((ex) => (
                  <div
                    key={ex.id}
                    className="p-4 border rounded-xl bg-white shadow-sm border-gray-300"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="text-xl font-bold">{ex.title}</h4>
                        {/* <div className="text-sm text-gray-600 flex items-center gap-1">
                      <Clock className="w-4 h-4" /> {ex.duration}
                    </div> */}
                      </div>
                      {/* {ex.completed && <CheckCircle className="text-green-500" />} */}
                    </div>

                    {/* <div className="mt-3 space-y-1 text-sm">
                  <p>
                    Sets x Reps:{" "}
                    <strong>
                      {ex.sets} x {ex.reps}
                    </strong>
                  </p>
                  <p>
                    Difficulty: <span className="italic">{ex.difficulty}</span>
                  </p>
                  <p>
                    Last Score:{" "}
                    <span className="font-bold">{ex.lastScore}%</span>
                  </p>
                </div> */}

                    <button
                      className={`mt-3 w-full py-2 px-4 rounded text-white ${
                        !ex.title ? "bg-gray-500" : "bg-blue-600"
                      }`}
                      onClick={() => {
                        setExercise(ex);
                      }}
                    >
                      {ex.completed ? "Practice Again" : "Start Exercise"}
                    </button>
                  </div>
                ))}
            </div>
          </section>
          {/* Scores Graph */}
          <h1 className="text-xl font-bold mb-4 ">Score History</h1>
          <section className="flex justify-center">
            <div className="xl:w-[70%] w-full">
              <ScoreLineChart scores={scores} />
            </div>
          </section>
        </>
      )}

      {selectedExercise && (
        <section className="mt-8 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">
              {todayExercises.find((e) => e.id === selectedExercise)?.name}
            </h2>
            <button
              className="text-sm text-blue-600 underline"
              onClick={() => setSelectedExercise(null)}
            >
              Back to Dashboard
            </button>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="relative bg-gray-100 rounded aspect-video flex items-center justify-center">
                <Video className="w-24 h-24 text-gray-300" />
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-4">
                  <button
                    onClick={() => setIsExercising(!isExercising)}
                    className="bg-blue-600 text-white px-6 py-2 rounded shadow"
                  >
                    {isExercising ? (
                      <>
                        <Pause className="inline mr-2" /> Pause
                      </>
                    ) : (
                      <>
                        <Play className="inline mr-2" /> Start
                      </>
                    )}
                  </button>
                  <button className="bg-white border px-6 py-2 rounded shadow">
                    <RotateCcw className="inline mr-2" /> Reset
                  </button>
                </div>
              </div>

              <div className="p-4 border rounded bg-white shadow-sm">
                <h3 className="font-semibold mb-2">Exercise Instructions</h3>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Stand with feet shoulder-width apart</li>
                  <li>Slowly raise your arms to shoulder height</li>
                  <li>Hold for 2 seconds at the top</li>
                  <li>Lower arms slowly back to starting position</li>
                </ol>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-green-100 p-4 rounded">
                <h4 className="text-sm font-semibold text-green-800">
                  Current Score
                </h4>
                <p className="text-3xl font-bold">89%</p>
                <p className="text-sm text-green-700">Excellent form!</p>
              </div>
              <div className="bg-yellow-100 p-4 rounded">
                <h4 className="text-sm font-semibold text-yellow-800">Tips</h4>
                <ul className="list-disc list-inside text-sm">
                  <li>Keep your core engaged</li>
                  <li>Maintain steady breathing</li>
                  <li>Focus on controlled movement</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      )}
    </>
  );
}

function PatientExercise({ exercise, setExercise, patient }) {
  const [score, setScore] = useState();
  const [ws, setWs] = useState(null);
  const imgRef = useRef(null);
  const displayRef = useRef(null);

  const camDim = {
    height: 480,
    width: 720,
  };

  async function assignScore() {
    const addScorePayload = {
      exercise_id: exercise.id,
      patient_id: patient.id,
      timestamp: new Date().getTime(),
      score: Math.floor(score),
    };

    await axios
      .post(
        `${isDev ? "http://localhost:8000" : ""}/api/scores/add`,
        addScorePayload,
        {
          withCredentials: true,
        }
      )
      .then((res) => {
        console.log("Add Score:\n");
        console.log(res.data);
        window.location.reload();
      })
      .catch((error) => {
        console.log("Add Score:\n");
        console.log(error);
      });
  }

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

    socket.onopen = () => {
      // Send exercise type first
      socket.send(
        JSON.stringify({
          exercise_id: exercise.id,
          patient_id: patient.id,
          timestamp: new Date().getTime(),
        })
      );
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;

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

  useEffect(() => {
    if (!score) {
      console.log("No score yet");
      return;
    }

    assignScore();
  }, [score]);

  return (
    <section className="w-full h-full z-50 fixed top-0 left-0 backdrop:blur bg-black/80">
      <div className="m-auto md:w-[75%] lg:w-[60%] mt-24">
        <div className="flex flex-col items-center">
          {/* Close Button */}
          <button
            className=" text-white px-2 text-2xl font-medium ml-auto"
            onClick={() => {
              setExercise(null);
            }}
          >
            X
          </button>

          {/* Webcam Component */}
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
          {/* Score Display */}
          {score && (
            <div className="text-white bg-green-500 px-4 py-2 my-4 rounded-sm w-[50%] text-2xl text-center">
              Excercise Completed
              <br />
              Final Score: {score}
            </div>
          )}
          {/* Processed output from backend */}
          <img
            ref={displayRef}
            alt="Processed Frame"
            style={{ width: camDim.width }}
          />

          {/* <button className="text-white bg-blue-500 px-4 py-2 mt-4 rounded-sm w-[50%]">
            Toggle
          </button> */}
        </div>
      </div>
    </section>
  );
}
