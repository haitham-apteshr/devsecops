/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cmrBlue: '#006B9F',
        cmrLightBlue: '#E6F0F5',
        cmrOrange: '#F08C4A'
      }
    },
  },
  plugins: [],
}
