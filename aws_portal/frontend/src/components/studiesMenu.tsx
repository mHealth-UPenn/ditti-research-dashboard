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
    <div className="bg-white studies-menu-container border-dark-r">
      <div className="studies-menu-header border-dark-b">
        <span>Studies</span>
      </div>
      <div className="studies-menu-content">
        {loading ? (
          <SmallLoader />
        ) : (
          <ul>
            {/* render a list of studies */}
            {studies.map((s: Study, i: number) => (
              <li
                key={i}
                className="link"
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
