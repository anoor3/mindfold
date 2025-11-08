/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      },
      colors: {
        aurora: {
          bg: "hsl(222 14% 10%)",
          card: "hsl(222 14% 12%)",
          muted: "hsl(222 12% 16%)",
          border: "hsl(222 10% 22%)",
          text: "hsl(210 20% 98%)",
          primary: "hsl(258 90% 66%)",
          accent: "hsl(160 84% 40%)"
        }
      }
    }
  },
  plugins: []
};
