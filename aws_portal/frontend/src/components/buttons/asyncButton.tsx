import * as React from "react";
import { Component } from "react";

/**
 * onClick: the function to handle clicks
 * text: the text to display in the button
 * type: the button's type (primary, secondary, etc.)
 */
interface AsyncButtonProps {
  onClick: () => Promise<any>;
  text: string;
  type: string;
}

/**
 * loading: whether to show the loader
 */
interface AsyncButtonState {
  loading: boolean;
}

class AsyncButton extends React.Component<AsyncButtonProps, AsyncButtonState> {
  state = { loading: false };

  /**
   * Show the loader, call the onClick function, and hide the loader when the
   * promise is complete
   */
  handleClick = (): void => {
    this.setState({ loading: true }, () =>
      this.props.onClick().then(() => this.setState({ loading: false }))
    );
  };

  render() {
    const { text, type } = this.props;

    const loader = (
      <div className="lds-ring lds-ring-small">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    );

    return (
      <button
        className={"button button-large button-" + type}
        onClick={this.handleClick}
      >
        {this.state.loading ? loader : text}
      </button>
    );
  }
}

export default AsyncButton;
