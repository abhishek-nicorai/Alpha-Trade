/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0B0F14',
        'bg-secondary': '#111827',
        'bg-tertiary': '#1F2933',
        'border-muted': '#2A2F3A',
        'text-primary': '#E5E7EB',
        'text-secondary': '#9CA3AF',
        'profit': '#16A34A',
        'loss': '#DC2626',
        'warning': '#F59E0B',
      },
    },
  },
  plugins: [],
}