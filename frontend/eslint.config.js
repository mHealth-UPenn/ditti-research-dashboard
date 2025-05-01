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
  }
);
