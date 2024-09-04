import * as React from "react";
import { useState, useEffect } from "react";
import { ResponseBody, Role, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import RolesEdit from "./rolesEdit";
import { SmallLoader } from "../loader";

const Roles: React.FC<ViewProps> = ({ flashMessage, goBack, handleClick }) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canArchive, setCanArchive] = useState<boolean>(false);
  const [roles, setRoles] = useState<Role[]>([]);
  const [columns] = useState<Column[]>([
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 15
    },
    {
      name: "Permissions",
      searchable: false,
      sortable: false,
      width: 75
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10
    }
  ]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      // check whether the user has permission to create
      const create = getAccess(1, "Create", "Roles")
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false));

      // check whether the user has permissions to edit
      const edit = getAccess(1, "Edit", "Roles")
        .then(() => setCanEdit(true))
        .catch(() => setCanEdit(false));

      // check whether the user has permissions to archive
      const archive = getAccess(1, "Archive", "Roles")
        .then(() => setCanArchive(true))
        .catch(() => setCanArchive(false));

      // get the table's data
      const rolesData = makeRequest("/admin/role?app=1").then((roles) => {
        setRoles(roles);
      });

      // when all requests are complete, hide the loading screen
      Promise.all([create, edit, archive, rolesData]).then(() => {
        setLoading(false);
      });
    };
    fetchData();
  }, []);

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    // iterate over the table's rows
    return roles.map((r: Role) => {
      const { id, name, permissions } = r;

      // map each row to a set of cells for each table column
      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {permissions
                  .map((p) => {
                    const action = p.action === "*" ? "All Actions" : p.action;
                    const resource =
                      p.resource === "*" ? "All Resources" : p.resource;
                    return action + " - " + resource;
                  })
                  .join(", ")}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: ""
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
                      <RolesEdit
                        roleId={id}
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
                  onClick={() => deleteRole(id)}
                >
                  Archive
                </button>
              ) : null}
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteRole = (id: number): void => {
    // prepare the request
    const body = { app: 1, id }; // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    // confirm deletion
    const msg = "Are you sure you want to archive this role?";

    if (confirm(msg))
      makeRequest("/admin/role/archive", opts)
        .then(handleSuccess)
        .catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    flashMessage(<span>{res.msg}</span>, "success");

    // show the loading screen
    setLoading(true);

    // refresh the table's data
    makeRequest("/admin/role?app=1").then((roles) => {
      setRoles(roles);
      setLoading(false);
    });
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message returned from the endpoint or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  // if the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <button
      className="button-primary"
      onClick={() =>
        handleClick(
          ["Create"],
          <RolesEdit
            roleId={0}
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick}
          />
        )
      }
    >
      Create&nbsp;<b>+</b>
    </button>
  ) : (
    <></>
  );

  return (
    <div className="page-container">
      <Navbar
        active="Roles"
        flashMessage={flashMessage}
        goBack={goBack}
        handleClick={handleClick}
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

export default Roles;
