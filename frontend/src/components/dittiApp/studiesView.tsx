/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { useEffect, useState } from "react";
import { getAccess } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { sub } from "date-fns";
import { Card } from "../cards/card";
import { ViewContainer } from "../containers/viewContainer/viewContainer";
import { CardContentRow } from "../cards/cardContentRow";
import { Button } from "../buttons/button";
import { Title } from "../text/title";
import { ActiveIcon } from "../icons/activeIcon";
import { LinkComponent } from "../links/linkComponent";
import { useDittiData } from "../../hooks/useDittiData";
import { APP_ENV } from "../../environment";
import { Link } from "react-router-dom";
import { useStudies } from "../../hooks/useStudies";

export const StudiesView = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [canViewAudioFiles, setCanViewAudioFiles] = useState(true);
  const [canCreateAudioFiles, setCanCreateAudioFiles] = useState(true);
  const [canViewTaps, setCanViewTaps] = useState<Set<number>>(new Set());

  const { dataLoading, taps, audioFiles } = useDittiData();
  const { studiesLoading, studies } = useStudies();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // get all studies that the user has access to
        const promises: Promise<void>[] = [];

        // get all tap and audio file data
        promises.push(
          getAccess(2, "View", "Audio Files").catch(() => {
            setCanViewAudioFiles(false);
          })
        );
        promises.push(
          getAccess(2, "Create", "Audio Files").catch(() => {
            setCanCreateAudioFiles(false);
          })
        );

        // when all promises resolve, hide the loader
        await Promise.all(promises);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data: ", error);
        setLoading(false);
      }
    };

    void fetchData();
  }, []);

  useEffect(() => {
    const updateCanViewTaps = async () => {
      const updatedCanViewTaps = new Set<number>();
      const promises = studies.map((s) => {
        return getAccess(2, "View", "Taps", s.id)
          .then(() => updatedCanViewTaps.add(s.id))
          .catch(() => updatedCanViewTaps.delete(s.id));
      });
      await Promise.all(promises);
      setCanViewTaps(updatedCanViewTaps);
    };

    void updateCanViewTaps();
  }, [studies]);

  if (loading || studiesLoading || dataLoading) {
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
                  {canViewTaps.has(s.id) ? (
                    <ActiveIcon active={!!lastWeek} className="mr-2" />
                  ) : (
                    // Optimistic hydration
                    <ActiveIcon active={false} className="mr-2" />
                  )}
                  {/* link to study summary */}
                  <div className="flex flex-col">
                    <Link to={`/coordinator/ditti/study?sid=${String(s.id)}`}>
                      <LinkComponent>{s.acronym}</LinkComponent>
                    </Link>
                    <span className="text-sm">{s.name}</span>
                  </div>
                </div>

                {/* display the number of taps in the last 7 days and 24 hours */}
                <div className="flex whitespace-nowrap">
                  {canViewTaps.has(s.id) ? (
                    <>
                      <div className="mr-2 flex flex-col font-bold">
                        <div>24 hours:</div>
                        <div>1 week:</div>
                      </div>
                      <div className="flex flex-col">
                        <div>{last24hrs} active subjects</div>
                        <div>{lastWeek} active subjects</div>
                      </div>
                    </>
                  ) : (
                    // Optimistic hydration
                    <>
                      <div className="mr-2 flex flex-col font-bold">
                        <div>24 hours:</div>
                        <div>1 week:</div>
                      </div>
                      <div className="flex flex-col">
                        <div>0 active subjects</div>
                        <div>0 active subjects</div>
                      </div>
                    </>
                  )}
                </div>
              </CardContentRow>
            );
          })
        }
      </Card>

      {canViewAudioFiles && (
        <Card width="sm">
          <CardContentRow>
            <Title>Audio Files</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex">
              {(canCreateAudioFiles || APP_ENV === "demo") && (
                <Link to="/coordinator/ditti/audio/upload">
                  <Button className="mr-2" rounded={true}>
                    Upload +
                  </Button>
                </Link>
              )}
              <Link to="/coordinator/ditti/audio">
                <Button variant="secondary" rounded={true}>
                  View all
                </Button>
              </Link>
            </div>
          </CardContentRow>
          <CardContentRow className="border-b border-light">
            <b>All files</b>
            <b>{audioFiles.length} files</b>
          </CardContentRow>
        </Card>
      )}
    </ViewContainer>
  );
};
