import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#1F2937",
        paper: "#FFFDF7",
        leaf: "#2F855A",
        sun: "#F59E0B"
      }
    }
  },
  plugins: []
};

export default config;
