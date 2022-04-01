import * as React from "react";
import { Component } from "react";
import "./studiesMenu.css";

interface StudiesMenuProps {
  studies: { name: string; id: number }[];
}

class StudiesMenu extends React.Component<StudiesMenuProps, any> {
  render() {
    const { studies } = this.props;

    return (
      <div className="bg-white studies-menu-container">
        <div className="studies-menu-header">
          <span>Studies</span>
        </div>
        <div className="studies-menu-content">
          <ul>
            {studies.map((s) => (
              <li key={s.id} id={"study-menu-" + s.id}>
                {s.name}
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
}

export default StudiesMenu;
