
import { useEffect, useState, type FormEvent } from "react";

type Job = {
  id: number;
  title: string;
  company: string;
  location: string;
  required_experience: number;
  required_skills: string[];
};

type JobsPageProps = {
  token: string;
};

const emptyForm = {
  title: "",
  company: "",
  location: "",
  required_experience: 0,
  skillsInput: "",
};

export default function JobsPage({ token }: JobsPageProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [form, setForm] = useState({ ...emptyForm });
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadJobs() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch("/jobs", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(
            `Could not load jobs (${response.status}).`
          );
        }

        const data: unknown = await response.json();

        // Initial implementation expects GET /jobs
        // to return an array of jobs.
        if (!Array.isArray(data)) {
          throw new Error(
            "Unexpected jobs response format."
          );
        }

        if (!controller.signal.aborted) {
          setJobs(data as Job[]);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(
            err instanceof Error
              ? err.message
              : "Could not load jobs."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadJobs();

    return () => controller.abort();
  }, [token]);

  async function handleCreateJob(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    const payload = {
      title: form.title.trim(),
      company: form.company.trim(),
      location: form.location.trim(),
      required_experience: Number(
        form.required_experience
      ),
      required_skills: [
        ...new Set(
          form.skillsInput
            .split(",")
            .map((skill) => skill.trim())
            .filter(Boolean)
        ),
      ],
    };

    try {
      const response = await fetch("/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const detail = await response.text();

        throw new Error(
          `Could not create job (${response.status}): ${detail}`
        );
      }

      const createdJob = (await response.json()) as Job;

      setJobs((previous) => [createdJob, ...previous]);
      setForm({ ...emptyForm });
      setShowForm(false);
      setMessage("Job created successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not create job."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="jobs-page">
      <div className="jobs-header">
        <div>
          <h2>Job Management</h2>
          <p>
            Create openings and manage hiring requirements.
          </p>
        </div>

        <button
          className="primary-action"
          onClick={() => setShowForm((value) => !value)}
        >
          {showForm ? "Cancel" : "+ Create Job"}
        </button>
      </div>

      {error && (
        <div className="jobs-error" role="alert">
          {error}
        </div>
      )}

      {message && (
        <div className="jobs-success" role="status">
          {message}
        </div>
      )}

      {showForm && (
        <form
          className="job-form"
          onSubmit={handleCreateJob}
        >
          <h3>Create a job opening</h3>

          <div className="job-field-grid">
            <label>
              Job title
              <input
                required
                value={form.title}
                onChange={(e) =>
                  setForm({
                    ...form,
                    title: e.target.value,
                  })
                }
                placeholder="Python Backend Developer"
              />
            </label>

            <label>
              Company
              <input
                required
                value={form.company}
                onChange={(e) =>
                  setForm({
                    ...form,
                    company: e.target.value,
                  })
                }
                placeholder="Tech Solutions"
              />
            </label>

            <label>
              Location
              <input
                required
                value={form.location}
                onChange={(e) =>
                  setForm({
                    ...form,
                    location: e.target.value,
                  })
                }
                placeholder="Lahore"
              />
            </label>

            <label>
              Required experience (years)
              <input
                type="number"
                required
                min="0"
                step="1"
                value={form.required_experience}
                onChange={(e) =>
                  setForm({
                    ...form,
                    required_experience: Number(
                      e.target.value
                    ),
                  })
                }
              />
            </label>
          </div>

          <label>
            Required skills
            <input
              value={form.skillsInput}
              onChange={(e) =>
                setForm({
                  ...form,
                  skillsInput: e.target.value,
                })
              }
              placeholder="Python, FastAPI, PostgreSQL"
            />
            <small>Separate skills using commas.</small>
          </label>

          <button
            className="primary-action"
            type="submit"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Job"}
          </button>
        </form>
      )}

      <div className="jobs-summary">
        <span>Job openings</span>
        <strong>{jobs.length}</strong>
      </div>

      {loading ? (
        <p>Loading jobs...</p>
      ) : jobs.length === 0 ? (
        <div className="empty-jobs">
          No jobs found. Create your first job opening.
        </div>
      ) : (
        <div className="job-cards">
          {jobs.map((job) => (
            <article className="job-card" key={job.id}>
              <div className="job-card-top">
                <span className="job-id">
                  JOB #{job.id}
                </span>
              </div>

              <h3>{job.title}</h3>
              <p>{job.company}</p>

              <div className="job-meta">
                <span>📍 {job.location}</span>
                <span>
                  {job.required_experience} years
                  experience
                </span>
              </div>

              <div className="skill-list">
                {(job.required_skills ?? []).map(
                  (skill) => (
                    <span
                      className="skill-chip"
                      key={skill}
                    >
                      {skill}
                    </span>
                  )
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
