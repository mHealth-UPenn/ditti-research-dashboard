import * as React from "react";
import { Component } from "react";
import { ReactComponent as Check } from "../../icons/check.svg";
import { renderToString } from "react-dom/server";

interface ToggleButtonProps {
  add: (id: number, callback: (ids: number[]) => void) => void;
  ids: number[];
  id: number;
  remove: (id: number, callback: (ids: number[]) => void) => void;
}

interface ToggleButtonState {
  ids: number[];
}

class ToggleButton extends React.Component<
  ToggleButtonProps,
  ToggleButtonState
> {
  constructor(props: ToggleButtonProps) {
    super(props);

    this.state = {
      ids: this.props.ids
    };
  }

  callback = (ids: number[]) => {
    this.setState({ ids });
  };

  render() {
    const { add, id, remove } = this.props;
    const { ids } = this.state;

    return ids.some((x: number) => x == id) ? (
      <button
        className="button-success flex-center"
        onClick={() => {
          remove(id, this.callback);
        }}
      >
        <Check />
      </button>
    ) : (
      <button
        className="button-secondary"
        onClick={() => {
          add(id, this.callback);
        }}
      >
        Add&nbsp;+
      </button>
    );
  }
}

export default ToggleButton;
