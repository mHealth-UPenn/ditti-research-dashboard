export type Environment = "production" | "demo" | "development" | "test";

export const APP_ENV: Environment = (() => {
  if (process.env.REACT_APP_DEMO === "1") {
    return "demo";
  } else {
    return process.env.NODE_ENV;
  }
})();
