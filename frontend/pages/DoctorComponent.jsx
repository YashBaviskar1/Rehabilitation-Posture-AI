import axios from "axios";
import { CheckCircle, Clock, User } from "lucide-react";
import { useEffect, useState } from "react";
import ScoreLineChart from "./GraphComponent";
const isDev = import.meta.env.MODE == "development";

export default function DoctorComponent() {
  const [patients, setPatients] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [open, setOpen] = useState(false);
  const [currPatient, setCurrPatient] = useState(null);
  const [showPatientId, setShowPatientId] = useState(null);
  const [exerciseObj, setExerciseObj] = useState({
    id: null,
    title: "",
  });
  const [removeExerciseObj, setRemoveExerciseObj] = useState({
    id: null,
    title: "",
  });

  async function getPatients() {
    await axios
      .get(`${isDev ? "http://localhost:8000" : ""}/api/users/patients`, {
        withCredentials: true,
      })
      .then((res) => {
        console.log("Doctor Dashboard:\n");
        console.log(res.data);
        setPatients(res.data);
      })
      .catch((error) => {
        console.log("Doctor Dashboard:\n");
        console.log(error);
      });
  }

  async function getExercises() {
    await axios
      .get(`${isDev ? "http://localhost:8000" : ""}/api/exercises/`, {
        withCredentials: true,
      })
      .then((res) => {
        console.log("All Exercises Dashboard:\n");
        console.log(res.data);
        setExercises(res.data);
      })
      .catch((error) => {
        console.log("All Exercises Dashboard:\n");
        console.log(error);
      });
  }

  async function addExercise() {
    const addExercisePayload = {
      patient_id: currPatient,
      exercise_ids: [exerciseObj.id],
    };

    await axios
      .post(
        `${isDev ? "http://localhost:8000" : ""}/api/exercises/assign`,
        addExercisePayload,
        {
          withCredentials: true,
        }
      )
      .then((res) => {
        console.log("Add Exercises Dashboard:\n");
        console.log(res.data);
        window.location.reload();
      })
      .catch((error) => {
        console.log("Add Exercises Dashboard:\n");
        console.log(error);
      });
  }

  async function removeExercise() {
    const removeExercisePayload = {
      patient_id: currPatient,
      exercise_ids: [exerciseObj.id],
    };

    await axios
      .delete(
        `${isDev ? "http://localhost:8000" : ""}/api/exercises/deassign`,
        {
          data: removeExercisePayload,
          withCredentials: true,
        }
      )
      .then((res) => {
        console.log("Remove Exercises Dashboard:\n");
        console.log(res.data);
        window.location.reload();
      })
      .catch((error) => {
        if (
          error.response.data.detail.includes(
            "one of the given exercises are assigned to this user"
          )
        ) {
          window.alert(error.response.data.detail);
          return;
        }
        console.log("Remove Exercises Dashboard:\n");
        console.log(error);
      });
  }

  useEffect(() => {
    getPatients();
    getExercises();
  }, []);

  return (
    <>
      {showPatientId && (
        <PatientScoreGraph
          patient_id={showPatientId}
          setShowPatientId={setShowPatientId}
        />
      )}
      <h3 className="text-xl font-bold mb-4">Patient Records</h3>
      {/* Patients container */}
      <div className="grid grid-cols-2 gap-6 lg:grid-cols-3">
        {patients.map((pt) => (
          <div
            key={pt.id}
            className="p-4 h-fit border rounded-xl bg-white shadow-sm border-gray-300"
          >
            <div className="w-full">
              <div>
                <div className="flex justify-between">
                  <p className="font-bold text-2xl">{pt.username}</p>
                  <button
                    className="bg-cyan-500 rounded-md text-white px-4"
                    onClick={() => {
                      setShowPatientId(pt.id);
                    }}
                  >
                    Progress
                  </button>
                </div>
                <p>
                  <strong>Age: </strong>
                  {pt.age}
                </p>
              </div>
              {/* {ex.completed && <CheckCircle className="text-green-500" />} */}
            </div>

            <div className="mt-3 space-y-1 text-md">
              <p>
                <strong>Exercises: </strong>
                {pt.exercises.map((_) => {
                  return _.title + ", ";
                })}
              </p>
              {currPatient == pt.id && (
                <div className="bg-gray-200 flex flex-wrap pl-1 py-2 rounded-md gap-2 relative">
                  {/* Add Exercises Section */}
                  <p className="font-bold p-[0.5px]">Exercises: </p>
                  <input
                    placeholder="Exercise IDs"
                    className=" border-gray-500 m-auto border-2 border-solid p-[0.5px] w-full"
                    value={exerciseObj.title}
                    readOnly
                    onFocus={() => {
                      setOpen(true);
                    }}
                    onBlur={() => {
                      setOpen(false);
                    }}
                  />
                  <button
                    className={`w-[25%] rounded text-white m-auto ${
                      pt.completed ? "bg-gray-500" : "bg-blue-600"
                    }`}
                    onClick={addExercise}
                  >
                    Add
                  </button>
                  <button
                    className={`w-[25%] rounded text-white m-auto ${
                      pt.completed ? "bg-gray-500" : "bg-blue-600"
                    }`}
                    onClick={removeExercise}
                  >
                    Remove
                  </button>
                  {/* Dropdown */}
                  {open && (
                    <div className="absolute top-full w-full left-0 mt-2  bg-white border border-gray-200 rounded-md shadow-lg z-50">
                      {/* <button
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => console.log("Go to Profile")}
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </button> */}
                      {exercises.map((ex, id) => {
                        return (
                          <div
                            key={id}
                            className="hover:bg-gray-300 px-4 py-1 "
                            onMouseEnter={() => {
                              setExerciseObj({ id: ex.id, title: ex.title });
                            }}
                          >
                            {ex.title}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
              {/* <p>
                Difficulty: <span className="italic">{}</span>
              </p>
              <p>
                Last Score: <span className="font-bold">{}%</span>
              </p> */}
            </div>

            <button
              className={`mt-3 w-full py-2 px-4 rounded text-white ${
                pt.completed ? "bg-gray-500" : "bg-blue-600"
              }`}
              onClick={(e) => {
                setCurrPatient(pt.id);
                if (currPatient == pt.id) {
                  setCurrPatient(null);
                  setExerciseObj({ id: null, title: "" });
                }
              }}
            >
              {currPatient == pt.id ? "Cancel" : "Edit"}
            </button>
          </div>
        ))}
      </div>
    </>
  );
}

function PatientScoreGraph({ patient_id, setShowPatientId }) {
  const [scores, setScores] = useState();

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
        `${
          isDev ? "http://localhost:8000" : ""
        }/api/scores/patient/${patient_id}`,
        {
          withCredentials: true,
        }
      )
      .then((res) => {
        console.log("Get Scores Doctor Dashboard:\n");
        console.log(res.data);
        let tempScores = res.data;
        tempScores.forEach((__, i) => {
          const dateObj = new Date(__.timestamp);

          const date = dateObj.getDate(); // day of the month (1-31)
          const hours = dateObj.getHours();
          const minutes = dateObj.getMinutes().toString().padStart(2, "0");

          const formatted = `${date} ${
            monthNames[dateObj.getMonth()]
          }: ${hours}:${minutes}`;

          __.timestamp = formatted;
        });
        setScores(tempScores);
      })
      .catch((error) => {
        console.log("Get Scores Doctor Dashboard:\n");
        console.log(error);
      });
  }

  useEffect(() => {
    getScores();
  }, []);

  return (
    <section className="w-full h-full z-50 fixed top-0 left-0 backdrop:blur bg-black/80">
      <div className="m-auto md:w-[75%] lg:w-[60%] mt-24">
        {scores && (
          <div className="items-end flex flex-col">
            <button
              className=" text-white px-2 text-2xl font-medium"
              onClick={() => {
                setShowPatientId(null);
              }}
            >
              X
            </button>
            <ScoreLineChart scores={scores} />
          </div>
        )}
      </div>
    </section>
  );
}
