import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess } from "../../utils";
import { IStudySubjectDetails, Study, UserDetails, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";
import SubjectsEdit from "./subjectsEdit";
import SubjectVisuals from "./subjectVisualsV2";
import { APP_ENV } from "../../environment";
import Button from "../buttons/button";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import LinkComponent from "../links/linkComponent";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { Link, useSearchParams } from "react-router-dom";
import { useStudiesContext } from "../../contexts/studiesContext";


const Subjects = () => {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;

  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canViewTaps, setCanViewTaps] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  
  const { studiesLoading, getStudyById } = useStudiesContext();
  const { studySubjectLoading, studySubjects } = useCoordinatorStudySubjectContext();

  const study = getStudyById(studyId);
  const filteredStudySubjects = studySubjects.filter(
    ss => ss.dittiId.startsWith(study?.dittiId || "undefined")  // TODO: use regex instead
  );

  const columns: Column[] = [
    {
      name: "Ditti ID",
      searchable: true,
      sortable: true,
      width: 15
    },
    {
      name: "Expires On",
      searchable: false,
      sortable: true,
      width: 30
    },
    {
      name: "Created On",
      searchable: false,
      sortable: true,
      width: 30
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
    // get whether the user can enroll subjects
    const promises: Promise<any>[] = [];
    promises.push(
      getAccess(2, "Create", "Participants", studyId)
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false))
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "Edit", "Participants", studyId)
        .then(() => setCanEdit(true))
        .catch(() => setCanEdit(false))
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "View", "Taps", studyId)
        .then(() => setCanViewTaps(true))
        .catch(() => setCanViewTaps(false))
    );

    // when all promises complete, hide the loader
    Promise.all(promises).then(() => setLoading(false));
  }, []);

  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  };

  const tableData: TableData[][] = filteredStudySubjects.map((studySubject: IStudySubjectDetails) => {
    return [
      {
        contents: (
          <>
            {/* if the studySubject has tap permission, link to a subject visuals page */}
            {(studySubject.tapPermission && canViewTaps) ? (
              <Link to={`/coordinator/ditti/participants/view?dittiId=${studySubject.dittiId}&sid=${studyId}`}>
                <LinkComponent>
                  {studySubject.dittiId}
                </LinkComponent>
              </Link>
            ) : (
              studySubject.dittiId
            )}
          </>
        ),
        searchValue: studySubject.dittiId,
        sortValue: studySubject.dittiId
      },
      {
        contents: (
          <span>
            {new Date(studySubject.expTime).toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: studySubject.expTime
      },
      {
        contents: (
          <span>
            {new Date(studySubject.createdAt).toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: studySubject.createdAt
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
                  to={`/coordinator/ditti/participants/edit?dittiId=${studySubject.dittiId}&sid=${studyId}`}>
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
    <Link to={`/coordinator/ditti/participants/enroll?sid=${studyId}`}>
      <Button
        disabled={!(canCreate || APP_ENV === "demo")}
        rounded={true}>
          Create +
      </Button>
    </Link>

if (loading || studiesLoading || studySubjectLoading) {
  return (
    <ViewContainer>
      <Card>
        <SmallLoader />
      </Card>
    </ViewContainer>
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

export default Subjects;
