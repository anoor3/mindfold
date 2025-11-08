import "../styles/globals.css";

import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import Link from "next/link";

import { Providers } from "../components/providers";
import { ThemeToggle } from "../components/ThemeToggle";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "Adaptive Feature Compression System",
  description: "A self-learning dimensionality reduction & feature ranking AI framework."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="bg-[var(--bg)] text-[var(--text)]">
        <Providers>
          <a href="#main" className="sr-only focus:not-sr-only focus-ring m-2 inline-block rounded bg-[var(--accent)] px-3 py-2 text-sm text-black">
            Skip to content
          </a>
          <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--bg)]/80 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
                <span className="h-2 w-12 rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--primary)]" aria-hidden="true" />
                AFCS
              </Link>
              <nav className="flex items-center gap-4 text-sm">
                <Link href="/upload" className="hover:text-[var(--accent)]">
                  Upload
                </Link>
                <Link href="/help" className="hover:text-[var(--accent)]">
                  Help
                </Link>
                <ThemeToggle />
              </nav>
            </div>
          </header>
          <main id="main" className="mx-auto max-w-6xl px-6 py-10">
            {children}
          </main>
          <footer className="border-t border-[var(--border)] bg-[var(--bg)]/80">
            <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 text-sm opacity-75 sm:flex-row sm:items-center sm:justify-between">
              <p>© {new Date().getFullYear()} Adaptive Feature Compression System.</p>
              <p>All processing stays on your device.</p>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}
