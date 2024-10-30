import React, { createRef, useEffect, useReducer, useRef } from "react";
import StudiesView from "./dittiApp/studies";
import Header from "./header";
import Home from "./home";
import Navbar from "./navbar";
import StudiesMenu from "./studiesMenu";
import "./dashboard.css";
import { AudioFile, AudioTap, AudioTapDetails, IFlashMessage, Tap, TapDetails, UserDetails } from "../interfaces";
import { differenceInMilliseconds } from "date-fns";
import { makeRequest } from "../utils";
import FlashMessage, { FlashMessageVariant } from "./flashMessage/flashMessage";
import { APP_ENV } from "../environment";
import dataFactory from "../dataFactory";

type Action =
  | { type: "INIT"; name: string; view: React.ReactElement }
  | { type: "GO_BACK" }
  | { type: "FLASH_MESSAGE"; msg: React.ReactElement; variant: FlashMessageVariant }
  | { type: "CLOSE_MESSAGE"; id: number }
  | { type: "SET_VIEW"; name: string[]; view: React.ReactElement; replace: boolean | null }
  | { type: "SET_STUDY"; name: string; view: React.ReactElement; appView: React.ReactElement }
  | { type: "SET_TAPS"; taps: TapDetails[] }
  | { type: "SET_AUDIO_TAPS"; audioTaps: AudioTapDetails[] }
  | { type: "SET_AUDIO_FILES"; audioFiles: AudioFile[] };


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
    case "SET_TAPS": {
      const { taps } = action;
      taps.sort((a, b) => differenceInMilliseconds(a.time, b.time));
      return { ...state, taps };
    }
    case "SET_AUDIO_TAPS": {
      const { audioTaps } = action;
      audioTaps.sort((a, b) => differenceInMilliseconds(a.time, b.time));
      return { ...state, audioTaps };
    }
    case "SET_AUDIO_FILES": {
      return { ...state, audioFiles: action.audioFiles };
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
  taps: TapDetails[];
  audioTaps: AudioTapDetails[];
  users: UserDetails[];
  audioFiles: AudioFile[];
  view: React.ReactElement;
}

const initialState: DashboardState = {
  breadcrumbs: [],
  flashMessages: [],
  history: [],
  taps: [],
  audioTaps: [],
  users: [],
  audioFiles: [],
  view: <React.Fragment />,
};


const Dashboard: React.FC = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { breadcrumbs, flashMessages, history, taps, audioTaps, audioFiles, view } = state;
  const tapRef = useRef<TapDetails[]>();
  const audioTapRef = useRef<AudioTapDetails[]>();
  const audioFileRef = useRef<AudioFile[]>();

  useEffect(() => {
    const view = (
      <Home
        getTapsAsync={getTapsAsync}
        getTaps={getTaps}
        getAudioTapsAsync={getAudioTapsAsync}
        getAudioTaps={getAudioTaps}
        getAudioFilesAsync={getAudioFilesAsync}
        getAudioFiles={getAudioFiles}
        handleClick={setView}
        goBack={goBack}
        flashMessage={flashMessage}
      />
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

  useEffect(() => {
    tapRef.current = taps;
  }, [taps])

  useEffect(() => {
    audioTapRef.current = audioTaps;
  }, [audioTaps])

  useEffect(() => {
    audioFileRef.current = audioFiles;
  }, [audioFiles])

  const getTapsAsync = async (): Promise<TapDetails[]> => {
    // if AWS has not been queried yet
    if (!taps.length) {
      let updatedTaps: TapDetails[];

      if (APP_ENV === "production") {
        updatedTaps = await makeRequest("/aws/get-taps?app=2").then((res: Tap[]) => {
          return res.map((tap) => {
            return { dittiId: tap.dittiId, time: new Date(tap.time) };
          });
        });
      } else {
        updatedTaps = dataFactory.taps;
      }

      // sort taps by timestamp
      updatedTaps = updatedTaps.sort((a, b) =>
        differenceInMilliseconds(new Date(a.time), new Date(b.time))
      );
    
      dispatch({ type: "SET_TAPS", taps: updatedTaps });
    }

    return taps;
  };

  const getTaps = (): TapDetails[] => tapRef.current || [];

  const getAudioTapsAsync = async (): Promise<AudioTapDetails[]> => {
    // if AWS has not been queried yet
    if (!audioTaps.length) {
      let updatedAudioTaps: AudioTapDetails[];

      if (APP_ENV == "production") {
        updatedAudioTaps = await makeRequest("/aws/get-audio-taps?app=2").then((res: AudioTap[]) => {
          return res.map((at) => {
            return {
              dittiId: at.dittiId,
              audioFileTitle: at.audioFileTitle,
              time: new Date(at.time),
              timezone: at.timezone,
              action: at.action,
            };
          });
        });
      } else {
        updatedAudioTaps = dataFactory.audioTaps;
      }

      // sort taps by timestamp
      updatedAudioTaps = updatedAudioTaps.sort((a, b) =>
        differenceInMilliseconds(new Date(a.time), new Date(b.time))
      );

      dispatch({ type: "SET_AUDIO_TAPS", audioTaps: updatedAudioTaps });
    }

    return audioTaps;
  };

  const getAudioTaps = (): AudioTapDetails[] => audioTapRef.current || [];

  const getAudioFilesAsync = async (): Promise<AudioFile[]> => {
    // if AWS has not been queried yet
    if (!audioFiles.length) {
      let newAudioFiles: AudioFile[];

      if (APP_ENV === "production") {
        newAudioFiles = await makeRequest("/aws/get-audio-files?app=2");
      } else {
        newAudioFiles = dataFactory.audioFiles;
      }

      dispatch({ type: "SET_AUDIO_FILES", audioFiles: newAudioFiles });
    }

    return audioFiles;
  };

  const getAudioFiles = () => audioFileRef.current || [];

  const setView = (
    name: string[], view: React.ReactElement, replace: boolean | null = null
  ) => {
    dispatch({ type: "SET_VIEW", name, view, replace })
  };

  const setStudy = (name: string, view: React.ReactElement) => {
    const appView =
      <StudiesView
        getTapsAsync={getTapsAsync}
        getTaps={getTaps}
        getAudioTapsAsync={getAudioTapsAsync}
        getAudioTaps={getAudioTaps}
        getAudioFilesAsync={getAudioFilesAsync}
        getAudioFiles={getAudioFiles}
        handleClick={setView}
        goBack={goBack}
        flashMessage={flashMessage}
      />
    dispatch({ type: "SET_STUDY", name, view, appView });
  };

  const goBack = () => dispatch({ type: "GO_BACK" });

  const flashMessage = (msg: React.ReactElement, variant: FlashMessageVariant) => {
    dispatch({ type: "FLASH_MESSAGE", msg, variant });
  };

  const popMessage = (id: number) => dispatch({ type: "CLOSE_MESSAGE", id });

  return (
    <main className="bg-[#F0F0F5] flex flex-col h-screen">

      {/* header with the account menu  */}
      <Header
        handleClick={setView}
        goBack={goBack}
        flashMessage={flashMessage}
      />
      <div className="flex flex-grow max-h-[calc(100vh-4rem)">

        {/* list of studies on the left of the screen */}
        <StudiesMenu
          setView={setStudy}
          flashMessage={flashMessage}
          handleClick={setView}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          goBack={goBack}
        />

        {/* main dashboard */}
        <div className="flex flex-col flex-grow max-w-[calc(100vw-16rem) overflow-hidden relative">

          {/* navigation bar */}
          <Navbar
            breadcrumbs={breadcrumbs}
            handleBack={goBack}
            handleClick={setView}
            hasHistory={history.length > 0}
          />

          {/* flash messages */}
          {flashMessages.length ? (
            <div className="flash-message-container">
              {flashMessages.map((fm) => fm.element)}
            </div>
          ) : null}

          {/* current view */}
          {view}
        </div>
      </div>
    </main>
  );
};


export default Dashboard;
