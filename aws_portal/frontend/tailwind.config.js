/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,tsx}"],
  theme: {
    extend: {},
    colors: {
      "white": "#FFFFFF",
      "black": "#000000",
      "primary": "#3366FF",
      "primary-hover": "#0040FF",
      "secondary": "#33334D",
      "secondary-hover": "#1F1F2E",
      "secondary-light": "#B3B3CC",
      "success": "#00CC00",
      "success-hover": "#009900",
      "success-dark": "#155724",
      "success-light": "#C3E6CB",
      "info-dark": "#0C5460",
      "info-light": "#D1ECF1",
      "danger": "#FF0000",
      "danger-hover": "#CC0000",
      "danger-dark": "#721C24",
      "danger-light": "#F8D7DA",
      "link": "#666699",
      "link-hover": "#52527A",
      "light": "#B3B3CC",
    },
  },
  plugins: [],
}

