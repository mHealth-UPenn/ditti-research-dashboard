import { createRoot } from "react-dom/client";
import LoginPage from "./loginPage";
import "./index.css";

const container = document.getElementById("root");
const root = createRoot(container!);
root.render(<LoginPage />);
