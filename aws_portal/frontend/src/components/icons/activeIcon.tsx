interface ActiveIconProps {
  active: boolean;
  className?: string;
}


const ActiveIcon = ({ active, className = "" }: ActiveIconProps) => {
  return (
    <div className="h-[1.35rem] flex items-end">
      <div className={`w-0 h-0 border-solid border-[0.5rem] ${active ? "border-success" : "border-[gray]"} rounded-2xl ${className}`} />
    </div>
  );
};


export default ActiveIcon;
