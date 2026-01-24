/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // UFLI brand colors
        ufli: {
          primary: '#2563eb',    // Blue
          secondary: '#7c3aed',  // Purple
          accent: '#06b6d4',     // Cyan
        },
        // Status colors
        status: {
          passed: '#22c55e',     // Green for Y
          failed: '#ef4444',     // Red for N
          absent: '#f59e0b',     // Amber for A
          unenrolled: '#6b7280', // Gray for U
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
