import { Header } from "./header";
import { Navbar } from "./navbar";
import "./dashboard.css";
import { Outlet } from "react-router-dom";
import { NavbarContextProvider } from "../contexts/navbarContext";
import { useFlashMessageContext } from "../contexts/flashMessagesContext";


export const Dashboard = () => {
  const { flashMessages } = useFlashMessageContext();

  return (
    <main className="flex flex-col h-screen">
      {/* header with the account menu  */}
      <Header />
      <div className="flex flex-grow max-h-[calc(100vh-4rem)]">

        {/* list of studies on the left of the screen */}
        {/* <StudiesMenu
          setView={setStudy}
          flashMessage={flashMessage}
          handleClick={setView}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          goBack={goBack} /> */}

        {/* main dashboard */}
        <div className="flex flex-col flex-grow max-w-[calc(100vw-16rem) overflow-hidden relative">
          <NavbarContextProvider>
            <Navbar />

            {/* flash messages */}
            {!!flashMessages.length &&
              <div className="flash-message-container">
                {flashMessages.map((fm) => fm.element)}
              </div>
            }
            <Outlet />
          </NavbarContextProvider>
        </div>
      </div>
    </main>
  );
};
