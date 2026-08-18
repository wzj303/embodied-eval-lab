import type { EvaluationRun } from "./types";

const API_BASE_URL = "http://127.0.0.1:8000";

async function requestJson<T>(path: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`);
  } catch {
    throw new Error(
      "Unable to connect to the evaluation API. Is FastAPI running?",
    );
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const body = (await response.json()) as {
        detail?: unknown;
      };

      if (typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // Keep the status-based message when no JSON error body exists.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function getEvaluationRuns(): Promise<EvaluationRun[]> {
  return requestJson<EvaluationRun[]>("/evaluation-runs");
}

export function getEvaluationRun(
  runId: number,
): Promise<EvaluationRun> {
  return requestJson<EvaluationRun>(
    `/evaluation-runs/${runId}`,
  );
}