import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess, makeRequest } from "../../utils";
import {
  AudioTapDetails,
  Study,
  TapDetails,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { SmallLoader } from "../loader";
import SubjectsEdit from "./subjectsEdit";
import SubjectVisuals from "./subjectVisualsV2";
import { APP_ENV } from "../../environment";
import dataFactory from "../../dataFactory";
import Button from "../buttons/button";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import Link from "../links/link";
import CardContentRow from "../cards/cardHeader";
import Title from "../cards/cardTitle";
import Subtitle from "../cards/cardSubtilte";
import AdminView from "../containers/admin/adminView";
import AdminContent from "../containers/admin/adminContent";

/**
 * studyDetails: the details of the study that subjects will be listed for
 * getTaps: get tap data
 */
interface SubjectsProps extends ViewProps {
  studyDetails: Study;
  getTaps: () => TapDetails[];
  getAudioTaps: () => AudioTapDetails[];
}

const Subjects: React.FC<SubjectsProps> = (props) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [users, setUsers] = useState<UserDetails[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

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
    const create = getAccess(2, "Create", "Users", id)
      .then(() => setCanCreate(true))
      .catch(() => setCanCreate(false));

    // get whether the user can edit subjects
    const edit = getAccess(2, "Edit", "Users", id)
      .then(() => setCanEdit(true))
      .catch(() => setCanEdit(false));

    // get all of the study's users
    const url = `/aws/scan?app=2&key=User&query=user.userPermissionIdBEGINS"${dittiId}"`;
    let usersRequest;
    if (APP_ENV === "production") {
      usersRequest = makeRequest(url).then((users: User[]) => {
        const userDetails = users.map(user => ({
            tapPermission: user.tap_permission,
            userPermissionId: user.user_permission_id,
            expTime: user.exp_time,
            createdAt: user.createdAt,
            information: user.information,
            teamEmail: user.team_email
          }));
        setUsers(userDetails)
      });
    } else {
      usersRequest = new Promise<UserDetails[]>(
        resolve => resolve(dataFactory.users)
      ).then(setUsers);
    }

    // when all promises complete, hide the loader
    Promise.all([create, edit, usersRequest]).then(() => setLoading(false));

  }, [props.studyDetails]);

  const { flashMessage, goBack, handleClick, getTaps, getAudioTaps } = props;
  const { id, dittiId, email } = props.studyDetails;
  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  };

  const tableData: TableData[][] = users.map((user: UserDetails) => {
    return [
      {
        contents: (
          <>
            {/* if the user has tap permission, link to a subject visuals page */}
            {(user.tapPermission && canEdit) ? (
              <Link
                onClick={() =>
                  handleClick(
                    [user.userPermissionId],
                    <SubjectVisuals
                      flashMessage={flashMessage}
                      getTaps={getTaps}
                      getAudioTaps={getAudioTaps}
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
          <>
            {/* if the user can edit, link to the edit subject page */}
            {canEdit &&
              <Button
                variant="secondary"
                className="w-full h-full"
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
                }>
                  Edit
              </Button>
            }
          </>
        ),
        searchValue: "",
        sortValue: "",
        paddingX: 0,
        paddingY: 0,
      }
    ];
  });

  // if the user can enroll subjects, include an enroll button
  const tableControl = canCreate ? (
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
      }>
        Create +
    </Button>
  ) : (
    <React.Fragment />
  );

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
