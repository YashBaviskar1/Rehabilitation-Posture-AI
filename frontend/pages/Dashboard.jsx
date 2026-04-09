import { useState } from "react";
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
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isExercising, setIsExercising] = useState(false);
  const [selectedExercise, setSelectedExercise] =
    (useState < number) | (null > null);

  // Sample data for exercises
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

  const recentProgress = [
    { date: "Mon", score: 78 },
    { date: "Tue", score: 82 },
    { date: "Wed", score: 85 },
    { date: "Thu", score: 88 },
    { date: "Fri", score: 90 },
    { date: "Sat", score: 87 },
    { date: "Sun", score: 92 },
  ];

  const handleStartExercise = (exerciseId) => {
    setSelectedExercise(exerciseId);
    setIsExercising(true);
  };

  const handleStopExercise = () => {
    setIsExercising(false);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card border-b border-border shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-medical flex items-center justify-center">
                <Activity className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">
                  PhysioTrack
                </h1>
                <p className="text-xs text-muted-foreground">
                  AI-Powered Physical Therapy
                </p>
              </div>
            </div>

            <nav className="hidden md:flex items-center gap-2">
              <Button
                variant={activeTab === "dashboard" ? "default" : "ghost"}
                className="gap-2"
                onClick={() => setActiveTab("dashboard")}
              >
                <Home className="w-4 h-4" />
                Dashboard
              </Button>
              <Button
                variant={activeTab === "exercises" ? "default" : "ghost"}
                className="gap-2"
                onClick={() => setActiveTab("exercises")}
              >
                <Activity className="w-4 h-4" />
                My Exercises
              </Button>
              <Button
                variant={activeTab === "progress" ? "default" : "ghost"}
                className="gap-2"
                onClick={() => setActiveTab("progress")}
              >
                <TrendingUp className="w-4 h-4" />
                Progress
              </Button>
              <Button
                variant={activeTab === "profile" ? "default" : "ghost"}
                className="gap-2"
                onClick={() => setActiveTab("profile")}
              >
                <User className="w-4 h-4" />
                Profile
              </Button>
            </nav>

            <div className="flex items-center gap-3">
              <Badge variant="outline" className="gap-1.5 px-3 py-1.5">
                <Calendar className="w-3.5 h-3.5" />
                Today:{" "}
                {new Date().toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })}
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === "dashboard" && !selectedExercise && (
          <div className="space-y-6 animate-fade-in">
            {/* Welcome Section */}
            <div className="bg-gradient-medical rounded-2xl p-8 text-primary-foreground shadow-medical">
              <div className="max-w-2xl">
                <h2 className="text-3xl font-bold mb-2">
                  Welcome back, Sarah!
                </h2>
                <p className="text-primary-foreground/90 mb-6">
                  You have 2 exercises remaining today. Keep up the great work!
                </p>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    <div>
                      <p className="text-sm opacity-90">Weekly Goal</p>
                      <p className="text-lg font-semibold">5/7 Days</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5" />
                    <div>
                      <p className="text-sm opacity-90">Current Streak</p>
                      <p className="text-lg font-semibold">12 Days</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Today's Exercises */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-foreground">
                  Today's Exercises
                </h3>
                <Badge className="bg-primary text-primary-foreground">
                  {todayExercises.filter((e) => !e.completed).length} Remaining
                </Badge>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {todayExercises.map((exercise) => (
                  <Card
                    key={exercise.id}
                    className={`bg-gradient-card border-2 transition-all hover:shadow-md ${
                      exercise.completed ? "border-success/30" : "border-border"
                    }`}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg font-semibold text-foreground mb-1">
                            {exercise.name}
                          </CardTitle>
                          <CardDescription className="flex items-center gap-2">
                            <Clock className="w-3.5 h-3.5" />
                            {exercise.duration}
                          </CardDescription>
                        </div>
                        {exercise.completed && (
                          <CheckCircle className="w-5 h-5 text-success" />
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">
                          Sets × Reps
                        </span>
                        <span className="font-medium text-foreground">
                          {exercise.sets} × {exercise.reps}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">
                          Difficulty
                        </span>
                        <Badge
                          variant="outline"
                          className={
                            exercise.difficulty === "Easy"
                              ? "border-success text-success"
                              : exercise.difficulty === "Medium"
                              ? "border-warning text-warning"
                              : "border-destructive text-destructive"
                          }
                        >
                          {exercise.difficulty}
                        </Badge>
                      </div>
                      {exercise.lastScore && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">
                            Last Score
                          </span>
                          <span
                            className={`font-semibold ${
                              exercise.lastScore >= 90
                                ? "text-success"
                                : exercise.lastScore >= 75
                                ? "text-warning"
                                : "text-destructive"
                            }`}
                          >
                            {exercise.lastScore}%
                          </span>
                        </div>
                      )}

                      <Button
                        className="w-full gap-2 mt-2"
                        variant={exercise.completed ? "outline" : "default"}
                        onClick={() => handleStartExercise(exercise.id)}
                      >
                        {exercise.completed ? (
                          <>
                            <RotateCcw className="w-4 h-4" />
                            Practice Again
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4" />
                            Start Exercise
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid md:grid-cols-3 gap-4">
              <Card className="bg-card">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Average Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-success">87%</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    +5% from last week
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-card">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total Sessions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-primary">42</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    This month
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-card">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Completion Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-foreground">94%</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Last 30 days
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Exercise Session View */}
        {selectedExercise && (
          <div className="space-y-6 animate-fade-in">
            {/* Exercise Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-1">
                  {todayExercises.find((e) => e.id === selectedExercise)?.name}
                </h2>
                <p className="text-muted-foreground">
                  Follow the on-screen guidance
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => setSelectedExercise(null)}
              >
                Back to Dashboard
              </Button>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
              {/* Camera View */}
              <div className="lg:col-span-2 space-y-4">
                <Card className="bg-card overflow-hidden">
                  <CardHeader className="bg-secondary/50 border-b">
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <Video className="w-5 h-5 text-primary" />
                        Live Camera View
                      </CardTitle>
                      <Badge variant="outline" className="gap-1.5">
                        <span className="w-2 h-2 bg-success rounded-full animate-pulse-soft"></span>
                        Active
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="relative aspect-video bg-muted flex items-center justify-center">
                      {/* Camera Placeholder */}
                      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-success/5 flex items-center justify-center">
                        <Video className="w-20 h-20 text-muted-foreground/30" />
                      </div>

                      {/* Posture Overlay Skeleton */}
                      <svg
                        className="absolute inset-0 w-full h-full"
                        viewBox="0 0 640 360"
                      >
                        {/* Head */}
                        <circle
                          cx="320"
                          cy="80"
                          r="25"
                          fill="none"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />

                        {/* Shoulders */}
                        <line
                          x1="280"
                          y1="130"
                          x2="360"
                          y2="130"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <circle
                          cx="280"
                          cy="130"
                          r="8"
                          fill="hsl(var(--success))"
                        />
                        <circle
                          cx="360"
                          cy="130"
                          r="8"
                          fill="hsl(var(--success))"
                        />

                        {/* Spine */}
                        <line
                          x1="320"
                          y1="105"
                          x2="320"
                          y2="130"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <line
                          x1="320"
                          y1="130"
                          x2="320"
                          y2="200"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />

                        {/* Arms */}
                        <line
                          x1="280"
                          y1="130"
                          x2="240"
                          y2="180"
                          stroke="hsl(var(--warning))"
                          strokeWidth="3"
                        />
                        <line
                          x1="240"
                          y1="180"
                          x2="230"
                          y2="220"
                          stroke="hsl(var(--warning))"
                          strokeWidth="3"
                        />
                        <circle
                          cx="240"
                          cy="180"
                          r="7"
                          fill="hsl(var(--warning))"
                        />
                        <circle
                          cx="230"
                          cy="220"
                          r="7"
                          fill="hsl(var(--warning))"
                        />

                        <line
                          x1="360"
                          y1="130"
                          x2="400"
                          y2="180"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <line
                          x1="400"
                          y1="180"
                          x2="410"
                          y2="220"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <circle
                          cx="400"
                          cy="180"
                          r="7"
                          fill="hsl(var(--success))"
                        />
                        <circle
                          cx="410"
                          cy="220"
                          r="7"
                          fill="hsl(var(--success))"
                        />

                        {/* Hips */}
                        <line
                          x1="295"
                          y1="200"
                          x2="345"
                          y2="200"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <circle
                          cx="295"
                          cy="200"
                          r="8"
                          fill="hsl(var(--success))"
                        />
                        <circle
                          cx="345"
                          cy="200"
                          r="8"
                          fill="hsl(var(--success))"
                        />

                        {/* Legs */}
                        <line
                          x1="295"
                          y1="200"
                          x2="285"
                          y2="260"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <line
                          x1="285"
                          y1="260"
                          x2="280"
                          y2="310"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <circle
                          cx="285"
                          cy="260"
                          r="7"
                          fill="hsl(var(--success))"
                        />
                        <circle
                          cx="280"
                          cy="310"
                          r="7"
                          fill="hsl(var(--success))"
                        />

                        <line
                          x1="345"
                          y1="200"
                          x2="355"
                          y2="260"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <line
                          x1="355"
                          y1="260"
                          x2="360"
                          y2="310"
                          stroke="hsl(var(--success))"
                          strokeWidth="3"
                        />
                        <circle
                          cx="355"
                          cy="260"
                          r="7"
                          fill="hsl(var(--success))"
                        />
                        <circle
                          cx="360"
                          cy="310"
                          r="7"
                          fill="hsl(var(--success))"
                        />
                      </svg>

                      {/* Control Overlay */}
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                        <Button
                          size="lg"
                          className="gap-2 shadow-lg"
                          onClick={() => setIsExercising(!isExercising)}
                        >
                          {isExercising ? (
                            <>
                              <Pause className="w-5 h-5" />
                              Pause
                            </>
                          ) : (
                            <>
                              <Play className="w-5 h-5" />
                              Start
                            </>
                          )}
                        </Button>
                        <Button
                          size="lg"
                          variant="outline"
                          className="gap-2 shadow-lg bg-card"
                        >
                          <RotateCcw className="w-5 h-5" />
                          Reset
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Exercise Instructions */}
                <Card className="bg-card">
                  <CardHeader>
                    <CardTitle className="text-lg">
                      Exercise Instructions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ol className="space-y-2 text-sm">
                      <li className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                          1
                        </span>
                        <span className="text-foreground">
                          Stand with feet shoulder-width apart
                        </span>
                      </li>
                      <li className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                          2
                        </span>
                        <span className="text-foreground">
                          Slowly raise your arms to shoulder height
                        </span>
                      </li>
                      <li className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                          3
                        </span>
                        <span className="text-foreground">
                          Hold for 2 seconds at the top
                        </span>
                      </li>
                      <li className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                          4
                        </span>
                        <span className="text-foreground">
                          Lower arms slowly back to starting position
                        </span>
                      </li>
                    </ol>
                  </CardContent>
                </Card>
              </div>

              {/* Feedback Panel */}
              <div className="space-y-4">
                {/* Current Score */}
                <Card className="bg-gradient-success text-success-foreground">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium opacity-90">
                      Current Score
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-5xl font-bold mb-2">89%</div>
                    <p className="text-sm opacity-90">Excellent form!</p>
                  </CardContent>
                </Card>

                {/* Posture Accuracy */}
                <Card className="bg-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Posture Accuracy
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2 text-sm">
                        <span className="text-foreground">
                          Shoulder Alignment
                        </span>
                        <span className="font-semibold text-success">95%</span>
                      </div>
                      <Progress value={95} className="h-2" />
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2 text-sm">
                        <span className="text-foreground">Arm Extension</span>
                        <span className="font-semibold text-warning">78%</span>
                      </div>
                      <Progress value={78} className="h-2" />
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2 text-sm">
                        <span className="text-foreground">Core Stability</span>
                        <span className="font-semibold text-success">92%</span>
                      </div>
                      <Progress value={92} className="h-2" />
                    </div>
                  </CardContent>
                </Card>

                {/* Real-time Tips */}
                <Card className="bg-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-warning" />
                      Coaching Tips
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="p-3 rounded-lg bg-warning-light border border-warning/30">
                      <p className="text-sm text-foreground font-medium mb-1">
                        Extend your left arm more
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Try to reach full extension for better results
                      </p>
                    </div>

                    <div className="p-3 rounded-lg bg-success-light border border-success/30">
                      <p className="text-sm text-foreground font-medium mb-1">
                        Great shoulder posture!
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Keep maintaining this alignment
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Progress */}
                <Card className="bg-card">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Session Progress
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2 text-sm">
                        <span className="text-foreground">Repetitions</span>
                        <span className="font-semibold text-foreground">
                          7 / 10
                        </span>
                      </div>
                      <Progress value={70} className="h-2" />
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2 text-sm">
                        <span className="text-foreground">Time Remaining</span>
                        <span className="font-semibold text-foreground">
                          1:45
                        </span>
                      </div>
                      <Progress value={42} className="h-2" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {/* Progress Tab */}
        {activeTab === "progress" && !selectedExercise && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-2">
                Your Progress
              </h2>
              <p className="text-muted-foreground">
                Track your improvement over time
              </p>
            </div>

            {/* Weekly Chart */}
            <Card className="bg-card">
              <CardHeader>
                <CardTitle>Weekly Performance</CardTitle>
                <CardDescription>
                  Average scores for the past 7 days
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-end justify-between gap-2">
                  {recentProgress.map((day, index) => (
                    <div
                      key={index}
                      className="flex-1 flex flex-col items-center gap-2"
                    >
                      <div
                        className="w-full bg-secondary rounded-t-lg relative overflow-hidden"
                        style={{ height: "200px" }}
                      >
                        <div
                          className="absolute bottom-0 w-full bg-gradient-success rounded-t-lg transition-all duration-500"
                          style={{ height: `${day.score}%` }}
                        ></div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs font-semibold text-foreground">
                          {day.score}%
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {day.date}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Sessions */}
            <Card className="bg-card">
              <CardHeader>
                <CardTitle>Recent Sessions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      exercise: "Shoulder Flexion",
                      date: "Today",
                      score: 92,
                      duration: "3 min",
                    },
                    {
                      exercise: "Knee Extension",
                      date: "Yesterday",
                      score: 88,
                      duration: "5 min",
                    },
                    {
                      exercise: "Hip Abduction",
                      date: "2 days ago",
                      score: 85,
                      duration: "4 min",
                    },
                  ].map((session, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 rounded-lg bg-secondary/50 border border-border hover:border-primary/30 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            session.score >= 90
                              ? "bg-success-light"
                              : "bg-warning-light"
                          }`}
                        >
                          <Activity
                            className={`w-5 h-5 ${
                              session.score >= 90
                                ? "text-success"
                                : "text-warning"
                            }`}
                          />
                        </div>
                        <div>
                          <p className="font-semibold text-foreground">
                            {session.exercise}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {session.date} · {session.duration}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p
                            className={`text-lg font-bold ${
                              session.score >= 90
                                ? "text-success"
                                : "text-warning"
                            }`}
                          >
                            {session.score}%
                          </p>
                          <p className="text-xs text-muted-foreground">Score</p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
