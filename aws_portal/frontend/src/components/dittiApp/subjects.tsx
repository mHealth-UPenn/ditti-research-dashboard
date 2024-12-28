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
import Link from "../links/linkComponent";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";

/**
 * studyDetails: the details of the study that subjects will be listed for
 * getTaps: get tap data
 */
interface SubjectsProps extends ViewProps {
  studyDetails: Study;
}

const Subjects = ({
  studyDetails,
  flashMessage,
  goBack,
  handleClick,
}: SubjectsProps) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canViewTaps, setCanViewTaps] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const { studySubjects } = useCoordinatorStudySubjectContext();
  const filteredStudySubjects = studySubjects.filter(
    u => u.dittiId.startsWith(studyDetails.dittiId)
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
    const { dittiId, id } = studyDetails;

    // get whether the user can enroll subjects
    const promises: Promise<any>[] = [];
    promises.push(
      getAccess(2, "Create", "Participants", id)
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false))
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "Edit", "Participants", id)
        .then(() => setCanEdit(true))
        .catch(() => setCanEdit(false))
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "View", "Taps", id)
        .then(() => setCanViewTaps(true))
        .catch(() => setCanViewTaps(false))
    );

    // when all promises complete, hide the loader
    Promise.all(promises).then(() => setLoading(false));
  }, [studyDetails]);

  const { id, dittiId, email } = studyDetails;
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
              <Link
                onClick={() =>
                  handleClick(
                    [studySubject.dittiId],
                    <SubjectVisuals
                      flashMessage={flashMessage}
                      goBack={goBack}
                      handleClick={handleClick}
                      studyDetails={studyDetails}
                      studySubject={studySubject} />
                  )
                }>
                  {studySubject.dittiId}
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
              onClick={() =>
                handleClick(
                  ["Edit", studySubject.dittiId],
                  <SubjectsEdit
                    dittiId={studySubject.dittiId}
                    studyDetails={studyDetails}
                    flashMessage={flashMessage}
                    goBack={goBack}
                    handleClick={handleClick} />
                )
              }
              disabled={!(canEdit || APP_ENV === "demo")}>
                Edit
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
    <Button
      onClick={() =>
        handleClick(
          ["Create"],
          <SubjectsEdit
            dittiId=""
            studyDetails={studyDetails}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick} />
        )
      }
      disabled={!(canCreate || APP_ENV === "demo")}
      rounded={true}>
        Create +
    </Button>

  if (loading) {
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
          <Title>{studyDetails.name}</Title>
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
