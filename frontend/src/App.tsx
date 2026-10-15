
import { useState, type FormEvent } from "react";
import "./App.css";
import JobsPage from "./pages/JobsPage";

// ---------------------------------------
// TYPES
// ---------------------------------------

type Role = "admin" | "hr" | "candidate";

type User = {
  id: number;
  email: string;
  role: Role;
};

type LoginResponse = {
  access_token: string;
  token_type: string;
};

type Page = "dashboard" | "jobs";

// ---------------------------------------
// FEATURES BY ROLE
// ---------------------------------------

const roleFeatures: Record<Role, string[]> = {
  admin: [
    "Manage HR accounts",
    "Assign roles and permissions",
    "Review recruitment activity",
    "Manage system settings",
  ],

  hr: [
    "Review candidates",
    "Upload and analyze resumes",
    "Review candidate-to-job matches",
    "Manage interviews",
  ],

  candidate: [
    "Browse job opportunities",
    "Manage personal profile",
    "Upload a resume",
    "Track applications",
  ],
};

// ---------------------------------------
// MAIN APP
// ---------------------------------------

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [activePage, setActivePage] =
    useState<Page>("dashboard");

  // ---------------------------------------
  // LOGIN
  // ---------------------------------------

  async function handleLogin(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();

      formData.append("username", email.trim());
      formData.append("password", password);

      const loginResponse = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      if (!loginResponse.ok) {
        if (
          loginResponse.status === 400 ||
          loginResponse.status === 401
        ) {
          throw new Error("Invalid email or password.");
        }

        throw new Error(
          `Login failed (${loginResponse.status}).`
        );
      }

      const loginData =
        (await loginResponse.json()) as LoginResponse;

      if (!loginData.access_token) {
        throw new Error(
          "Authentication token was not returned."
        );
      }

      const userResponse = await fetch("/auth/me", {
        headers: {
          Authorization:
            `Bearer ${loginData.access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error(
          "Could not verify your account."
        );
      }

      const currentUser =
        (await userResponse.json()) as User;

      const validRoles: Role[] = [
        "admin",
        "hr",
        "candidate",
      ];

      if (!validRoles.includes(currentUser.role)) {
        throw new Error(
          "Your account has an unsupported role."
        );
      }

      setUser(currentUser);
      setToken(loginData.access_token);
      setActivePage("dashboard");
      setPassword("");
    } catch (err) {
      setUser(null);
      setToken(null);

      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------
  // LOGOUT
  // ---------------------------------------

  function handleLogout() {
    setUser(null);
    setToken(null);
    setEmail("");
    setPassword("");
    setError("");
    setActivePage("dashboard");
  }

  // ---------------------------------------
  // AUTHENTICATED DASHBOARD
  // ---------------------------------------

  if (user && token) {
    const canManageJobs =
      user.role === "admin" ||
      user.role === "hr";

    const showJobsPage =
      activePage === "jobs" && canManageJobs;

    const dashboardTitle =
      user.role === "admin"
        ? "Admin Dashboard"
        : user.role === "hr"
          ? "HR Dashboard"
          : "Candidate Dashboard";

    const pageTitle = showJobsPage
      ? "Job Management"
      : dashboardTitle;

    return (
      <div className="dashboard-layout">

        {/* SIDEBAR */}
        <aside className="sidebar">

          <div className="brand">
            <span className="brand-icon">
              HR
            </span>
            <span>RecruitFlow</span>
          </div>

          <div className="sidebar-section">
            WORKSPACE
          </div>

          <nav className="navigation">

            {/* DASHBOARD BUTTON */}
            <button
              type="button"
              className={`nav-link ${
                activePage === "dashboard"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActivePage("dashboard")
              }
            >
              Dashboard
            </button>

            {/* ADMIN / HR JOB MANAGEMENT */}
            {canManageJobs && (
              <button
                type="button"
                className={`nav-link ${
                  showJobsPage ? "active" : ""
                }`}
                onClick={() =>
                  setActivePage("jobs")
                }
              >
                Manage Jobs
              </button>
            )}

            {/* UNFINISHED FEATURES */}
            <div className="sidebar-section">
              COMING SOON
            </div>

            {roleFeatures[user.role].map(
              (feature) => (
                <div
                  className="nav-link nav-link-disabled"
                  key={feature}
                  title="This feature is under development"
                  aria-disabled="true"
                >
                  <span>{feature}</span>

                  <span className="coming-soon-label">
                    Soon
                  </span>
                </div>
              )
            )}

          </nav>

          <div className="sidebar-footer">
            <span className="online-dot" />
            RecruitFlow Workspace
          </div>

        </aside>

        {/* MAIN CONTENT */}
        <main className="main-content">

          <header className="topbar">

            <div>
              <span className="eyebrow">
                Recruitment platform
              </span>

              <h1>{pageTitle}</h1>
            </div>

            <button
              type="button"
              className="logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>

          </header>

          {/* PAGE NAVIGATION */}
          {showJobsPage ? (
            <JobsPage token={token} />
          ) : (
            <>
              <section className="welcome-card">

                <div className="welcome-tag">
                  Authenticated session
                </div>

                <h2>
                  Welcome to RecruitFlow
                </h2>

                <p>
                  Signed in as{" "}
                  <strong>{user.email}</strong>
                </p>

                <span className="role-pill">
                  Role: {user.role.toUpperCase()}
                </span>

              </section>

              <section className="workspace-section">

                <h2>Your workspace</h2>

                <p className="section-description">
                  Manage your recruitment activities
                  from one place. Additional features
                  will be connected in upcoming lessons.
                </p>

                {/* FUNCTIONAL MODULES */}
                {canManageJobs && (
                  <div className="feature-grid">

                    <article className="feature-card">
                      <div className="feature-number">
                        AVAILABLE
                      </div>

                      <h3>Job Management</h3>

                      <p>
                        Create jobs, view openings,
                        and manage required skills.
                      </p>

                      <button
                        type="button"
                        className="primary-action"
                        onClick={() =>
                          setActivePage("jobs")
                        }
                      >
                        Open Job Management
                      </button>
                    </article>

                  </div>
                )}

                {/* FUTURE MODULES */}
                <h2 style={{ marginTop: 32 }}>
                  Upcoming Features
                </h2>

                <div className="feature-grid">

                  {roleFeatures[user.role].map(
                    (feature, index) => (
                      <article
                        className="feature-card"
                        key={feature}
                      >

                        <div className="feature-number">
                          {String(index + 1).padStart(
                            2,
                            "0"
                          )}
                        </div>

                        <h3>{feature}</h3>

                        <p>
                          Coming in the next
                          development phase
                        </p>

                        <span className="feature-soon">
                          Under development
                        </span>

                      </article>
                    )
                  )}

                </div>

              </section>
            </>
          )}

        </main>
      </div>
    );
  }

  // ---------------------------------------
  // LOGIN PAGE
  // ---------------------------------------

  return (
    <div className="login-page">

      <div className="login-panel">

        <div className="brand dark-brand">
          <span className="brand-icon">
            HR
          </span>
          <span>RecruitFlow</span>
        </div>

        <div className="login-heading">

          <span className="eyebrow">
            AI-ASSISTED RECRUITMENT
          </span>

          <h1>Welcome back</h1>

          <p>
            Sign in to manage your
            recruitment workspace.
          </p>

        </div>

        <form onSubmit={handleLogin}>

          <label htmlFor="email">
            Email address
          </label>

          <input
            id="email"
            type="email"
            value={email}
            placeholder="you@company.com"
            onChange={(event) =>
              setEmail(event.target.value)
            }
            autoComplete="username"
            required
          />

          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            value={password}
            placeholder="Enter your password"
            onChange={(event) =>
              setPassword(event.target.value)
            }
            autoComplete="current-password"
            required
          />

          {error && (
            <div
              className="error-message"
              role="alert"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>

        </form>

        <p className="login-note">
          Access is determined by your
          registered account role.
        </p>

      </div>

      {/* RIGHT VISUAL PANEL */}
      <div className="login-visual">

        <span className="visual-label">
          SMARTER RECRUITMENT
        </span>

        <h2>
          Hire with better information.
        </h2>

        <p>
          Manage job openings, organize resumes,
          and review candidate qualifications
          in one workspace.
        </p>

        <div className="visual-card">

          <div className="visual-card-icon">
            ✓
          </div>

          <div>
            <strong>Human-led hiring</strong>

            <span>
              AI-assisted analysis with
              recruiter oversight
            </span>
          </div>

        </div>

      </div>
    </div>
  );
}

export default App;
