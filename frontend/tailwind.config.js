/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { colors } from "./src/colors";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,tsx}"],
  theme: {
    extend: {
      animation: {
        "spin-reverse-slow": "spin-reverse 2s linear infinite",
      },
      keyframes: {
        "spin-reverse": {
          from: { transform: "rotate(0deg)" },
          to: { transform: "rotate(-360deg)" },
        },
      },
    },
    colors: {
      white: colors.white,
      black: colors.black,
      primary: colors.primary,
      "primary-hover": colors.primaryHover,
      secondary: colors.secondary,
      "secondary-hover": colors.secondaryHover,
      "secondary-light": colors.secondaryLight,
      success: colors.success,
      "success-hover": colors.successHover,
      "success-dark": colors.successDark,
      "success-light": colors.successLight,
      "info-dark": colors.infoDark,
      "info-light": colors.infoLight,
      danger: colors.danger,
      "danger-hover": colors.dangerHover,
      "danger-dark": colors.dangerDark,
      "danger-light": colors.dangerLight,
      link: colors.link,
      "link-hover": colors.linkHover,
      light: colors.light,
      "extra-light": colors.extraLight,
      "wearable-wake": colors.wearableWake,
      "wearable-rem": colors.wearableRem,
      "wearable-light": colors.wearableLight,
      "wearable-deep": colors.wearableDeep,
    },
  },
  plugins: [],
};
