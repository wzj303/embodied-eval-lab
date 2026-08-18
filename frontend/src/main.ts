import "./style.css";

import {
  getEvaluationRun,
  getEvaluationRuns,
} from "./api";
import type { EvaluationRun } from "./types";

const appElement = document.querySelector<HTMLDivElement>("#app");

if (appElement === null) {
  throw new Error("Dashboard root element was not found");
}

const app = appElement;

function escapeHtml(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[character] ?? character,
  );
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value: number): string {
  return `${formatNumber(value * 100)}%`;
}

function formatTimestamp(value: string): string {
  const timestamp = new Date(
    `${value.replace(" ", "T")}Z`,
  );

  return timestamp.toLocaleString();
}

function renderLoading(): void {
  app.innerHTML = `
    <main class="dashboard">
      <section class="state" aria-live="polite">
        <p>Loading evaluation runs...</p>
      </section>
    </main>
  `;
}

function renderEmpty(): void {
  app.innerHTML = `
    <main class="dashboard">
      <header class="page-header">
        <div>
          <p class="eyebrow">Embodied Eval Lab</p>
          <h1>Evaluation dashboard</h1>
        </div>
        <button id="refresh-button" type="button">Refresh</button>
      </header>
      <section class="state">
        <h2>No evaluation runs</h2>
        <p>Create and save an evaluation run to populate this dashboard.</p>
      </section>
    </main>
  `;

  bindRefreshButton();
}

function renderError(error: unknown): void {
  const message = error instanceof Error
    ? error.message
    : "An unexpected error occurred.";

  app.innerHTML = `
    <main class="dashboard">
      <section class="state state-error" role="alert">
        <h1>Unable to load dashboard</h1>
        <p>${escapeHtml(message)}</p>
        <button id="retry-button" type="button">Retry</button>
      </section>
    </main>
  `;

  const retryButton = document.querySelector<HTMLButtonElement>(
    "#retry-button",
  );

  retryButton?.addEventListener("click", () => {
    void loadDashboard();
  });
}

function renderDashboard(
  runs: EvaluationRun[],
  selectedRun: EvaluationRun,
): void {
  const tableRows = runs.map((run) => {
    const isSelected = run.id === selectedRun.id;

    return `
      <tr class="${isSelected ? "selected-row" : ""}">
        <td>${run.id}</td>
        <td>${escapeHtml(run.run_name)}</td>
        <td>${formatPercent(run.success_rate)}</td>
        <td>${formatNumber(run.mean_inference_latency_ms)} ms</td>
        <td>${formatTimestamp(run.created_at)}</td>
        <td>
          <button
            class="table-action"
            data-run-id="${run.id}"
            type="button"
          >
            View
          </button>
        </td>
      </tr>
    `;
  }).join("");

  app.innerHTML = `
    <main class="dashboard">
      <header class="page-header">
        <div>
          <p class="eyebrow">Embodied Eval Lab</p>
          <h1>Evaluation dashboard</h1>
        </div>
        <button id="refresh-button" type="button">Refresh</button>
      </header>

      <section class="metric-grid" aria-label="Selected evaluation metrics">
        <article class="metric">
          <p>Success rate</p>
          <strong>${formatPercent(selectedRun.success_rate)}</strong>
        </article>
        <article class="metric">
          <p>Average duration</p>
          <strong>
            ${formatNumber(selectedRun.average_episode_duration_s)} s
          </strong>
        </article>
        <article class="metric">
          <p>Mean latency</p>
          <strong>
            ${formatNumber(selectedRun.mean_inference_latency_ms)} ms
          </strong>
        </article>
        <article class="metric">
          <p>P95 latency</p>
          <strong>
            ${formatNumber(selectedRun.p95_inference_latency_ms)} ms
          </strong>
        </article>
      </section>

      <section class="content-grid">
        <section class="panel">
          <div class="panel-heading">
            <h2>Evaluation runs</h2>
            <span>${runs.length} total</span>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Run name</th>
                  <th>Success rate</th>
                  <th>Mean latency</th>
                  <th>Created at</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>${tableRows}</tbody>
            </table>
          </div>
        </section>

        <aside class="panel details-panel">
          <div class="panel-heading">
            <h2>Run ${selectedRun.id}</h2>
          </div>
          <dl class="details-list">
            <div>
              <dt>Run name</dt>
              <dd>${escapeHtml(selectedRun.run_name)}</dd>
            </div>
            <div>
              <dt>Dataset</dt>
              <dd>${escapeHtml(selectedRun.dataset_path)}</dd>
            </div>
            <div>
              <dt>Episodes</dt>
              <dd>${selectedRun.episode_count}</dd>
            </div>
            <div>
              <dt>Total steps</dt>
              <dd>${selectedRun.total_step_count}</dd>
            </div>
            <div>
              <dt>Successful episodes</dt>
              <dd>${selectedRun.success_count}</dd>
            </div>
            <div>
              <dt>Average steps</dt>
              <dd>
                ${formatNumber(selectedRun.average_steps_per_episode)}
              </dd>
            </div>
          </dl>
        </aside>
      </section>
    </main>
  `;

  bindRefreshButton();
  bindRunButtons();
}

function bindRefreshButton(): void {
  const refreshButton = document.querySelector<HTMLButtonElement>(
    "#refresh-button",
  );

  refreshButton?.addEventListener("click", () => {
    void loadDashboard();
  });
}

function bindRunButtons(): void {
  const buttons = document.querySelectorAll<HTMLButtonElement>(
    "[data-run-id]",
  );

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const runId = Number(button.dataset.runId);

      if (Number.isInteger(runId)) {
        void loadDashboard(runId);
      }
    });
  });
}

async function loadDashboard(
  selectedRunId?: number,
): Promise<void> {
  renderLoading();

  try {
    const runs = await getEvaluationRuns();

    if (runs.length === 0) {
      renderEmpty();
      return;
    }

    const selectedRun = selectedRunId === undefined
      ? runs[0]
      : await getEvaluationRun(selectedRunId);

    renderDashboard(runs, selectedRun);
  } catch (error) {
    renderError(error);
  }
}

void loadDashboard();
