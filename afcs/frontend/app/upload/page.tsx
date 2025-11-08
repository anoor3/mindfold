"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { DataTable } from "../../components/DataTable";
import { FileDropzone } from "../../components/FileDropzone";
import { uploadFile } from "../../lib/api";

const formSchema = z.object({
  missing_policy: z.enum(["drop", "median", "most_frequent"]).default("median"),
  encode_categorical: z.boolean().default(true),
  standardize: z.boolean().default(true)
});

type FormValues = z.infer<typeof formSchema>;

export default function UploadPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [preview, setPreview] = useState<Array<Record<string, unknown>>>([]);
  const [info, setInfo] = useState<{ name: string; rows: number; cols: number } | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      missing_policy: "median",
      encode_categorical: true,
      standardize: true
    }
  });

  const uploadMutation = useMutation({
    mutationFn: async (payload: { file?: File; demo?: boolean }) =>
      uploadFile(payload.file ?? new File([], ""), payload.demo ?? false),
    onSuccess: async (data) => {
      setDatasetId(data.id);
      setInfo({ name: data.name, rows: data.rows, cols: data.cols });
      setPreview([]);
    }
  });

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === "u") {
        event.preventDefault();
        inputRef.current?.click();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const onSubmit = (values: FormValues) => {
    if (!datasetId) return;
    const params = new URLSearchParams({
      missing: values.missing_policy,
      encode: values.encode_categorical ? "1" : "0",
      standardize: values.standardize ? "1" : "0"
    });
    router.push(`/analysis/${datasetId}?${params.toString()}`);
  };

  return (
    <div className="space-y-10">
      <div className="glassy p-8">
        <h1 className="text-3xl font-bold">Upload your dataset</h1>
        <p className="mt-2 text-sm opacity-80">
          CSV files up to 50MB. Keyboard shortcut <kbd className="rounded bg-black/40 px-2 py-1 font-mono text-xs">U</kbd> opens the file picker.
        </p>
        <div className="mt-6 space-y-6">
          <FileDropzone
            onDrop={(file) => uploadMutation.mutate({ file })}
            hint={uploadMutation.isPending ? "Uploading…" : "Drop CSV or click"}
          />
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) uploadMutation.mutate({ file });
            }}
          />
        </div>
      </div>

      <div className="glassy space-y-6 p-8">
        <h2 className="text-2xl font-semibold">Options</h2>
        <form className="grid gap-6 sm:grid-cols-2" onSubmit={form.handleSubmit(onSubmit)}>
          <label className="flex flex-col gap-2 text-sm">
            Missing value policy
            <select className="rounded border border-[var(--border)] bg-transparent p-2" {...form.register("missing_policy")}>
              <option value="drop">Drop rows</option>
              <option value="median">Fill numeric median</option>
              <option value="most_frequent">Fill most frequent</option>
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" className="h-4 w-4" {...form.register("encode_categorical")} /> One-hot encode categorical columns
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" className="h-4 w-4" {...form.register("standardize")} /> Standardize numeric features
          </label>
          <button
            type="submit"
            disabled={!datasetId}
            className="focus-ring col-span-full inline-flex w-full items-center justify-center rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--primary)] px-6 py-3 text-sm font-semibold disabled:opacity-50"
          >
            Continue to Analysis
          </button>
        </form>
        {info ? (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Preview: {info.name}</h3>
            <p className="text-sm opacity-70">
              {info.rows.toLocaleString()} rows × {info.cols} columns detected.
            </p>
            <DataTable data={preview} />
          </div>
        ) : (
          <p className="text-sm opacity-70">No dataset yet—drop a CSV to begin.</p>
        )}
      </div>
    </div>
  );
}
