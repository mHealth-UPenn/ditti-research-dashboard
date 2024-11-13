import React, { ChangeEvent, createRef } from "react";

/**
 * id (optional): an optional html id
 * prefill (optional): whether the field is checked
 * label (optional): the field's label text
 * onChange (optional): a callback function when the field is clicked
 */
interface RadioFieldProps {
  id?: string;
  label?: string;
  checked?: string;
  values: string[];
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
}

const RadioField: React.FC<RadioFieldProps> = ({
    id,
    label,
    checked,
    values,
    onChange
}) => {
  const radioButtons = values.map((v, i) => {
    const ref = createRef<HTMLInputElement>();
    return (
      <div key={i} className="flex items-center">
        <label
          htmlFor={`${id}-${v}`}
          className="p-2 cursor-pointer">
            {v}
        </label>
        <input
          ref={ref}
          id={`${id}-${v}`}
          className="cursor-pointer"
          type="radio"
          checked={v === checked}
          name={id}
          value={v}
          onChange={onChange} />
      </div>
    );
  });

  return (
    <div className="flex flex-col w-full">
      {label &&
        <span className="mb-1">
          {label}
        </span>
      }
      <div className="flex justify-evenly select-none">
        {radioButtons}
      </div>
    </div>
  );
};

export default RadioField;
