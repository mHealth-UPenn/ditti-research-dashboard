import React, { useEffect, useState } from "react";
import { Study, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";
import StudySummary from "./studySummary";
import { sub } from "date-fns";
import AudioFileUpload from "./audioFileUpload";
import AudioFiles from "./audioFiles";
import Card from "../cards/card";
import ViewContainer from "../containers/viewContainer";
import CardContentRow from "../cards/cardContentRow";
import Button from "../buttons/button";
import Title from "../text/title";
import ActiveIcon from "../icons/activeIcon";
import Link from "../links/link";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { APP_ENV } from "../../environment";


const StudiesView: React.FC<ViewProps> = ({
  flashMessage,
  goBack,
  handleClick
}) => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [canViewAudioFiles, setCanViewAudioFiles] = useState(true);
  const [canCreateAudioFiles, setCanCreateAudioFiles] = useState(true);
  const [canViewTaps, setCanViewTaps] = useState<Set<number>>(new Set());

  const { taps, audioFiles } = useDittiDataContext();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // get all studies that the user has access to
        const promises: Promise<any>[] = [];
        promises.push(makeRequest("/db/get-studies?app=2").then(setStudies));

        // get all tap and audio file data
        promises.push(
          getAccess(2, "View", "Audio Files")
            .catch(() => setCanViewAudioFiles(false))
        );
        promises.push(
          getAccess(2, "Create", "Audio Files")
            .catch(() => setCanCreateAudioFiles(false))
        );

        // when all promises resolve, hide the loader
        Promise.all(promises).then(() => setLoading(false));
      } catch (error) {
        console.error("Error fetching data: ", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const updateCanViewTaps = async () => {
      const updatedCanViewTaps: Set<number> = new Set();
      const promises = studies.map(s => {
        return getAccess(2, "View", "Taps", s.id)
          .then(() => updatedCanViewTaps.add(s.id))
          .catch(() => updatedCanViewTaps.delete(s.id));
      });
      await Promise.all(promises)
      setCanViewTaps(updatedCanViewTaps)
    }
    updateCanViewTaps();
  }, [studies]);

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
          goBack={goBack}
          studyId={study.id}
        />
      );

      handleClick([study.acronym], view, false);
    }
  };

  const handleClickUploadAudioFile = () => handleClick(
    ["Audio File", "Upload"],
    <AudioFileUpload
      goBack={goBack}
      flashMessage={flashMessage}
      handleClick={handleClick}
    />
  );

  const handleClickViewAudioFiles = () => handleClick(
    ["Audio File"],
    <AudioFiles
      goBack={goBack}
      flashMessage={flashMessage}
      handleClick={handleClick}
    />
  );

  if (loading) {
    return (
      <ViewContainer>
        <Card width="md">
          <SmallLoader />
        </Card>
        <Card width="sm">
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <ViewContainer>
      <Card width="md">
        <CardContentRow>
          <Title>Studies</Title>
        </CardContentRow>
        {
          // for each study the user has access to
          studies.map((s) => {
            // count the number of taps that were recorded in the last 7 days
            const lastWeek = taps
              .filter(
                (t) =>
                  t.time > sub(new Date(), { weeks: 1 }) &&
                  t.dittiId.startsWith(s.dittiId)
              )
              .map((t) => t.dittiId)
              .filter((v, i, arr) => arr.indexOf(v) === i).length;

            // count the number of taps that were recorded in the last 24 hours
            const last24hrs = taps
              .filter(
                (t) =>
                  t.time > sub(new Date(), { days: 1 }) && // This should be 'days' not 'weeks'
                  t.dittiId.startsWith(s.dittiId)
              )
              .map((t) => t.dittiId)
              .filter((v, i, arr) => arr.indexOf(v) === i).length;

            return (
              <CardContentRow key={s.id} className="border-b border-light">
                <div className="flex items-start">
                  {/* active tapping icon */}
                  {canViewTaps.has(s.id) ?
                    <ActiveIcon active={!!lastWeek} className="mr-2" /> :
                    // Optimistic hydration
                    <ActiveIcon active={false} className="mr-2" />
                  }
                  {/* link to study summary */}
                  <div className="flex flex-col">
                    <Link onClick={() => handleClickStudy(s.id)}>
                      {s.acronym}
                    </Link>
                    <span className="text-sm">{s.name}</span>
                  </div>
                </div>

                {/* display the number of taps in the last 7 days and 24 hours */}
                <div className="flex whitespace-nowrap">
                  {canViewTaps.has(s.id) ?
                    <>
                      <div className="flex flex-col mr-2 font-bold">
                        <div>24 hours:</div>
                        <div>1 week:</div>
                      </div>
                      <div className="flex flex-col">
                        <div>{last24hrs} active subjects</div>
                        <div>{lastWeek} active subjects</div>
                      </div>
                    </> :
                    // Optimistic hydration
                    <>
                      <div className="flex flex-col mr-2 font-bold">
                        <div>24 hours:</div>
                        <div>1 week:</div>
                      </div>
                      <div className="flex flex-col">
                        <div>0 active subjects</div>
                        <div>0 active subjects</div>
                      </div>
                    </>
                  }
                </div>
              </CardContentRow>
            );
          })
        }
      </Card>

      {canViewAudioFiles &&
        <Card width="sm">
          <CardContentRow>
            <Title>Audio Files</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex">
              {(canCreateAudioFiles || APP_ENV === "demo") &&
                <Button
                  onClick={handleClickUploadAudioFile}
                  className="mr-2"
                  rounded={true}>
                    Upload +
                </Button>
              }
              <Button
                variant="secondary"
                onClick={handleClickViewAudioFiles}
                rounded={true}>
                  View all
              </Button>
            </div>
          </CardContentRow>
          <CardContentRow className="border-b border-light">
            <b>All files</b>
            <b>{audioFiles.length} files</b>
          </CardContentRow>
        </Card>
      }
    </ViewContainer>
  );
};

export default StudiesView;
