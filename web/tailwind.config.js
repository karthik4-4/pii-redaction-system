/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080c14",
        surface: "#0f172a",
        card: "#1e293b",
        accent: "#3b82f6",
        cyanAccent: "#06b6d4",
      },
    },
  },
  plugins: [],
};
