import { ActiveIconProps } from "./activeIcon.types";

export const ActiveIcon = ({ active, className = "" }: ActiveIconProps) => {
  return (
    <div className="flex h-[1.35rem] items-end">
      <div
        className={`size-0 border-[0.5rem] border-solid
          ${active ? "border-[#00CC00]" : "border-[gray]"} rounded-2xl
          ${className}`}
      />
    </div>
  );
};
