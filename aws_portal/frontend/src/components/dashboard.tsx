import React, { createRef, useEffect, useReducer } from "react";
import StudiesView from "./dittiApp/studies";
import Header from "./header";
import Home from "./home";
import Navbar from "./navbar";
import "./dashboard.css";
import { IFlashMessage } from "../interfaces";
import FlashMessage, { FlashMessageVariant } from "./flashMessage/flashMessage";
import DittiDataContext from "../contexts/dittiDataContext";
import useDittiData from "../hooks/useDittiData";

type Action =
  | { type: "INIT"; name: string; view: React.ReactElement }
  | { type: "GO_BACK" }
  | { type: "FLASH_MESSAGE"; msg: React.ReactElement; variant: FlashMessageVariant }
  | { type: "CLOSE_MESSAGE"; id: number }
  | { type: "SET_VIEW"; name: string[]; view: React.ReactElement; replace: boolean | null }
  | { type: "SET_STUDY"; name: string; view: React.ReactElement; appView: React.ReactElement };


const reducer = (state: DashboardState, action: Action) => {
  switch (action.type) {
    case "INIT": {
      const { name, view } = action;
      return { ...state, breadcrumbs: [{ name, view }], view };
    }
    case "GO_BACK": {
      const history = [...state.history];

      // get the last set of breadcrumbs
      const breadcrumbs = history.pop();

      // if there was any history to begin with
      if (breadcrumbs) {

        // set the last view in the history as the new view
        const view = breadcrumbs[breadcrumbs.length - 1].view;
        return { ...state, breadcrumbs, history, view };
      }

      return state;
    }
    case "FLASH_MESSAGE": {
      const { msg, variant } = action;
      const flashMessages = [...state.flashMessages];
      const containerRef = createRef<HTMLDivElement>();
      const closeRef = createRef<HTMLDivElement>();

      // set the element's key to 0 or the last message's key + 1
      const id = flashMessages.length
        ? flashMessages[flashMessages.length - 1].id + 1
        : 0;

      const element =
        <FlashMessage
          key={id}
          variant={variant}
          containerRef={containerRef}
          closeRef={closeRef}>
            {msg}
        </FlashMessage>;

      // add the message to the page
      flashMessages.push({ id, element, containerRef, closeRef });
      return { ...state, flashMessages };
    }
    case "CLOSE_MESSAGE": {
      const { id } = action;
      let flashMessages = [...state.flashMessages];
      flashMessages = flashMessages.filter((fm) => fm.id != id);
      return { ...state, flashMessages };
    }
    case "SET_VIEW": {
      const { name, view, replace } = action;
      let breadcrumbs = [...state.breadcrumbs];
      const history = [...state.history];

      // add the current view to the history stack
      history.push(breadcrumbs.slice(0));

      // if replacing the top breadcrumb
      if (replace) breadcrumbs.pop();

      // for each breadcrumb
      let i = 0;
      for (const b of breadcrumbs) {

        // if this breadcrumb matches the first name to be used as breadcrumbs
        if (b.name === name[0]) {

          // then remove the following breadcrumbs to continue from this point
          breadcrumbs = breadcrumbs.slice(0, i + 1);
          break;
        } else if (i === breadcrumbs.length - 1) {

          // else add each name to the breadcrumbs
          for (const i in name) {

            // add the view only for the last name
            breadcrumbs.push({
              name: name[i],
              view: parseInt(i) === name.length - 1 ? view : <React.Fragment />
            });
          }
          break;
        }
        i++;
      }

      return { ...state, breadcrumbs, history, view };
    }
    case "SET_STUDY": {
      const { name, view, appView } = action;
      let breadcrumbs = [...state.breadcrumbs];
      const history = [...state.history];
      history.push(breadcrumbs.slice(0));

      breadcrumbs = breadcrumbs.slice(0, 2);
      if (breadcrumbs.length == 1) {
        breadcrumbs.push({ name: "Ditti App", view: appView });
      }

      breadcrumbs.push({ name, view });
      return { ...state, breadcrumbs, history, view }
    }
    default:
      return state;
  }
};


/**
 * breadcrumbs: the breadcrumbs to display in the navbar
 * flashMessages: messages to be displayed on the page
 * history: a history stack for user navigation
 * taps: tap data
 * users: this is unused
 * view: the current view
 */
interface DashboardState {
  breadcrumbs: { name: string; view: React.ReactElement }[];
  flashMessages: IFlashMessage[];
  history: { name: string; view: React.ReactElement }[][];
  view: React.ReactElement;
}

const initialState: DashboardState = {
  breadcrumbs: [],
  flashMessages: [],
  history: [],
  view: <React.Fragment />,
};


const Dashboard: React.FC = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { breadcrumbs, flashMessages, history, view } = state;

  const {
    dataLoading,
    taps,
    audioTaps,
    audioFiles,
    users,
    refreshAudioFiles,
    getUserByDittiId,
  } = useDittiData();

  useEffect(() => {
    const view = (
      <Home
        handleClick={setView}
        goBack={goBack}
        flashMessage={flashMessage} />
    );
    dispatch({ type: "INIT", name: "Home", view })
  }, []);

  useEffect(() => {
    flashMessages.forEach(flashMessage => {
      const closeDiv = flashMessage.closeRef.current;
      if (closeDiv && !closeDiv.onclick) {
        closeDiv.onclick = () => popMessage(flashMessage.id);
      }

      const containerDiv = flashMessage.containerRef.current;
      if (containerDiv) {
        setTimeout(() => containerDiv.style.opacity = "0", 3000);
        setTimeout(() => popMessage(flashMessage.id), 5000)
      }
    });
  }, [flashMessages]);

  const setView = (
    name: string[], view: React.ReactElement, replace: boolean | null = null
  ) => {
    dispatch({ type: "SET_VIEW", name, view, replace })
  };

  const setStudy = (name: string, view: React.ReactElement) => {
    const appView =
      <StudiesView
        handleClick={setView}
        goBack={goBack}
        flashMessage={flashMessage} />
    dispatch({ type: "SET_STUDY", name, view, appView });
  };

  const goBack = () => dispatch({ type: "GO_BACK" });

  const flashMessage = (msg: React.ReactElement, variant: FlashMessageVariant) => {
    dispatch({ type: "FLASH_MESSAGE", msg, variant });
  };

  const popMessage = (id: number) => dispatch({ type: "CLOSE_MESSAGE", id });

  return (
    <main className="flex flex-col h-screen">
      {/* header with the account menu  */}
      <Header
        handleClick={setView}
        goBack={goBack}
        flashMessage={flashMessage} />
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

          {/* navigation bar */}
          <Navbar
            breadcrumbs={breadcrumbs}
            handleBack={goBack}
            handleClick={setView}
            hasHistory={history.length > 0} />

          {/* flash messages */}
          {!!flashMessages.length &&
            <div className="flash-message-container">
              {flashMessages.map((fm) => fm.element)}
            </div>
          }

          {/* current view */}
          <DittiDataContext.Provider value={{
              dataLoading,
              taps,
              audioTaps,
              audioFiles,
              users,
              refreshAudioFiles,
              getUserByDittiId,
            }}>
              {view}
          </DittiDataContext.Provider>
        </div>
      </div>
    </main>
  );
};


export default Dashboard;
