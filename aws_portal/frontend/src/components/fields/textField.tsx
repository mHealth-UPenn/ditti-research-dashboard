import * as React from "react";
import { Component } from "react";
import "./textField.css";

interface TextFieldProps {
  id?: string;
  type?: string;
  placeholder?: string;
  prefill?: string;
  value?: string;
  label?: string;
  onKeyup?: (text: string) => void;
  feedback?: string;
  disabled?: boolean;
}

interface TextFieldState {
  text: string;
}

class TextField extends React.Component<TextFieldProps, TextFieldState> {
  state = {
    text: ""
  };

  render() {
    const {
      id,
      type,
      placeholder,
      prefill,
      label,
      onKeyup,
      feedback,
      disabled,
      value
    } = this.props;
    console.log(prefill, value);

    return (
      <div className="text-field-container">
        {label ? (
          <label className="text-field-label" htmlFor={id}>
            {label}
          </label>
        ) : null}
        <div
          className={
            "text-field-content border-light" + (disabled ? " bg-light" : "")
          }
        >
          {this.props.children ? this.props.children : null}
          <div className="text-field-input">
            <input
              type={type ? type : "text"}
              placeholder={placeholder ? placeholder : ""}
              defaultValue={prefill ? prefill : undefined}
              value={value}
              onChange={
                onKeyup
                  ? (e) => onKeyup((e.target as HTMLInputElement).value)
                  : () => null
              }
              disabled={disabled}
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
