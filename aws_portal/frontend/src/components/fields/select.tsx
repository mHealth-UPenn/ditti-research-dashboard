import * as React from "react";
import { Component } from "react";

interface SelectProps {
  id: number;
  opts: { value: number; label: string }[];
  placeholder: string;
  callback: (selected: number, id: number) => void;
  getDefault: (id: number) => number;
}

interface SelectState {
  value: string;
}

export default class Select extends React.Component<SelectProps, SelectState> {
  constructor(props: SelectProps) {
    super(props);

    this.state = {
      value: String(props.getDefault(props.id))
    };
  }

  changeValue = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    const { callback, id } = this.props;
    const value = e.target.value;
    this.setState({ value }, () => callback(parseInt(value), id));
  };

  render() {
    let { opts } = this.props;
    const { placeholder } = this.props;
    const { value } = this.state;
    opts = [{ value: 0, label: "" }].concat(opts);

    return (
      <div
        style={{
          alignItems: "center",
          display: "flex",
          flexGrow: 1,
          position: "relative"
        }}
      >
        {value === "0" ? (
          <div
            style={{
              position: "absolute",
              marginLeft: "1rem",
              backgroundColor: "white",
              color: "#B3B3CC"
            }}
          >
            {placeholder}
          </div>
        ) : null}
        <select
          onChange={this.changeValue}
          value={value}
          style={{ minHeight: "2.5rem" }}
        >
          {opts.map((opt, i) => (
            <option key={i} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    );
  }
}
