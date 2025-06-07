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

import js from "@eslint/js";
import tseslint from "typescript-eslint";
import tsParser from "@typescript-eslint/parser";
import importPlugin from "eslint-plugin-import";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import prettierRecommended from "eslint-plugin-prettier/recommended";
import tailwind from "eslint-plugin-tailwindcss";

export default tseslint.config(
  { ignores: ["**/node_modules/**", "dist/**", "build/**", ".env.*"] },

  // JS config
  {
    files: ["**/*.js"],
    ignores: ["dist/**", "build/**"],
    languageOptions: {
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: { version: "detect" },
      "import/ignore": ["node_modules"], // skip parsing modules we didn't author
      "import/resolver": {
        node: { extensions: [".js", ".jsx", ".ts", ".tsx"] },
        typescript: { project: "./tsconfig.json", alwaysTryTypes: true },
      },
    },
    extends: [
      js.configs.recommended, // ESLint core
      importPlugin.flatConfigs["recommended"], // import checks
      prettierRecommended, // Prettier formatting
    ],
    rules: {
      // JS-specific rule overrides
    },
  },

  // TS/TSX config
  {
    files: ["**/*.{ts,tsx}"],
    ignores: ["dist/**", "build/**"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: ["./tsconfig.json"],
        tsconfigRootDir: import.meta.dirname,
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: { version: "detect" },
      "import/resolver": {
        node: { extensions: [".js", ".jsx", ".ts", ".tsx"] },
        typescript: { project: "./tsconfig.json", alwaysTryTypes: true },
      },
    },
    extends: [
      js.configs.recommended,
      importPlugin.flatConfigs.recommended,
      importPlugin.flatConfigs.typescript,
      tseslint.configs.recommended,
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      reactPlugin.configs.flat.recommended,
      reactPlugin.configs.flat["jsx-runtime"],
      reactHooksPlugin.configs["recommended-latest"],
      tailwind.configs["flat/recommended"],
      prettierRecommended,
    ],
    rules: {
      // TS-specific rule overrides
      "tailwindcss/no-custom-classname": "off",
    },
  },

  // Test-specific TS/TSX config
  {
    files: ["tests/**/*.{ts,tsx}"],
    rules: {
      // Disable for expect.any() and other test patterns
      "@typescript-eslint/no-unsafe-assignment": "off",
      // Often needed for flexible mock call assertions
      "@typescript-eslint/no-unsafe-call": "off",
      // Also common for mocks
      "@typescript-eslint/no-unsafe-member-access": "off",
      // Common mock assertion patterns
      "@typescript-eslint/unbound-method": "off",
    },
  }
);
