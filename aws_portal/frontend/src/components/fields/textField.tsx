import * as React from "react";
import { Component } from "react";
import "./textField.css";

interface TextFieldProps {
  id: string;
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
    const { id, type, placeholder, prefill, label, onKeyup, feedback } =
      this.props;

    return (
      <div className="text-field-container">
        {label ? (
          <label className="text-field-label" htmlFor={id}>
            {label}
          </label>
        ) : null}
        <div className="text-field-content border-light">
          {this.props.children ? this.props.children : null}
          <div className="text-field-input">
            <input
              type={type ? type : "text"}
              placeholder={placeholder}
              defaultValue={prefill}
              onKeyUp={(e) => onKeyup((e.target as HTMLInputElement).value)}
            />
          </div>
        </div>
        {feedback ? (
          <span className="text-field-feedback">{feedback}</span>
        ) : null}
      </div>
    );
  }
}

export default TextField;
