import React from "react";
import { Link } from "react-router-dom";
import "./App.css";
import AppView from "./components/views/appView";
import Dashboard from "./components/dashboard";
import Header from "./components/header";
import HomeView from "./components/views/homeView";
import Navbar from "./components/navbar";
import StudiesMenu from "./components/studiesMenu";

function App() {
  const studies = [
    { name: "MSBI", id: 1 },
    { name: "ART OSA", id: 2 }
  ];

  const breadcrumbs = [
    { name: "Home", view: () => HomeView },
    { name: "Ditti App", view: () => AppView }
  ];

  return (
    <Dashboard>
      <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
      <div style={{ display: "flex", flexGrow: 1 }}>
        <StudiesMenu studies={studies} />
        <div style={{ display: "flex", flexDirection: "column", flexGrow: 1 }}>
          <Navbar breadcrumbs={breadcrumbs} />
        </div>
      </div>
    </Dashboard>
  );
}

export default App;
