import React, { createRef, useEffect, useState } from "react";
import { AudioTapDetails, Study, TapDetails, ViewProps } from "../interfaces";
import { makeRequest } from "../utils";
import StudySummary from "./dittiApp/studySummary";
import { SmallLoader } from "./loader";
import "./studiesMenu.css";
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';


/**
 * getTaps: get tap data
 * setView: set the current view
 */
interface StudiesMenuProps extends ViewProps {
  getTaps: () => TapDetails[];
  getAudioTaps: () => AudioTapDetails[];
  setView: (name: string, view: React.ReactElement) => void;
}

const StudiesMenu: React.FC<StudiesMenuProps> = ({
  flashMessage,
  handleClick,
  getTaps,
  getAudioTaps,
  goBack,
  setView,
}) => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const drawerRef = createRef<HTMLDivElement>();

  useEffect(() => {
    // get the studies that the user has access to
    makeRequest("/db/get-studies?app=2").then((studies: Study[]) => {
      setStudies(studies);
      setLoading(false);
    });
  }, []);

  const handleClickMenu = () => {
    if (drawerRef.current) {
      drawerRef.current.style.width = "16rem";
      drawerRef.current.style.padding = "2rem";
      setDrawerOpen(true);
    }
  };

  const handleClickClose = () => {
    if (drawerRef.current) {
      drawerRef.current.style.width = "0";
      drawerRef.current.style.padding = "0";
      setDrawerOpen(false);
    }
  };

  const studiesList = (
    <ul className="m-0 p-0 list-none">
      {/* render a list of studies */}
      {studies.map((s: Study, i: number) => (
        <li
          key={i}
          className="mb-4 text-[#666699] cursor-pointer underline"
          id={"study-menu-" + s.id}
          onClick={() =>
            setView(
              s.acronym,
              <StudySummary
                flashMessage={flashMessage}
                handleClick={handleClick}
                getTaps={getTaps}
                getAudioTaps={getAudioTaps}
                goBack={goBack}
                studyId={s.id}
              />
            )
          }
        >
          {s.acronym}
        </li>
      ))}
    </ul>
  );

  return (
    <div className="bg-white flex flex-col flex-shrink-0 border-r border-solid border-[#33334D] w-16 xl:w-64">
      <div className="flex items-center font-bold h-16 xl:pl-8 border-b border-solid border-[#33334D]">
        <div className="flex flex-grow items-center justify-center h-full cursor-pointer xl:hidden" onClick={drawerOpen ? handleClickClose : handleClickMenu}>
          {drawerOpen ? <CloseIcon /> : <MenuIcon />}
        </div>
        <span className="hidden xl:block">Studies</span>
      </div>
      <div className="p-8 hidden xl:flex">
        {loading ? <SmallLoader /> : studiesList}
      </div>
      <div ref={drawerRef} className="w-0 overflow-hidden p-0 flex flex-col bg-white z-10 flex-grow border-r border-solid border-[#33334D]">
        <span className="mb-4 font-bold">Studies</span>
        {loading ? <SmallLoader /> : studiesList}
      </div>
    </div>
  );
};

export default StudiesMenu;
