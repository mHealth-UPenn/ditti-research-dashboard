import React, { useState, useEffect } from "react";
import Navbar from "./navbar";
import Table, { Column, TableData } from "../table/table";
import AccessGroupsEdit from "./accessGroupsEdit";
import { AccessGroup, ResponseBody, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";

const AccessGroups: React.FC<ViewProps> = ({ flashMessage, goBack, handleClick }) => {
  // State
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [accessGroups, setAccessGroups] = useState<AccessGroup[]>([]);
  const [loading, setLoading] = useState(true);

  const columns: Column[] = [
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 20,
    },
    {
      name: "App",
      searchable: true,
      sortable: true,
      width: 20,
    },
    {
      name: "Permissions",
      searchable: false,
      sortable: false,
      width: 50,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ];

  useEffect(() => {
    // Check user permissions and fetch data on component mount
    const fetchData = async () => {
      try {
        await getAccess(1, "Create", "Access Groups");
        setCanCreate(true);
      } catch {
        setCanCreate(false);
      }

      try {
        await getAccess(1, "Edit", "Access Groups");
        setCanEdit(true);
      } catch {
        setCanEdit(false);
      }

      try {
        await getAccess(1, "Archive", "Access Groups");
        setCanArchive(true);
      } catch {
        setCanArchive(false);
      }

      try {
        const accessGroups = await makeRequest("/admin/access-group?app=1");
        setAccessGroups(accessGroups);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getData = (): TableData[][] => {
    // Iterate over the table's rows
    return accessGroups.map((ag: AccessGroup) => {
      const { app, id, name, permissions } = ag;

      // Map each row to a set of cells for each table column
      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: name,
          sortValue: name,
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{app.name}</span>
            </div>
          ),
          searchValue: app.name,
          sortValue: app.name,
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {permissions
                  .map(
                    (p) =>
                      (p.action == "*" ? "All Actions" : p.action) +
                      " - " +
                      (p.resource == "*" ? "All Resources" : p.resource)
                  )
                  .join(", ")}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: "",
        },
        {
          contents: (
            <div className="flex-left table-control">
              {canEdit ? (
                <button
                  className="button-secondary"
                  onClick={() =>
                    handleClick(
                      ["Edit", name],
                      <AccessGroupsEdit
                        accessGroupId={id}
                        flashMessage={flashMessage}
                        goBack={goBack}
                        handleClick={handleClick}
                      />
                    )
                  }
                >
                  Edit
                </button>
              ) : null}
              {canArchive ? (
                <button
                  className="button-danger"
                  onClick={() => deleteAccessGroup(id)}
                >
                  Archive
                </button>
              ) : null}
            </div>
          ),
          searchValue: "",
          sortValue: "",
        },
      ];
    });
  };

  const deleteAccessGroup = (id: number) => {
    // Prepare the request
    const body = { app: 1, id }; // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    // Confirm deletion
    const msg = "Are you sure you want to archive this access group?";
    if (confirm(msg)) {
      makeRequest("/admin/access-group/archive", opts)
        .then(handleSuccess)
        .catch(handleFailure);
    }
  };

  const handleSuccess = (res: ResponseBody) => {
    flashMessage(<span>{res.msg}</span>, "success");
    setLoading(true);

    // Refresh the table's data
    makeRequest("/admin/access-group?app=1").then((accessGroups) => {
      setAccessGroups(accessGroups);
      setLoading(false);
    });
  };

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

  // If the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <button
      className="button-primary"
      onClick={() =>
        handleClick(
          ["Create"],
          <AccessGroupsEdit
            accessGroupId={0}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick}
          />
        )
      }
    >
      Create&nbsp;<b>+</b>
    </button>
  ) : <React.Fragment />;

  return (
    <div className="page-container">
      <Navbar
        handleClick={handleClick}
        active="Access Groups"
        flashMessage={flashMessage}
        goBack={goBack}
      />
      <div className="page-content bg-white">
        {loading ? (
          <SmallLoader />
        ) : (
          <Table
            columns={columns}
            control={tableControl}
            controlWidth={10}
            data={getData()}
            includeControl={true}
            includeSearch={true}
            paginationPer={10}
            sortDefault=""
          />
        )}
      </div>
    </div>
  );
};

export default AccessGroups;
