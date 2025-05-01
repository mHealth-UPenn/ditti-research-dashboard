import { Header } from "../header";
import { Navbar } from "../navbar";
import "./dashboard.css";
import { Outlet } from "react-router-dom";
import { NavbarContextProvider } from "../../contexts/navbarContext";
import { useFlashMessages } from "../../hooks/useFlashMessages";

export const Dashboard = () => {
  const { flashMessages } = useFlashMessages();

  return (
    <main className="flex h-screen flex-col">
      {/* header with the account menu  */}
      <Header />
      <div className="flex max-h-[calc(100vh-4rem)] grow">
        {/* list of studies on the left of the screen */}
        {/* <StudiesMenu
          setView={setStudy}
          flashMessage={flashMessage}
          handleClick={setView}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          goBack={goBack} /> */}

        {/* main dashboard */}
        <div
          className="max-w-[calc(100vw-16rem) relative flex grow flex-col
            overflow-hidden"
        >
          <NavbarContextProvider>
            <Navbar />

            {/* flash messages */}
            {!!flashMessages.length && (
              <div className="flash-message-container">
                {flashMessages.map((fm) => fm.element)}
              </div>
            )}
            <Outlet />
          </NavbarContextProvider>
        </div>
      </div>
    </main>
  );
};
