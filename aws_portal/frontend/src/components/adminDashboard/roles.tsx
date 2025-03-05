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

import { useState, useEffect } from "react";
import { ResponseBody, Role } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import { SmallLoader } from "../loader";
import Button from "../buttons/button";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";

const Roles = () => {
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
  const { flashMessage } = useFlashMessageContext();

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
            <span>{name}</span>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
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
          ),
          searchValue: "",
          sortValue: ""
        },
        {
          contents: (
            <div className="flex w-full h-full">
              {canEdit &&
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  fullWidth={true}
                  fullHeight={true}>
                    <Link
                      className="w-full h-full flex items-center justify-center"
                      to={`/coordinator/admin/roles/edit?id=${id}`}>
                        Edit
                    </Link>
                </Button>
              }
              {canArchive &&
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() => deleteRole(id)}>
                    Archive
                </Button>
              }
            </div>
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
    <Link to={`/coordinator/admin/roles/create`}>
      <Button variant="primary">
          Create +
      </Button>
    </Link>
  ) : (
    <></>
  );

  const navbar = <Navbar activeView="Roles" />;

  if (loading) {
    return (
      <ListView>
        {navbar}
        <ListContent>
          <SmallLoader />
        </ListContent>
      </ListView>
    );
  }

  return (
    <ListView>
      {navbar}
      <ListContent>
        <Table
          columns={columns}
          control={tableControl}
          controlWidth={10}
          data={getData()}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault="" />
      </ListContent>
    </ListView>
  );
};

export default Roles;
