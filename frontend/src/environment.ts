export type Environment = "production" | "demo" | "development" | "test";

export const APP_ENV: Environment = (() => {
  if (import.meta.env.VITE_DEMO === "1") {
    return "demo";
  } else {
    return import.meta.env.MODE as Environment;
  }
})();
