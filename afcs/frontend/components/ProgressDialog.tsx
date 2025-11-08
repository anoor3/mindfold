"use client";

import { motion } from "framer-motion";

export type ProgressDialogProps = {
  open: boolean;
  progress: number;
  message?: string;
};

export function ProgressDialog({ open, progress, message }: ProgressDialogProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glassy w-full max-w-md space-y-4 p-6"
      >
        <h2 className="text-lg font-semibold">Processing dataset</h2>
        <p className="text-sm opacity-75">{message ?? "Crunching numbers—this won't take long."}</p>
        <div className="h-3 w-full rounded-full bg-black/30">
          <div
            className="h-3 rounded-full bg-[var(--accent)] transition-all"
            style={{ width: `${progress}%` }}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
          />
        </div>
      </motion.div>
    </div>
  );
}
