import * as React from "react";
import { useState, useEffect } from "react";
import { ResponseBody, Study, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import StudiesEdit from "./studiesEdit";
import { SmallLoader } from "../loader";
import Button from "../buttons/button";
import AdminView from "../containers/admin/adminView";
import AdminContent from "../containers/admin/adminContent";

const Studies: React.FC<ViewProps> = ({ flashMessage, goBack, handleClick }) => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [studies, setStudies] = useState<Study[]>([]);
  const [columns] = useState<Column[]>([
    { name: "Acronym", searchable: true, sortable: true, width: 10 },
    { name: "Name", searchable: true, sortable: true, width: 45 },
    { name: "Ditti ID", searchable: true, sortable: true, width: 10 },
    { name: "Email", searchable: true, sortable: true, width: 25 },
    { name: "", searchable: false, sortable: false, width: 10 }
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check create, edit, and archive permissions
        await Promise.all([
          getAccess(1, "Create", "Studies").then(() => setCanCreate(true)),
          getAccess(1, "Edit", "Studies").then(() => setCanEdit(true)),
          getAccess(1, "Archive", "Studies").then(() => setCanArchive(true)),
          makeRequest("/admin/study?app=1").then((data) => setStudies(data))
        ]);
      } catch (error) {
        console.error("Error fetching permissions or data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    return studies.map((s: Study) => {
      const { acronym, dittiId, email, id, name } = s;
      return [
        {
          contents: (
            <span>{acronym}</span>
          ),
          searchValue: acronym,
          sortValue: acronym
        },
        {
          contents: (
            <span>{name}</span>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <span>{dittiId}</span>
          ),
          searchValue: dittiId,
          sortValue: dittiId
        },
        {
          contents: (
            <span>{email}</span>
          ),
          searchValue: email,
          sortValue: email
        },
        {
          contents: (
            <>
              {canEdit &&
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() =>
                    handleClick(
                      ["Edit", acronym],
                      <StudiesEdit
                        studyId={id}
                        flashMessage={flashMessage}
                        goBack={goBack}
                        handleClick={handleClick} />
                    )
                  }>
                    Edit
                </Button>
              }
              {canArchive &&
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() => deleteStudy(id)}>
                    Archive
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
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteStudy = async (id: number) => {
    // Confirm deletion
    const msg = "Are you sure you want to archive this study?";
    if (!confirm(msg)) return;

    // Prepare and send the request
    const body = { app: 1, id }; // Admin Dashboard = 1
    await makeRequest("/admin/study/archive", { 
      method: "POST", 
      body: JSON.stringify(body) 
    }).then(handleSuccess).catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param id - the archived study id
   */
  const handleSuccess = async (id: number) => {
    flashMessage(<span>Study archived successfully.</span>, "success");

    // show the loading screen
    setLoading(true);

    // refresh the table's data
    makeRequest("/admin/study?app=1").then((studies) => {
      setStudies(studies);
      setLoading(false);
    });
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );
    flashMessage(msg, "danger");
  };

  const tableControl = canCreate ? (
    <Button
      variant="primary"
      onClick={() =>
        handleClick(
          ["Create"],
          <StudiesEdit
            studyId={0}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick}
          />
        )
      }>
        Create +
    </Button>
  ) : (
    <React.Fragment />
  )

  const navbar =
    <Navbar
      active="Studies"
      flashMessage={flashMessage}
      goBack={goBack}
      handleClick={handleClick} />

  if (loading) {
    return (
      <AdminView>
        {navbar}
        <AdminContent>
          <SmallLoader />
        </AdminContent>
      </AdminView>
    );
  }

  return (
    <AdminView>
      {navbar}
      <AdminContent>
        <Table
          columns={columns}
          control={tableControl}
          controlWidth={10}
          data={getData()}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault="" />
      </AdminContent>
    </AdminView>
  );
};

export default Studies;
