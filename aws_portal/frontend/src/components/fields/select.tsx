import * as React from "react";
import { Component } from "react";
import "./select.css";

/**
 * id: the value of the selected option
 * opts: an array of values and labels for each option
 * placeholder: a placeholder for when no option is selected
 * callback: a callback function for when an option is selected
 * getDefault: get the default string value given the id that was passed
 */
interface SelectProps {
  id: number;
  opts: { value: number; label: string }[];
  placeholder: string;
  callback: (selected: number, id: number) => void;
  getDefault: (id: number) => number;
}

/**
 * value: the string to display as the selected option
 */
interface SelectState {
  value: string;
}

export default class Select extends React.Component<SelectProps, SelectState> {
  constructor(props: SelectProps) {
    super(props);

    // set the default value
    this.state = {
      value: String(props.getDefault(props.id))
    };
  }

  /**
   * Change the displayed value when an option is selected and call the
   * callback function
   * @param e - the select field's change event
   */
  changeValue = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    const { callback, id } = this.props;
    const value = e.target.value;
    this.setState({ value }, () => callback(parseInt(value), id));
  };

  render() {
    let { opts } = this.props;
    const { placeholder } = this.props;
    const { value } = this.state;

    // always start with a blank option
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

        {/* if the blank option is selected, show the placeholder */}
        {value === "0" ? (
          <div className="select-placeholder">{placeholder}</div>
        ) : null}
        <select
          onChange={this.changeValue}
          value={value}
          style={{ minHeight: "calc(3rem - 2px)" }}
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
