export interface EvaluationRun {
  id: number;
  run_name: string;
  dataset_path: string;
  created_at: string;
  episode_count: number;
  total_step_count: number;
  success_count: number;
  success_rate: number;
  average_steps_per_episode: number;
  average_episode_duration_s: number;
  mean_inference_latency_ms: number;
  p95_inference_latency_ms: number;
}