import { useState } from "react";
import { LogIn, UserPlus, Lock, Mail } from "lucide-react";
import axios from "axios";
import { Navigate, useNavigate } from "react-router-dom";
const isDev = import.meta.env.MODE == "development";

export default function AuthPage({}) {
  const [isSignup, setIsSignup] = useState(false);
  const [loginFields, setLoginFields] = useState({
    email: "",
    password: "",
  });
  const [signUpFields, setSignUpFields] = useState({
    email: "",
    password: "",
    name: "",
    confirmPassword: "",
  });

  const navigate = useNavigate();

  function updateLoginFields(field, value) {
    setLoginFields((prev) => ({ ...prev, [field]: value }));
  }

  function updateSignUpFields(field, value) {
    setSignUpFields((prev) => ({ ...prev, [field]: value }));
  }

  async function postLogin() {
    await axios
      .post(
        `${isDev ? "http://localhost:8000" : ""}/api/auth/login`,
        {
          username: loginFields.email,
          password: loginFields.password,
        },
        {
          withCredentials: true,
        }
      )
      .then((res) => {
        console.log(`Login result:`);
        console.log(res.data);
        localStorage.setItem("user", JSON.stringify(res.data));
        navigate("/dashboard");
      })
      .catch((error) => {
        console.log(`Login Error:`);
        console.log(error);
      });
  }

  async function postRegister() {
    await axios
      .post(`${isDev ? "http://localhost:8000" : ""}/api/auth/register`, {
        name: signUpFields.name,
        username: signUpFields.email,
        password: signUpFields.password,
        role: "patient",
      })
      .then((res) => {
        console.log(`Register result:`);
        console.log(res.data);
        window.alert("Success");
        setIsSignup(false);
      })
      .catch((error) => {
        console.log(`Register Error:`);
        console.log(error);
      });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-8 space-y-6 animate-fade-in">
        <div className="text-center">
          <div className="flex justify-center mb-2">
            {isSignup ? (
              <UserPlus className="h-8 w-8 text-purple-600" />
            ) : (
              <LogIn className="h-8 w-8 text-blue-600" />
            )}
          </div>
          <h2 className="text-2xl font-bold text-gray-800">
            {isSignup ? "Create an Account" : "Welcome Back"}
          </h2>
          <p className="text-sm text-gray-500">
            {isSignup
              ? "Join PhysioTrack to get started"
              : "Log in to continue"}
          </p>
        </div>

        <div className="space-y-4">
          {isSignup ? (
            <div>
              {/* Name field */}
              <label className="block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                type="text"
                placeholder="Jane Doe"
                value={signUpFields.name}
                name="name"
                onChange={(e) => {
                  updateSignUpFields(e.target.name, e.target.value);
                }}
                className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none"
              />
              {/* Email field */}
              <label className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={signUpFields.email}
                  name="email"
                  onChange={(e) => {
                    updateSignUpFields(e.target.name, e.target.value);
                  }}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>
              {/* Password field */}
              <label className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  placeholder="password"
                  value={signUpFields.password}
                  name="password"
                  onChange={(e) => {
                    updateSignUpFields(e.target.name, e.target.value);
                  }}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>
              {/* Confim Password field */}
              <label className="block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  placeholder="confirm password"
                  value={signUpFields.confirmPassword}
                  name="confirmPassword"
                  onChange={(e) => {
                    updateSignUpFields(e.target.name, e.target.value);
                  }}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>
              {/* Button */}
              <button
                className="w-full mt-4 py-2 px-4 text-white font-semibold rounded-md bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 transition"
                onClick={postRegister}
              >
                Sign Up
              </button>
            </div>
          ) : (
            <div>
              {/* Email field */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    placeholder="you@example.com"
                    value={loginFields.email}
                    name="email"
                    onChange={(e) => {
                      updateLoginFields(e.target.name, e.target.value);
                    }}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  />
                </div>
              </div>
              {/* Password  field */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    placeholder="password"
                    value={loginFields.password}
                    name="password"
                    onChange={(e) => {
                      updateLoginFields(e.target.name, e.target.value);
                    }}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  />
                </div>
              </div>
              {/* Button */}
              <button
                className="w-full mt-4 py-2 px-4 text-white font-semibold rounded-md bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 transition"
                onClick={postLogin}
              >
                Log In
              </button>
            </div>
          )}
        </div>

        <div className="text-center text-sm text-gray-600">
          {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            onClick={() => setIsSignup(!isSignup)}
            className="text-blue-600 font-medium hover:underline transition"
          >
            {isSignup ? "Log in" : "Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
}
