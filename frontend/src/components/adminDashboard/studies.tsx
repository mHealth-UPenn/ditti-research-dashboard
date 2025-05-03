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

import React, { useState, useEffect } from "react"; // Removed useCallback
import { ResponseBody, Study } from "../../types/api";
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

const COLUMNS: Column[] = [
  { name: "Acronym", searchable: true, sortable: true, width: 10 },
  { name: "Name", searchable: true, sortable: true, width: 30 },
  { name: "Ditti ID", searchable: true, sortable: true, width: 10 },
  { name: "Email", searchable: true, sortable: true, width: 20 },
  {
    name: "Default Enrollment Period",
    searchable: false,
    sortable: true,
    width: 15,
  },
  { name: "QI", searchable: false, sortable: true, width: 5 },
  { name: "", searchable: false, sortable: false, width: 10 },
];

export const Studies = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [studies, setStudies] = useState<Study[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);

  // --- API Handlers ---
  const { safeRequest: safeFetchInitialData, isLoading: isLoadingData } =
    useApiHandler<{
      studies: Study[];
      permissions: { create: boolean; edit: boolean; archive: boolean };
    }>({
      errorMessage: "Failed to load studies or permissions.",
      showDefaultSuccessMessage: false,
    });

  const { safeRequest: safeArchive } = useApiHandler<ResponseBody>({
    successMessage: (data) => data.msg,
    errorMessage: (error) => `Failed to archive study: ${error.message}`,
    onSuccess: () => {
      setRefreshKey((prev) => prev + 1); // Trigger refresh
    },
  });
  // --------------------

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
        const createPerm = checkPermission(adminAppId, "Create", "Studies");
        const editPerm = checkPermission(adminAppId, "Edit", "Studies");
        const archivePerm = checkPermission(adminAppId, "Archive", "Studies");
        const studiesReq = httpClient.request<Study[]>("/admin/study?app=1");

        const [canCreateRes, canEditRes, canArchiveRes, studiesRes] =
          await Promise.all([createPerm, editPerm, archivePerm, studiesReq]);

        return {
          studies: studiesRes,
          permissions: {
            create: canCreateRes,
            edit: canEditRes,
            archive: canArchiveRes,
          },
        };
      });

      if (fetchedData) {
        setStudies(fetchedData.studies);
        setCanCreate(fetchedData.permissions.create);
        setCanEdit(fetchedData.permissions.edit);
        setCanArchive(fetchedData.permissions.archive);
      } else {
        // Reset state on error
        setStudies([]);
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
    return studies.map((s: Study) => {
      const { acronym, dittiId, email, id, name, defaultExpiryDelta, isQi } = s;
      return [
        {
          contents: <span>{acronym}</span>,
          searchValue: acronym,
          sortValue: acronym,
        },
        {
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name,
        },
        {
          contents: <span>{dittiId}</span>,
          searchValue: dittiId,
          sortValue: dittiId,
        },
        {
          contents: <span>{email}</span>,
          searchValue: email,
          sortValue: email,
        },
        {
          contents: <span>{defaultExpiryDelta} days</span>,
          searchValue: defaultExpiryDelta.toString(),
          sortValue: defaultExpiryDelta,
        },
        {
          contents: <span>{isQi ? "Yes" : "No"}</span>,
          searchValue: isQi ? "Yes" : "No",
          sortValue: isQi ? "Yes" : "No",
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
                    to={`/coordinator/admin/studies/edit?id=${String(id)}`}
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
                  onClick={() => void deleteStudy(id)}
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
  const deleteStudy = async (id: number) => {
    const msg = "Are you sure you want to archive this study?";
    if (!confirm(msg)) return;

    const body = { app: 1, id };

    await safeArchive(() =>
      httpClient.request<ResponseBody>("/admin/study/archive", {
        method: "POST",
        data: body,
      })
    );
  };

  const tableControl = canCreate ? (
    <Link to={`/coordinator/admin/studies/create`}>
      <Button variant="primary">Create +</Button>
    </Link>
  ) : (
    <React.Fragment />
  );

  const navbar = <AdminNavbar activeView="Studies" />;

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
          columns={COLUMNS}
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
