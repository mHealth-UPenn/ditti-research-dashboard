import React, { useEffect, useState } from "react";
import { Study, TapDetails, ViewProps } from "../interfaces";
import { makeRequest } from "../utils";
import StudySummary from "./dittiApp/studySummary";
import { SmallLoader } from "./loader";
import "./studiesMenu.css";

/**
 * getTaps: get tap data
 * setView: set the current view
 */
interface StudiesMenuProps extends ViewProps {
  getTaps: () => TapDetails[];
  setView: (name: string, view: React.ReactElement) => void;
}

const StudiesMenu: React.FC<StudiesMenuProps> = ({
  flashMessage,
  handleClick,
  getTaps,
  goBack,
  setView,
}) => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // get the studies that the user has access to
    makeRequest("/db/get-studies?app=2").then((studies: Study[]) => {
      setStudies(studies);
      setLoading(false);
    });
  }, []);

  return (
    <div className="bg-white flex flex-col flex-shrink-0 w-64 border-r border-solid border-[#33334D]">
      <div className="flex items-center font-bold h-16 pl-8 border-b border-solid border-[#33334D]">
        <span>Studies</span>
      </div>
      <div className="p-8">
        {loading ? (
          <SmallLoader />
        ) : (
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
        )}
      </div>
    </div>
  );
};

export default StudiesMenu;
