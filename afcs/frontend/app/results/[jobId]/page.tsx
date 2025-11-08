"use client";

import { useQuery } from "@tanstack/react-query";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";

import { ChartCard } from "../../../components/ChartCard";
import { fetchResult } from "../../../lib/api";

export default function ResultsPage() {
  const params = useParams<{ jobId: string }>();
  const query = useQuery({
    queryKey: ["result", params.jobId],
    queryFn: () => fetchResult(params.jobId)
  });

  if (query.isLoading) {
    return <p>Loading results…</p>;
  }

  if (query.isError || !query.data) {
    return (
      <div className="space-y-4">
        <p className="text-red-400">We couldn’t load this result.</p>
        <Link href="/upload" className="focus-ring inline-flex items-center gap-2 rounded-full border border-[var(--border)] px-4 py-2 text-sm">
          Start over
        </Link>
      </div>
    );
  }

  const result = query.data;

  return (
    <div className="space-y-10">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Compression results</h1>
        <p className="text-sm opacity-75">
          Method: <span className="font-semibold uppercase">{result.method}</span> · Latent shape {result.latent_shape.join(" × ")} · Reconstruction error {result.recon_error.toFixed(4)}
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="Feature importance" description="AFCS scoring with redundancy penalty.">
          <ul className="space-y-2 text-sm">
            {result.feature_importance.slice(0, 8).map((item) => (
              <li key={item.name} className="flex justify-between">
                <span>{item.name}</span>
                <span>{item.score.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </ChartCard>
        <ChartCard title="Artifacts" description="Download compressed data and pipeline assets.">
          <ul className="space-y-2 text-sm">
            {result.artifacts.map((artifact) => (
              <li key={artifact.name}>
                <a className="text-[var(--accent)]" href={`http://localhost:8000${artifact.url}`}>{artifact.name}</a>
              </li>
            ))}
          </ul>
        </ChartCard>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {result.plots.map((plot) => (
          <div key={plot.name} className="glassy overflow-hidden">
            <Image
              src={`http://localhost:8000${plot.url}`}
              alt={plot.name}
              width={800}
              height={400}
              className="h-64 w-full object-cover"
            />
            <div className="p-4 text-sm capitalize opacity-80">{plot.name.replace(/_/g, " ")}</div>
          </div>
        ))}
      </section>

      <section className="glassy space-y-4 p-6">
        <h2 className="text-xl font-semibold">Reproduce locally</h2>
        <pre className="overflow-x-auto rounded-lg bg-black/40 p-4 font-mono text-xs">
          {`pip install -r backend/requirements.txt
python -m afcs_core.samples
# Launch backend
uvicorn backend.main:app --reload
# Download artifacts from http://localhost:8000/download/${result.result_id}/compressed.csv`}
        </pre>
      </section>
    </div>
  );
}
