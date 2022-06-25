import * as React from "react";
import { Component } from "react";
import "./checkField.css";

interface CheckFieldProps {
  id?: string;
  prefill?: boolean;
  label?: string;
  onChange?: (val: boolean) => void;
}

class CheckField extends React.Component<CheckFieldProps, any> {
  render() {
    const { id, prefill, label, onChange } = this.props;

    return (
      <div className="check-field-container">
        {label ? (
          <label className="check-field-label" htmlFor={id}>
            {label}
          </label>
        ) : null}
        <input
          type="checkbox"
          checked={prefill}
          onChange={
            onChange
              ? (e) => onChange((e.target as HTMLInputElement).checked)
              : () => null
          }
        />
      </div>
    );
  }
}

export default CheckField;
