import { z } from "zod";

export const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const DatasetInfo = z.object({
  id: z.string(),
  name: z.string(),
  rows: z.number(),
  cols: z.number(),
  numeric_cols: z.number(),
  categorical_cols: z.number(),
  missing_pct: z.number()
});

export type DatasetInfo = z.infer<typeof DatasetInfo>;

const AnalyzeResponseSchema = z.object({
  stats: z.any(),
  inferred_types: z.record(z.enum(["numeric", "categorical"])),
  missingness: z.record(z.number()),
  preview_rows: z.number()
});

export type AnalyzeResponse = z.infer<typeof AnalyzeResponseSchema>;

const JobStatusSchema = z.object({
  job_id: z.string(),
  status: z.enum(["queued", "running", "done", "error"]),
  progress: z.number(),
  message: z.string().nullable().optional(),
  result_id: z.string().nullable().optional()
});

export type JobStatus = z.infer<typeof JobStatusSchema>;

const ResultInfoSchema = z.object({
  result_id: z.string(),
  method: z.string(),
  latent_shape: z.array(z.number()),
  recon_error: z.number(),
  explained_variance: z.array(z.number()).nullable(),
  feature_importance: z.array(z.object({ name: z.string(), score: z.number() })),
  plots: z.array(z.object({ name: z.string(), url: z.string() })),
  artifacts: z.array(z.object({ name: z.string(), url: z.string() })),
  cluster_labels: z.array(z.number()).nullable()
});

export type ResultInfo = z.infer<typeof ResultInfoSchema>;

async function request<T>(path: string, init?: RequestInit, schema?: z.ZodType<T>): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!(init?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }
  if (!schema) {
    return (undefined as unknown) as T;
  }
  const data = await response.json();
  return schema.parse(data);
}

export async function uploadFile(file: File | undefined, demo = false): Promise<DatasetInfo> {
  if (demo) {
    const response = await fetch(`${baseUrl}/upload?demo=true`, { method: "POST" });
    if (!response.ok) {
      throw new Error("Unable to load demo dataset");
    }
    const json = await response.json();
    return DatasetInfo.parse(json.dataset);
  }
  if (!file) {
    throw new Error("A CSV file is required for upload");
  }
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${baseUrl}/upload`, {
    method: "POST",
    body: form
  });
  if (!response.ok) {
    throw new Error("We couldn’t parse that file. Try a CSV under 50MB with a header row.");
  }
  const json = await response.json();
  return DatasetInfo.parse(json.dataset);
}

export async function analyzeDataset(payload: { dataset_id: string; missing_policy: string; encode_categorical: boolean; standardize: boolean; }): Promise<AnalyzeResponse> {
  return request("/analyze", { method: "POST", body: JSON.stringify(payload) }, AnalyzeResponseSchema);
}

export async function startCompression(payload: {
  dataset_id: string;
  method: "pca" | "autoencoder";
  pca_variance: number;
  ae_latent_dim: number;
  epochs: number;
  batch_size: number;
  learning_rate: number;
  clustering: "kmeans" | "none";
  random_state: number;
}): Promise<{ job_id: string; status: string }> {
  return request("/compress", { method: "POST", body: JSON.stringify(payload) }, z.object({ job_id: z.string(), status: z.string() }));
}

export async function pollJob(jobId: string): Promise<JobStatus> {
  return request(`/jobs/${jobId}`, { method: "GET" }, JobStatusSchema);
}

export async function fetchResult(resultId: string): Promise<ResultInfo> {
  return request(`/results/${resultId}`, { method: "GET" }, ResultInfoSchema);
}
