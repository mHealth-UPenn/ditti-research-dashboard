import React from "react";
import { Link } from "react-router-dom";
import "./App.css";
import Header from "./components/header";

function App() {
  return (
    <main>
      <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
    </main>
  );
}

export default App;
