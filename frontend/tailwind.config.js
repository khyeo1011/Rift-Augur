/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#1a202c',
        'secondary': '#2d3748',
        'accent': '#4a5568',
        'highlight': '#a0aec0',
        'text-primary': '#e2e8f0',
        'text-secondary': '#cbd5e0',
      }
    },
  },
  plugins: [],
}