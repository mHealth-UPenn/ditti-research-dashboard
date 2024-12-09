import { PropsWithChildren } from "react";
import { APP_ENV } from "../../environment";
import Button from "../buttons/button";

interface IViewContainerProps {
  navbar?: boolean;
  participantDashboard?: boolean;
}


const ViewContainer = ({
  navbar = true,
  participantDashboard = false,
  children
}: PropsWithChildren<IViewContainerProps>) => {
  const height =
    navbar ?
    "min-h-[calc(calc(100vh-8rem)-1px)] h-[calc(calc(100vh-8rem)-1px)]" :
    "min-h-[calc(calc(100vh-4rem)-1px)] h-[calc(calc(100vh-4rem)-1px)]";

  return (
    <div className={`relative bg-extra-light ${height} px-4 py-16 md:px-6 overflow-scroll`}>
      {APP_ENV === "demo" &&
        <div className="absolute top-[16px] flex justify-center w-full">
          <span className="text-sm italic">All data are simulated and for demonstration purposes only.</span>
        </div>
      }
      <div className="relative flex flex-wrap basis-[content]">
        {children}
      </div>
      {(participantDashboard && APP_ENV === "demo") &&
        <Button
          size="lg"
          rounded={true}
          className="fixed bottom-[32px] left-[24px] shadow-xl"
          onClick={() => window.location.href = "/coordinator"}>
            View the Coordinator Dashboard
        </Button>
      }
      {(!participantDashboard && APP_ENV === "demo") &&
        <Button
          size="lg"
          rounded={true}
          className="fixed bottom-[32px] left-[24px] shadow-xl"
          onClick={() => window.location.href = "/"}>
            View the Participant Dashboard
        </Button>
      }
    </div>
  );
};


export default ViewContainer;
