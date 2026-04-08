/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        card: "0 18px 45px rgba(18, 24, 21, 0.08)",
      },
      colors: {
        parchment: "#f3f0e4",
        turf: "#5d8c45",
        ink: "#101814",
      },
      fontFamily: {
        display: ['"Iowan Old Style"', '"Palatino Linotype"', '"Book Antiqua"', "Georgia", "serif"],
        sans: ['"Avenir Next"', '"Segoe UI"', '"Helvetica Neue"', "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
