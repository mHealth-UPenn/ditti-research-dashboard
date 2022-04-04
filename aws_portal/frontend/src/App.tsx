import React from "react";
import { Link } from "react-router-dom";
import "./App.css";
import Header from "./components/header";
import Navbar from "./components/navbar";
import StudiesMenu from "./components/studiesMenu";

function App() {
  const studies = [
    { name: "MSBI", id: 1 },
    { name: "ART OSA", id: 2 }
  ];

  const breadcrumbs = [{ name: "Home" }, { name: "Ditti App" }];

  return (
    <main>
      <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
      <div style={{ display: "flex", flexGrow: 1 }}>
        <StudiesMenu studies={studies} />
        <Navbar breadcrumbs={breadcrumbs} />
      </div>
    </main>
  );
}

export default App;
