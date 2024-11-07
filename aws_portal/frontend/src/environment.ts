export type Environment = "production" | "demo" | "development";

export const APP_ENV: Environment = (() => {
  switch (process.env.REACT_APP_ENV) {
    case "production":
      return "production"
    case "demo":
      return "demo"
    default:
      return "development"
  }
})();
