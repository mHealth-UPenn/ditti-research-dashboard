import * as React from "react";
import { Component } from "react";
import { ReactComponent as Check } from "../../icons/check.svg";
import { renderToString } from "react-dom/server";

/**
 * id: an id of the item that will be toggled by the button
 * getActive: gets whether the toggled item is currently active
 * add: adds the item
 * remove: removes the item
 */
interface ToggleButtonProps {
  id: number;
  getActive: (id: number) => boolean;
  add: (id: number, callback: () => void) => void;
  remove: (id: number, callback: () => void) => void;
}

/**
 * active: whether the button is active
 */
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

    // get whether the toggled item is currently active
    this.state = {
      active: getActive(id)
    };
  }

  /**
   * Update the button's active state
   */
  update = () => {
    const { id, getActive } = this.props;

    // get whether the toggled item is currently active
    const active = getActive(id);
    this.setState({ active });
  };

  render() {
    const { id, add, remove } = this.props;

    // if the toggled item is active, show the button to remove the item and vice versa
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
