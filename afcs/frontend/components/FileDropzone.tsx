"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

export type FileDropzoneProps = {
  onDrop: (file: File) => void;
  disabled?: boolean;
  hint?: string;
};

export function FileDropzone({ onDrop, disabled, hint }: FileDropzoneProps) {
  const handleDrop = useCallback(
    (files: File[]) => {
      if (files.length > 0) {
        onDrop(files[0]);
      }
    },
    [onDrop]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleDrop,
    disabled,
    accept: { "text/csv": [".csv"] }
  });

  return (
    <div
      {...getRootProps()}
      className="glassy flex h-48 cursor-pointer flex-col items-center justify-center gap-3 border-dashed border-[var(--border)] p-6 text-center transition hover:border-[var(--accent)]"
    >
      <input {...getInputProps()} />
      <p className="text-lg font-semibold">{isDragActive ? "Drop your CSV" : "Drag & drop or click to upload"}</p>
      <p className="text-sm text-muted-foreground opacity-75">{hint ?? "CSV up to 50MB"}</p>
    </div>
  );
}
