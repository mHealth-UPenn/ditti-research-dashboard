/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { useState, useEffect } from "react";
import { ResponseBody, Role } from "../../types/api";
import { httpClient } from "../../lib/http";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AdminNavbar } from "./adminNavbar";
import { SmallLoader } from "../loader/loader";
import { Button } from "../buttons/button";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useApiHandler } from "../../hooks/useApiHandler";

export const Roles = () => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canEdit, setCanEdit] = useState<boolean>(false);
  const [canArchive, setCanArchive] = useState<boolean>(false);
  const [roles, setRoles] = useState<Role[]>([]);
  const [columns] = useState<Column[]>([
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 15,
    },
    {
      name: "Permissions",
      searchable: false,
      sortable: false,
      width: 75,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ]);
  const [refreshKey, setRefreshKey] = useState(0);

  const { safeRequest: safeFetchInitialData, isLoading: isLoadingData } =
    useApiHandler<{
      roles: Role[];
      permissions: { create: boolean; edit: boolean; archive: boolean };
    }>({
      errorMessage: "Failed to load roles or permissions.",
      showDefaultSuccessMessage: false,
    });

  const { safeRequest: safeArchive } = useApiHandler<ResponseBody>({
    successMessage: (data) => data.msg,
    errorMessage: (error) => `Failed to archive role: ${error.message}`,
    onSuccess: () => {
      setRefreshKey((prev) => prev + 1);
    },
  });

  useEffect(() => {
    const initialFetch = async () => {
      const fetchedData = await safeFetchInitialData(async () => {
        const checkPermission = async (
          appId: number,
          action: string,
          resource: string
        ): Promise<boolean> => {
          const url = `/auth/researcher/get-access?app=${String(appId)}&action=${action}&resource=${resource}`;
          try {
            const res = await httpClient.request<ResponseBody>(url);
            return res.msg === "Authorized";
          } catch {
            return false;
          }
        };

        const adminAppId = 1;
        const createPerm = checkPermission(adminAppId, "Create", "Roles");
        const editPerm = checkPermission(adminAppId, "Edit", "Roles");
        const archivePerm = checkPermission(adminAppId, "Archive", "Roles");
        const rolesReq = httpClient.request<Role[]>("/admin/role?app=1");

        const [canCreateRes, canEditRes, canArchiveRes, rolesRes] =
          await Promise.all([createPerm, editPerm, archivePerm, rolesReq]);

        return {
          roles: rolesRes,
          permissions: {
            create: canCreateRes,
            edit: canEditRes,
            archive: canArchiveRes,
          },
        };
      });

      if (fetchedData) {
        setRoles(fetchedData.roles);
        setCanCreate(fetchedData.permissions.create);
        setCanEdit(fetchedData.permissions.edit);
        setCanArchive(fetchedData.permissions.archive);
      } else {
        setRoles([]);
        setCanCreate(false);
        setCanEdit(false);
        setCanArchive(false);
      }
    };
    void initialFetch();
  }, [safeFetchInitialData, refreshKey]);

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
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name,
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
          sortValue: "",
        },
        {
          contents: (
            <div className="flex size-full">
              {canEdit && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full grow"
                  fullWidth={true}
                  fullHeight={true}
                >
                  <Link
                    className="flex size-full items-center justify-center"
                    to={`/coordinator/admin/roles/edit?id=${String(id)}`}
                  >
                    Edit
                  </Link>
                </Button>
              )}
              {canArchive && (
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full grow"
                  onClick={() => {
                    void deleteRole(id);
                  }}
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

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteRole = async (id: number) => {
    const body = { app: 1, id };
    const msg = "Are you sure you want to archive this role?";

    if (confirm(msg)) {
      await safeArchive(() =>
        httpClient.request<ResponseBody>("/admin/role/archive", {
          method: "POST",
          data: body,
        })
      );
    }
  };

  // if the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <Link to={`/coordinator/admin/roles/create`}>
      <Button variant="primary">Create +</Button>
    </Link>
  ) : (
    <></>
  );

  const navbar = <AdminNavbar activeView="Roles" />;

  if (isLoadingData) {
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
