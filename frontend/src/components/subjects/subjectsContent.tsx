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
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { getAccess, getEnrollmentInfoForStudy } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { APP_ENV } from "../../environment";
import { Button } from "../buttons/button";
import { LinkComponent } from "../links/linkComponent";
import { Title } from "../text/title";
import { Subtitle } from "../text/subtitle";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { Link } from "react-router-dom";
import { useStudies } from "../../hooks/useStudies";
import { StudySubjectModel } from "../../types/models";
import { SubjectsContentProps } from "./subjects.types";

export const SubjectsContent = ({ app }: SubjectsContentProps) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canViewTaps, setCanViewTaps] = useState<boolean>(false);
  const [canViewWearableData, setCanViewWearableData] =
    useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const { studiesLoading, study } = useStudies();
  const { studySubjectLoading, studySubjects } = useCoordinatorStudySubjects();

  const appSlug = app === 2 ? "ditti" : "wearable";

  const filteredStudySubjects = studySubjects.filter((ss) =>
    ss.dittiId.startsWith(study?.dittiId ?? "undefined")
  );

  const columns: Column[] = [
    {
      name: "Ditti ID",
      searchable: true,
      sortable: true,
      width: 15,
    },
    {
      name: "Ditti ID Expiry Date",
      searchable: false,
      sortable: true,
      width: 20,
    },
    {
      name: "Enrollment Start Date",
      searchable: false,
      sortable: true,
      width: 20,
    },
    {
      name: "Enrollment End Date",
      searchable: false,
      sortable: true,
      width: 20,
    },
    {
      name: "Tapping",
      searchable: false,
      sortable: true,
      width: 15,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ];

  useEffect(() => {
    if (study) {
      const promises: Promise<void>[] = [];
      promises.push(
        getAccess(app, "Create", "Participants", study.id)
          .then(() => {
            setCanCreate(true);
          })
          .catch(() => {
            setCanCreate(false);
          })
      );

      promises.push(
        getAccess(app, "Edit", "Participants", study.id)
          .then(() => {
            setCanEdit(true);
          })
          .catch(() => {
            setCanEdit(false);
          })
      );

      promises.push(
        getAccess(app, "View", "Taps", study.id)
          .then(() => {
            setCanViewTaps(true);
          })
          .catch(() => {
            setCanViewTaps(false);
          })
      );

      promises.push(
        getAccess(app, "View", "Wearable Data", study.id)
          .then(() => {
            setCanViewWearableData(true);
          })
          .catch(() => {
            setCanViewWearableData(false);
          })
      );

      Promise.all(promises)
        .then(() => {
          setLoading(false);
        })
        .catch((error: unknown) => {
          console.error("Error checking access:", error);
          setLoading(false);
        });
    }
  }, [study, app]);

  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };

  const tableData: TableData[][] = filteredStudySubjects.map(
    (studySubject: StudySubjectModel) => {
      const { startsOn, expiresOn } = getEnrollmentInfoForStudy(
        studySubject,
        study?.id
      );

      return [
        {
          contents: (
            <>
              {app === 2 && studySubject.tapPermission && canViewTaps ? (
                <Link
                  to={`/coordinator/ditti/participants/view?dittiId=${studySubject.dittiId}&sid=${String(study?.id)}`}
                >
                  <LinkComponent>{studySubject.dittiId}</LinkComponent>
                </Link>
              ) : studySubject.apis.length && canViewWearableData ? (
                <Link
                  to={`/coordinator/wearable/participants/view?dittiId=${studySubject.dittiId}&sid=${String(study?.id)}`}
                >
                  <LinkComponent>{studySubject.dittiId}</LinkComponent>
                </Link>
              ) : (
                studySubject.dittiId
              )}
            </>
          ),
          searchValue: studySubject.dittiId,
          sortValue: studySubject.dittiId,
        },
        {
          contents: (
            <span>
              {new Date(studySubject.dittiExpTime).toLocaleDateString(
                "en-US",
                dateOptions
              )}
            </span>
          ),
          searchValue: "",
          sortValue: studySubject.dittiExpTime,
        },
        {
          contents: (
            <span>{startsOn.toLocaleDateString("en-US", dateOptions)}</span>
          ),
          searchValue: "",
          sortValue: startsOn.toLocaleDateString("en-US", dateOptions),
        },
        {
          contents: (
            <span>{expiresOn.toLocaleDateString("en-US", dateOptions)}</span>
          ),
          searchValue: "",
          sortValue: expiresOn.toLocaleDateString("en-US", dateOptions),
        },
        {
          contents: <span>{studySubject.tapPermission ? "Yes" : "No"}</span>,
          searchValue: "",
          sortValue: studySubject.tapPermission ? "1" : "0",
        },
        {
          contents: (
            <div className="flex size-full">
              {/* if the user can edit, link to the edit subject page */}
              <Button
                variant="secondary"
                size="sm"
                className="h-full grow"
                disabled={!(canEdit || APP_ENV === "demo")}
                fullWidth={true}
                fullHeight={true}
              >
                <Link
                  className="flex size-full items-center justify-center"
                  to={`/coordinator/${appSlug}/participants/edit?dittiId=${studySubject.dittiId}&sid=${String(study?.id)}`}
                >
                  Edit
                </Link>
              </Button>
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
        },
      ];
    }
  );

  // if the user can enroll subjects, include an enroll button
  const tableControl = (
    <Link
      to={`/coordinator/${appSlug}/participants/enroll?sid=${String(study?.id)}`}
    >
      <Button disabled={!(canCreate || APP_ENV === "demo")} rounded={true}>
        Enroll +
      </Button>
    </Link>
  );

  if (loading || studiesLoading || studySubjectLoading) {
    return (
      <ListView>
        <ListContent>
          <SmallLoader />
        </ListContent>
      </ListView>
    );
  }

  return (
    <ListView>
      <ListContent>
        <div className="mb-8 flex flex-col">
          <Title>{study?.name}</Title>
          <Subtitle>All subjects</Subtitle>
        </div>
        <Table
          columns={columns}
          control={tableControl}
          controlWidth={10}
          data={tableData}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault=""
        />
      </ListContent>
    </ListView>
  );
};
