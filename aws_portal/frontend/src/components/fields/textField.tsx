import * as React from "react";
import { Component } from "react";
import "./textField.css";

interface TextFieldProps {
  id: string;
  svg: React.ReactElement;
  type: string;
  placeholder: string;
  prefill: string;
  label: string;
  onKeyup: (text: string) => void;
  feedback: string;
}

interface TextFieldState {
  text: string;
}

class TextField extends React.Component<TextFieldProps, TextFieldState> {
  state = {
    text: ""
  };

  render() {
    const { id, svg, type, placeholder, prefill, label, onKeyup, feedback } =
      this.props;

    return (
      <div className="text-field-container">
        {label ? (
          <label className="text-field-label" htmlFor={id}>
            {label}
          </label>
        ) : null}
        <div className="text-field-content border-light">
          {svg ? svg : null}
          {this.props.children ? this.props.children : null}
          <input
            type={type ? type : "text"}
            className="text-field-input"
            placeholder={placeholder}
            defaultValue={prefill}
            onKeyUp={(e) => onKeyup((e.target as HTMLInputElement).value)}
          />
        </div>
        {feedback ? (
          <span className="text-field-feedback">{feedback}</span>
        ) : null}
      </div>
    );
  }
}

export default TextField;
