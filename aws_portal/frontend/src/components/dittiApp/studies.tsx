import React, { useEffect, useState } from "react";
import { AudioFile, AudioTapDetails, Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";
import StudySummary from "./studySummary";
import { sub } from "date-fns";
import AudioFileUpload from "./audioFileUpload";
import AudioFiles from "./audioFiles";

interface StudiesViewProps extends ViewProps {
  getTapsAsync: () => Promise<TapDetails[]>;
  getTaps: () => TapDetails[];
  getAudioTapsAsync: () => Promise<AudioTapDetails[]>;
  getAudioTaps: () => AudioTapDetails[];
  getAudioFilesAsync: () => Promise<AudioFile[]>;
  getAudioFiles: () => AudioFile[];
}

const StudiesView: React.FC<StudiesViewProps> = ({
  getTapsAsync,
  getTaps,
  getAudioTapsAsync,
  getAudioTaps,
  getAudioFilesAsync,
  getAudioFiles,
  flashMessage,
  goBack,
  handleClick
}) => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [users, setUsers] = useState<UserDetails[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // get all studies that the user has access to
        const studiesPromise = makeRequest("/db/get-studies?app=2").then(setStudies);
        const usersPromise = makeRequest("/aws/get-users?app=2").then(setUsers);

        // get all tap and audio file data
        const tapsPromise = getTapsAsync();
        const audioTapsPromise = getAudioTapsAsync();
        const audioFilesPromise = getAudioFilesAsync();

        // when all promises resolve, hide the loader
        Promise.all(
          [studiesPromise, tapsPromise, audioTapsPromise, usersPromise, audioFilesPromise]
        ).then(() => setLoading(false));
      } catch (error) {
        console.error("Error fetching data: ", error);
        setLoading(false);
      }
    };

    fetchData();
  }, [getTapsAsync, getAudioTapsAsync, getAudioFilesAsync]);

  /**
   * Handle when a user clicks on a study
   * @param id - the study's database primary key
   */
  const handleClickStudy = (id: number): void => {
    // get the study
    const study = studies.find((s) => s.id === id);

    if (study) {
      // set the view
      const view = (
        <StudySummary
          flashMessage={flashMessage}
          handleClick={handleClick}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          goBack={goBack}
          studyId={study.id}
        />
      );

      handleClick([study.acronym], view, false);
    }
  };

  const audioFileCard = (
    <div className="p-6 m-6 w-[24rem] bg-white shadow">
      <div className="card-title">Audio Files</div>
      {loading ? (
        <SmallLoader />
      ) : (
        <div>
          <div style={{ marginBottom: "1rem" }}>
            <button
              className="button-primary button-lg"
              onClick={() => handleClick(
                ["Audio File", "Upload"],
                <AudioFileUpload
                  goBack={goBack}
                  flashMessage={flashMessage}
                  handleClick={handleClick}
                />
              )}
              style={{ marginRight: "0.5rem" }}
            >
              Upload +
            </button>
            <button
              className="button-secondary button-lg"
              onClick={() => handleClick(
                ["Audio File"],
                <AudioFiles
                  goBack={goBack}
                  flashMessage={flashMessage}
                  handleClick={handleClick}
                />
              )}
            >
              View All
            </button>
          </div>
          <div>
            <div className="flex-space border-light-b" style={{ paddingBottom: "0.5rem" }}>
              <span><b>All files</b></span>
              <span><b>{getAudioFiles().length} files</b></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="flex flex-wrap p-6 max-h-[calc(calc(100vh-8rem)-1px)] overflow-scroll overflow-x-hidden">
      <div className="p-6 m-6 w-[36rem] bg-white shadow">
        <div className="text-xl font-bold mb-4">Studies</div>
        {loading ? (
          <SmallLoader />
        ) : (
          // for each study the user has access to
          studies.map((s) => {
            // count the number of taps that were recorded in the last 7 days
            const lastWeek = getTaps()
              .filter(
                (t) =>
                  t.time > sub(new Date(), { weeks: 1 }) &&
                  t.dittiId.startsWith(s.dittiId)
              )
              .map((t) => t.dittiId)
              .filter((v, i, arr) => arr.indexOf(v) === i).length;

            // count the number of taps that were recorded in the last 24 hours
            const last24hrs = getTaps()
              .filter(
                (t) =>
                  t.time > sub(new Date(), { days: 1 }) && // This should be 'days' not 'weeks'
                  t.dittiId.startsWith(s.dittiId)
              )
              .map((t) => t.dittiId)
              .filter((v, i, arr) => arr.indexOf(v) === i).length;

            return (
              <div key={s.id} className="border-light-b study-row">
                {/* active tapping icon */}
                <div
                  className={
                    "icon " + (last24hrs ? "icon-success" : "icon-gray")
                  }
                ></div>

                {/* link to study summary */}
                <div className="study-row-name">
                  <span
                    className="link"
                    onClick={() => handleClickStudy(s.id)}
                  >
                    {s.acronym}
                  </span>
                </div>

                {/* display the number of taps in the last 7 days and 24 hours */}
                <div className="study-row-summary">
                  <div className="study-row-summary-l">
                    <div>24 hours:</div>
                    <div>1 week:</div>
                  </div>
                  <div className="study-row-summary-r">
                    <div>{last24hrs} active subjects</div>
                    <div>{lastWeek} active subjects</div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
      {audioFileCard}
    </div>
  );
};

export default StudiesView;
