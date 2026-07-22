import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        primary: "#2563EB",
        accent: "#16A34A",
        danger: "#DC2626",
        surface: "#F8FAFC",
        ink: "#1F2937",
      },
      boxShadow: {
        soft: "0 8px 24px rgba(15, 23, 42, 0.07)",
      },
    },
  },
  plugins: [],
} satisfies Config;
