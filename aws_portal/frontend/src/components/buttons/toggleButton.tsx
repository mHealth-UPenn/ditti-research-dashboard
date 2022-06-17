import * as React from "react";
import { Component } from "react";
import { ReactComponent as Check } from "../../icons/check.svg";
import { renderToString } from "react-dom/server";

interface ToggleButtonProps {
  id: number;
  getActive: (id: number) => boolean;
  add: (id: number, callback: () => void) => void;
  remove: (id: number, callback: () => void) => void;
}

interface ToggleButtonState {
  active: boolean;
}

class ToggleButton extends React.Component<
  ToggleButtonProps,
  ToggleButtonState
> {
  constructor(props: ToggleButtonProps) {
    const { id, getActive } = props;
    super(props);

    this.state = {
      active: getActive(id)
    };
  }

  update = () => {
    const { id, getActive } = this.props;
    const active = getActive(id);
    this.setState({ active });
  };

  render() {
    const { id, add, remove } = this.props;

    return this.state.active ? (
      <button
        className="button-success flex-center"
        onClick={() => remove(id, this.update)}
      >
        <Check />
      </button>
    ) : (
      <button className="button-secondary" onClick={() => add(id, this.update)}>
        Add&nbsp;+
      </button>
    );
  }
}

export default ToggleButton;
