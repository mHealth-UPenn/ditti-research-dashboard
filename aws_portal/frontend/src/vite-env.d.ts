/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />

interface ImportMeta {
  readonly env: {
    readonly VITE_FLASK_SERVER: string;
    readonly VITE_DEMO: string;
    // https://vite.dev/guide/env-and-mode#built-in-constants
    readonly MODE: string;
    readonly BASE_URL: string;
    readonly PROD: boolean;
    readonly DEV: boolean;
    readonly SSR: boolean;
  }
}
