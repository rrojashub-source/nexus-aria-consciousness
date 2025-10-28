/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        nexus: {
          dark: '#0a0a0f',
          darker: '#050508',
          primary: '#00d4ff',
          secondary: '#7c3aed',
          accent: '#f97316',
        },
      },
    },
  },
  plugins: [],
}
