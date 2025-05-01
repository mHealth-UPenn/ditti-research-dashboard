import { CheckFieldProps } from "./fields.types";

export const CheckField = ({
  id,
  prefill,
  label,
  onChange,
}: CheckFieldProps) => {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-1 hidden md:flex">&nbsp;</div>
      <div className="flex grow items-center">
        <div>
          {label && (
            <label className="mr-4" htmlFor={id}>
              {label}
            </label>
          )}
          <input
            type="checkbox"
            checked={prefill}
            onChange={
              onChange
                ? (e) => {
                    onChange((e.target as HTMLInputElement).checked);
                  }
                : () => null
            }
          />
        </div>
      </div>
    </div>
  );
};
