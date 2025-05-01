import { createRef } from "react";
import { RadioFieldProps } from "./fields.types";

export const RadioField = ({
  id,
  label,
  checked,
  values,
  onChange,
}: RadioFieldProps) => {
  const radioButtons = values.map((v, i) => {
    const ref = createRef<HTMLInputElement>();
    return (
      <div key={i} className="flex items-center">
        <label htmlFor={`${id ?? ""}-${v}`} className="cursor-pointer p-2">
          {v}
        </label>
        <input
          ref={ref}
          id={`${id ?? ""}-${v}`}
          className="cursor-pointer"
          type="radio"
          checked={v === checked}
          name={id}
          value={v}
          onChange={onChange}
        />
      </div>
    );
  });

  return (
    <div className="flex w-full flex-col">
      {label && <span className="mb-1">{label}</span>}
      <div className="flex select-none justify-evenly">{radioButtons}</div>
    </div>
  );
};
