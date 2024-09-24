import { createRoot } from "react-dom/client";
import LoginPage from "./loginPage";
import "./index.css";
import "./output.css"
import { StrictMode } from "react";

const container = document.getElementById("root");
const root = createRoot(container!);
root.render(
  <StrictMode>
    <LoginPage />
  </StrictMode>
);
