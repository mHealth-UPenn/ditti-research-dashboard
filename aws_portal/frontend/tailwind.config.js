import colors from "./src/colors";

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,tsx}"],
  theme: {
    extend: {},
    colors: {
      "white": colors.white,
      "black": colors.black,
      "primary": colors.primary,
      "primary-hover": colors.primaryHover,
      "secondary": colors.secondary,
      "secondary-hover": colors.secondaryHover,
      "secondary-light": colors.secondaryLight,
      "success": colors.success,
      "success-hover": colors.successHover,
      "success-dark": colors.successDark,
      "success-light": colors.successLight,
      "info-dark": colors.infoDark,
      "info-light": colors.infoLight,
      "danger": colors.danger,
      "danger-hover": colors.dangerHover,
      "danger-dark": colors.dangerDark,
      "danger-light": colors.dangerLight,
      "link": colors.link,
      "link-hover": colors.linkHover,
      "light": colors.light,
      "extra-light": colors.extraLight,
    },
  },
  plugins: [],
}

