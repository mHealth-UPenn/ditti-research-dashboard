/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
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


/**
 * @property {2 | 3} app - The app number (2 for Ditti, 3 for Wearable)
 */
interface ISubjectsContentProps {
  app: 2 | 3;
}


export const SubjectsContent = ({ app }: ISubjectsContentProps) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canViewTaps, setCanViewTaps] = useState<boolean>(false);
  const [canViewWearableData, setCanViewWearableData] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  
  const { studiesLoading, study } = useStudies();
  const { studySubjectLoading, studySubjects } = useCoordinatorStudySubjects();

  const appSlug = app === 2 ? "ditti" : "wearable";

  const filteredStudySubjects = studySubjects.filter(
    ss => ss.dittiId.startsWith(study?.dittiId || "undefined")
  );

  const columns: Column[] = [
    {
      name: "Ditti ID",
      searchable: true,
      sortable: true,
      width: 15
    },
    {
      name: "Ditti ID Expiry Date",
      searchable: false,
      sortable: true,
      width: 20
    },
    {
      name: "Enrollment Start Date",
      searchable: false,
      sortable: true,
      width: 20
    },
    {
      name: "Enrollment End Date",
      searchable: false,
      sortable: true,
      width: 20
    },
    {
      name: "Tapping",
      searchable: false,
      sortable: true,
      width: 15
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10
    }
  ];

  useEffect(() => {
    if (study) {
      const promises: Promise<void>[] = [];
      promises.push(
        getAccess(app, "Create", "Participants", study.id)
          .then(() => setCanCreate(true))
          .catch(() => setCanCreate(false))
      );

      promises.push(
        getAccess(app, "Edit", "Participants", study.id)
          .then(() => setCanEdit(true))
          .catch(() => setCanEdit(false))
      );

      promises.push(
        getAccess(app, "View", "Taps", study.id)
          .then(() => setCanViewTaps(true))
          .catch(() => setCanViewTaps(false))
      );

      promises.push(
        getAccess(app, "View", "Wearable Data", study.id)
          .then(() => setCanViewWearableData(true))
          .catch(() => setCanViewWearableData(false))
      );

      Promise.all(promises).then(() => setLoading(false));
    }
  }, [study]);

  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };

  const tableData: TableData[][] = filteredStudySubjects.map((studySubject: StudySubjectModel) => {
    const { startsOn, expiresOn } = getEnrollmentInfoForStudy(studySubject, study?.id);

    return [
      {
        contents: (
          <>
            {(app === 2 && studySubject.tapPermission && canViewTaps)
              ? <Link to={`/coordinator/ditti/participants/view?dittiId=${studySubject.dittiId}&sid=${study?.id}`}>
                  <LinkComponent>
                    {studySubject.dittiId}
                  </LinkComponent>
                </Link>
              : (studySubject.apis.length && canViewWearableData)
                ? <Link to={`/coordinator/wearable/participants/view?dittiId=${studySubject.dittiId}&sid=${study?.id}`}>
                    <LinkComponent>
                      {studySubject.dittiId}
                    </LinkComponent>
                  </Link>
                : studySubject.dittiId
            }
          </>
        ),
        searchValue: studySubject.dittiId,
        sortValue: studySubject.dittiId
      },
      {
        contents: (
          <span>
            {new Date(studySubject.dittiExpTime).toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: studySubject.dittiExpTime
      },
      {
        contents: (
          <span>
            {startsOn.toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: startsOn.toLocaleDateString("en-US", dateOptions)
      },
      {
        contents: (
          <span>
            {expiresOn.toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: expiresOn.toLocaleDateString("en-US", dateOptions)
      },
      {
        contents: (
          <span>{studySubject.tapPermission ? "Yes" : "No"}</span>
        ),
        searchValue: "",
        sortValue: studySubject.tapPermission ? "1" : "0"
      },
      {
        contents: (
          <div className="flex w-full h-full">
            {/* if the user can edit, link to the edit subject page */}
            <Button
              variant="secondary"
              size="sm"
              className="h-full flex-grow"
              disabled={!(canEdit || APP_ENV === "demo")}
              fullWidth={true}
              fullHeight={true}>
                <Link
                  className="w-full h-full flex items-center justify-center"
                  to={`/coordinator/${appSlug}/participants/edit?dittiId=${studySubject.dittiId}&sid=${study?.id}`}>
                    Edit
                </Link>
            </Button>
          </div>
        ),
        searchValue: "",
        sortValue: "",
        paddingX: 0,
        paddingY: 0,
      }
    ];
  });

  // if the user can enroll subjects, include an enroll button
  const tableControl =
    <Link to={`/coordinator/${appSlug}/participants/enroll?sid=${study?.id}`}>
      <Button
        disabled={!(canCreate || APP_ENV === "demo")}
        rounded={true}>
          Enroll +
      </Button>
    </Link>

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
        <div className="flex flex-col mb-8">
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
          sortDefault="" />
      </ListContent>
    </ListView>
  );
};
