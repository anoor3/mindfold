"use client";

import { useMemo } from "react";

type DataTableProps = {
  data: Array<Record<string, unknown>>;
};

export function DataTable({ data }: DataTableProps) {
  const columns = useMemo(() => (data[0] ? Object.keys(data[0]) : []), [data]);

  if (data.length === 0) {
    return <p className="text-sm opacity-70">No dataset yet—drop a CSV to begin.</p>;
  }

  return (
    <div className="max-h-80 overflow-auto rounded-lg border border-[var(--border)]">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-[var(--muted)] text-xs uppercase tracking-wide">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-3 py-2 font-semibold">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="odd:bg-black/10">
              {columns.map((col) => (
                <td key={`${idx}-${col}`} className="px-3 py-2">
                  {String(row[col] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
