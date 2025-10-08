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

import { useEffect, useState } from "react";

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

  const handleStartExercise = (id) => {
    setSelectedExercise(id);
    setIsExercising(true);
  };

  const handleStopExercise = () => {
    setIsExercising(false);
  };

  useEffect(() => {
    const tempUser = JSON.parse(localStorage.getItem("user"));
    setPatient(tempUser);
  }, []);

  return (
    <>
      {!selectedExercise && (
        <section>
          <h3 className="text-xl font-bold mb-4">Today's Exercises</h3>
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
                  >
                    {ex.completed ? "Practice Again" : "Start Exercise"}
                  </button>
                </div>
              ))}
          </div>
        </section>
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
