interface ActiveIconProps {
  active: boolean;
  className?: string;
}


export const ActiveIcon = ({ active, className = "" }: ActiveIconProps) => {
  return (
    <div className="h-[1.35rem] flex items-end">
      <div className={`w-0 h-0 border-solid border-[0.5rem] ${active ? "border-[#00CC00]" : "border-[gray]"} rounded-2xl ${className}`} />
    </div>
  );
};
