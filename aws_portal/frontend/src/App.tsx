import React from "react";
import { Link } from "react-router-dom";
import "./App.css";
import Header from "./components/header";
import StudiesMenu from "./components/studiesMenu";

function App() {
  const studies = [
    { name: "MSBI", id: 1 },
    { name: "ART OSA", id: 2 }
  ];

  return (
    <main>
      <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
      <StudiesMenu studies={studies} />
    </main>
  );
}

export default App;
