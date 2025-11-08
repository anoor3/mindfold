"use client";

import dynamic from "next/dynamic";
import type { ReactNode } from "react";
import type { Data, Layout } from "plotly.js-dist-min";

type PlotProps = {
  data: Data[];
  layout?: Partial<Layout>;
};

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

type ChartCardProps = {
  title: string;
  description?: string;
  plot?: PlotProps;
  children?: ReactNode;
};

export function ChartCard({ title, description, plot, children }: ChartCardProps) {
  return (
    <section className="glassy flex flex-col gap-4 p-6">
      <div>
        <h3 className="text-xl font-semibold">{title}</h3>
        {description ? <p className="text-sm opacity-80">{description}</p> : null}
      </div>
      {plot ? <Plot data={plot.data} layout={{ autosize: true, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", margin: { t: 30 }, ...plot.layout }} style={{ width: "100%", height: "320px" }} /> : children}
    </section>
  );
}
