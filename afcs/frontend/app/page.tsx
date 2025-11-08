import Link from "next/link";
import { ArrowRight, BarChart, Brain, Download } from "lucide-react";
import { motion } from "framer-motion";

export default function HomePage() {
  return (
    <div className="space-y-16">
      <section className="glassy overflow-hidden p-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="space-y-6">
          <span className="inline-flex items-center rounded-full bg-[var(--accent)]/20 px-3 py-1 text-xs uppercase tracking-[0.3em] text-[var(--accent)]">
            Adaptive Feature Compression System
          </span>
          <h1 className="text-4xl font-bold sm:text-5xl">
            A self-learning dimensionality reduction & feature ranking AI framework.
          </h1>
          <p className="max-w-2xl text-lg opacity-80">
            Upload a CSV, let AFCS clean and rank features, compress with PCA or a smart autoencoder, visualise latent structure, and export reproducible pipelines in seconds.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <Link href="/upload" className="focus-ring inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--primary)] px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:scale-105">
              Upload CSV <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/upload?demo=true" className="focus-ring inline-flex items-center gap-2 rounded-full border border-[var(--border)] px-6 py-3 text-sm">
              Try demo dataset
            </Link>
          </div>
        </motion.div>
      </section>

      <section className="grid gap-6 sm:grid-cols-3">
        {[
          {
            icon: <BarChart className="h-6 w-6" />,
            title: "Visual clarity",
            description: "Heatmaps, scree plots, and latent scatter bring your data stories forward."
          },
          {
            icon: <Brain className="h-6 w-6" />,
            title: "Smart compression",
            description: "Switch between PCA or autoencoder compression with seed-level reproducibility."
          },
          {
            icon: <Download className="h-6 w-6" />,
            title: "Export ready",
            description: "Download latent CSVs, pipeline artifacts, and metadata with a single click."
          }
        ].map((feature) => (
          <motion.div key={feature.title} whileHover={{ y: -4 }} className="glassy space-y-3 p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--accent)]/20 text-[var(--accent)]">
              {feature.icon}
            </div>
            <h3 className="text-lg font-semibold">{feature.title}</h3>
            <p className="text-sm opacity-80">{feature.description}</p>
          </motion.div>
        ))}
      </section>

      <section className="glassy p-8">
        <h2 className="text-2xl font-semibold">How it works</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-4">
          {["Upload", "Analyze", "Compress", "Export"].map((step, index) => (
            <div key={step} className="rounded-xl border border-[var(--border)]/60 p-4">
              <span className="text-sm font-mono text-[var(--accent)]">{String(index + 1).padStart(2, "0")}</span>
              <h3 className="mt-3 text-lg font-semibold">{step}</h3>
              <p className="text-sm opacity-75">
                {[
                  "Drop a CSV or use our demo dataset.",
                  "Preview inferred types, missingness, and feature stats.",
                  "Choose PCA or Autoencoder with clustering overlays.",
                  "Download compressed data, pipelines, and visual insights."
                ][index]}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
