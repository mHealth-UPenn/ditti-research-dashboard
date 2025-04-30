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

import React, { useState, useEffect } from "react";
import { AdminNavbar } from "./adminNavbar";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AccessGroup, ResponseBody } from "../../types/api";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { Button } from "../buttons/button";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";

export const AccessGroups = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [accessGroups, setAccessGroups] = useState<AccessGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const { flashMessage } = useFlashMessages();

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
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name,
        },
        {
          contents: <span>{app.name}</span>,
          searchValue: app.name,
          sortValue: app.name,
        },
        {
          contents: (
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
          ),
          searchValue: "",
          sortValue: "",
        },
        {
          contents: (
            <div className="flex h-full w-full">
              {canEdit && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  fullWidth={true}
                  fullHeight={true}
                >
                  <Link
                    className="flex h-full w-full items-center justify-center"
                    to={`/coordinator/admin/access-groups/edit?id=${id}`}
                  >
                    Edit
                  </Link>
                </Button>
              )}
              {canArchive && (
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() => deleteAccessGroup(id)}
                >
                  Archive
                </Button>
              )}
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
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
    <Link to={`/coordinator/admin/access-groups/create`}>
      <Button variant="primary">Create +</Button>
    </Link>
  ) : (
    <React.Fragment />
  );

  const navbar = <AdminNavbar activeView="Access Groups" />;

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
          sortDefault=""
        />
      </ListContent>
    </ListView>
  );
};
