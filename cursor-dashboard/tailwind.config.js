/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'data-missing': '#fbbf24', // yellow
        'data-verified': '#3b82f6', // blue
        'data-stale': '#ef4444', // red
        'editor-bg': '#1e1e1e',
        'sidebar-bg': '#252526',
        'accent': '#007acc',
      },
    },
  },
  plugins: [],
}
