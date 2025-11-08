"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ChartCard } from "../../../components/ChartCard";
import { ProgressDialog } from "../../../components/ProgressDialog";
import { analyzeDataset, pollJob, startCompression } from "../../../lib/api";

const tabs = ["Overview", "Compression", "Explain"] as const;

type Tab = (typeof tabs)[number];

export default function AnalysisPage() {
  const params = useParams<{ datasetId: string }>();
  const search = useSearchParams();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>("Overview");
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState({ value: 0, message: "Preparing" });

  const analysisQuery = useQuery({
    queryKey: ["analysis", params.datasetId, search.toString()],
    queryFn: () =>
      analyzeDataset({
        dataset_id: params.datasetId,
        missing_policy: search.get("missing") ?? "median",
        encode_categorical: search.get("encode") !== "0",
        standardize: search.get("standardize") !== "0"
      })
  });

  const compressionMutation = useMutation({
    mutationFn: (payload: Parameters<typeof startCompression>[0]) => startCompression(payload),
    onSuccess: (data) => {
      setJobId(data.job_id);
    }
  });

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;
    const interval = setInterval(async () => {
      const status = await pollJob(jobId);
      if (!cancelled) {
        setProgress({ value: status.progress, message: status.message ?? "Processing" });
        if (status.status === "done" && status.result_id) {
          clearInterval(interval);
          router.push(`/results/${status.result_id}`);
        }
        if (status.status === "error") {
          clearInterval(interval);
          setJobId(null);
        }
      }
    }, 1200);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [jobId, router]);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "/") {
        event.preventDefault();
        const element = document.getElementById("global-search") as HTMLInputElement | null;
        element?.focus();
      }
      if (event.key.toLowerCase() === "g") {
        const listener = (e: KeyboardEvent) => {
          if (e.key.toLowerCase() === "r") {
            router.push("/results");
          }
          window.removeEventListener("keydown", listener);
        };
        window.addEventListener("keydown", listener, { once: true });
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [router]);

  const stats = analysisQuery.data?.stats;

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analysis</h1>
          <p className="text-sm opacity-75">
            Tweak preprocessing, inspect feature dynamics, and choose your compression strategy.
          </p>
        </div>
        <input
          id="global-search"
          placeholder="Search features (/ to focus)"
          className="focus-ring w-full rounded-full border border-[var(--border)] bg-transparent px-4 py-2 text-sm sm:w-72"
        />
      </header>

      <nav className="flex gap-3">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`focus-ring rounded-full px-4 py-2 text-sm transition ${activeTab === tab ? "bg-[var(--accent)] text-black" : "border border-[var(--border)]"}`}
          >
            {tab}
          </button>
        ))}
      </nav>

      {analysisQuery.isLoading ? (
        <p>Loading analysis…</p>
      ) : analysisQuery.isError ? (
        <p className="text-red-400">Failed to analyze dataset.</p>
      ) : (
        <section className="space-y-6">
          {activeTab === "Overview" && stats ? (
            <div className="grid gap-6 lg:grid-cols-2">
              <ChartCard
                title="Dataset snapshot"
                description="Rows, columns, and missingness overview."
              >
                <ul className="space-y-2 text-sm">
                  <li>Shape: {stats.shape?.[0]?.toLocaleString()} rows × {stats.shape?.[1]} columns</li>
                  <li>Missing cells: {Object.values(stats.missing ?? {}).reduce((sum: number, value: number) => sum + value, 0)}</li>
                </ul>
              </ChartCard>
              <ChartCard title="Type inference" description="Count of numeric vs categorical columns.">
                <ul className="space-y-2 text-sm max-h-72 overflow-auto">
                  {Object.entries(analysisQuery.data?.inferred_types ?? {}).map(([name, type]) => (
                    <li key={name} className="flex justify-between">
                      <span>{name}</span>
                      <span className="uppercase text-[var(--accent)]">{type}</span>
                    </li>
                  ))}
                </ul>
              </ChartCard>
            </div>
          ) : null}

          {activeTab === "Compression" && (
            <div className="grid gap-6 lg:grid-cols-2">
              <ChartCard title="Choose method" description="Select PCA or Autoencoder and tune hyperparameters.">
                <form
                  className="space-y-4"
                  onSubmit={(event) => {
                    event.preventDefault();
                    const formData = new FormData(event.currentTarget as HTMLFormElement);
                    const method = formData.get("method") as "pca" | "autoencoder";
                    const variance = Number(formData.get("pca_variance")) || 0.95;
                    const latent = Number(formData.get("ae_latent_dim")) || 4;
                    const epochs = Number(formData.get("epochs")) || 30;
                    const batch = Number(formData.get("batch_size")) || 32;
                    const lr = Number(formData.get("learning_rate")) || 0.001;
                    compressionMutation.mutate({
                      dataset_id: params.datasetId,
                      method,
                      pca_variance: variance,
                      ae_latent_dim: latent,
                      epochs,
                      batch_size: batch,
                      learning_rate: lr,
                      clustering: "kmeans",
                      random_state: 42
                    });
                  }}
                >
                  <label className="flex items-center gap-2 text-sm">
                    <input type="radio" name="method" value="pca" defaultChecked /> PCA (retain variance)
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="radio" name="method" value="autoencoder" /> Autoencoder (learned latent)
                  </label>
                  <label className="flex flex-col gap-2 text-sm">
                    PCA variance threshold
                    <input type="number" name="pca_variance" step="0.01" min="0.8" max="0.99" defaultValue={0.95} className="rounded border border-[var(--border)] bg-transparent px-3 py-2" />
                  </label>
                  <label className="flex flex-col gap-2 text-sm">
                    AE latent dimension
                    <input type="number" name="ae_latent_dim" min="2" max="16" defaultValue={4} className="rounded border border-[var(--border)] bg-transparent px-3 py-2" />
                  </label>
                  <label className="flex flex-col gap-2 text-sm">
                    Epochs
                    <input type="number" name="epochs" min="5" max="200" defaultValue={30} className="rounded border border-[var(--border)] bg-transparent px-3 py-2" />
                  </label>
                  <label className="flex flex-col gap-2 text-sm">
                    Batch size
                    <input type="number" name="batch_size" min="4" max="256" defaultValue={32} className="rounded border border-[var(--border)] bg-transparent px-3 py-2" />
                  </label>
                  <label className="flex flex-col gap-2 text-sm">
                    Learning rate
                    <input type="number" name="learning_rate" step="0.0001" defaultValue={0.001} className="rounded border border-[var(--border)] bg-transparent px-3 py-2" />
                  </label>
                  <button
                    type="submit"
                    className="focus-ring inline-flex w-full items-center justify-center rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--primary)] px-6 py-3 text-sm font-semibold"
                  >
                    Run compression
                  </button>
                </form>
              </ChartCard>
              <ChartCard title="What to expect" description="AFCS estimates training duration and reconstruction quality.">
                <p className="text-sm opacity-75">
                  PCA runs in seconds. Autoencoder training may take longer but can capture nonlinear structure. Reconstruction error and variance metrics will appear in the results view once training completes.
                </p>
              </ChartCard>
            </div>
          )}

          {activeTab === "Explain" && (
            <ChartCard title="Explainability" description="Generated summary based on preprocessing settings.">
              <p className="text-sm opacity-80">
                AFCS analyzed {stats?.shape?.[0]?.toLocaleString()} rows × {stats?.shape?.[1]} columns. After preprocessing, feature importance ranks and correlation hotspots will be summarised in the results view.
              </p>
            </ChartCard>
          )}
        </section>
      )}

      <ProgressDialog open={jobId !== null} progress={progress.value} message={progress.message} />
    </div>
  );
}
