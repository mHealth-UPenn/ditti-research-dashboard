import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess, makeRequest } from "../../utils";
import { Study, User, UserDetails, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";
import SubjectsEdit from "./subjectsEdit";
import SubjectVisuals from "./subjectVisualsV2";
import { APP_ENV } from "../../environment";
import Button from "../buttons/button";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import Link from "../links/link";
import Title from "../cards/cardTitle";
import Subtitle from "../cards/cardSubtilte";
import AdminView from "../containers/admin/adminView";
import AdminContent from "../containers/admin/adminContent";
import { useDittiDataContext } from "../../contexts/dittiDataContext";

/**
 * studyDetails: the details of the study that subjects will be listed for
 * getTaps: get tap data
 */
interface SubjectsProps extends ViewProps {
  studyDetails: Study;
}

const Subjects: React.FC<SubjectsProps> = (props) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canViewTaps, setCanViewTaps] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const { users } = useDittiDataContext();
  const filteredUsers = users.filter(
    u => u.userPermissionId.startsWith(props.studyDetails.dittiId)
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
    const { dittiId, id } = props.studyDetails;

    // get whether the user can enroll subjects
    const promises: Promise<any>[] = [];
    promises.push(
      getAccess(2, "Create", "Users", id)
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false))
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "Edit", "Users", id)
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
  }, [props.studyDetails]);

  const { flashMessage, goBack, handleClick } = props;
  const { id, dittiId, email } = props.studyDetails;
  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  };

  const tableData: TableData[][] = filteredUsers.map((user: UserDetails) => {
    return [
      {
        contents: (
          <>
            {/* if the user has tap permission, link to a subject visuals page */}
            {(user.tapPermission && canViewTaps) ? (
              <Link
                onClick={() =>
                  handleClick(
                    [user.userPermissionId],
                    <SubjectVisuals
                      flashMessage={flashMessage}
                      goBack={goBack}
                      handleClick={handleClick}
                      studyDetails={props.studyDetails}
                      user={user} />
                  )
                }>
                  {user.userPermissionId}
              </Link>
            ) : (
              user.userPermissionId
            )}
          </>
        ),
        searchValue: user.userPermissionId,
        sortValue: user.userPermissionId
      },
      {
        contents: (
          <span>
            {new Date(user.expTime).toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: user.expTime
      },
      {
        contents: (
          <span>
            {new Date(user.createdAt).toLocaleDateString("en-US", dateOptions)}
          </span>
        ),
        searchValue: "",
        sortValue: user.createdAt
      },
      {
        contents: (
          <span>{user.tapPermission ? "Yes" : "No"}</span>
        ),
        searchValue: "",
        sortValue: user.tapPermission ? "1" : "0"
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
                  ["Edit", user.userPermissionId],
                  <SubjectsEdit
                    dittiId={user.userPermissionId}
                    studyId={id}
                    studyEmail={email}
                    studyPrefix={dittiId}
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
            studyId={id}
            studyEmail={email}
            studyPrefix={dittiId}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick} />
        )
      }
      disabled={!(canCreate || APP_ENV === "demo")}>
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
    <AdminView>
      <AdminContent>
        <div className="flex flex-col mb-8">
          <Title>{props.studyDetails.name}</Title>
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
      </AdminContent>
    </AdminView>
  );
};

export default Subjects;
