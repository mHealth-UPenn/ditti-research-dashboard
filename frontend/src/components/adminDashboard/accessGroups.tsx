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

import React, { useState, useEffect, useCallback } from "react";
import { AdminNavbar } from "./adminNavbar";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AccessGroup, ResponseBody } from "../../types/api";
import { getAccess } from "../../utils";
import { httpClient } from "../../lib/http";
import { SmallLoader } from "../loader/loader";
import { Button } from "../buttons/button";
import { AsyncButton } from "../buttons/asyncButton";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useApiHandler } from "../../hooks/useApiHandler";

/**
 * Component to display and manage Access Groups in the Admin Dashboard.
 */
export const AccessGroups = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [accessGroups, setAccessGroups] = useState<AccessGroup[]>([]);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  const { flashMessage } = useFlashMessages();

  /**
   * Fetches the latest access groups and updates the state.
   */
  const refreshAccessGroups = useCallback(async () => {
    try {
      const response = await httpClient.request<AccessGroup[]>(
        "/admin/access-group?app=1"
      );
      setAccessGroups(response);
    } catch (error) {
      // Handle refresh-specific errors (e.g., show flash message)
      console.error("Failed to refresh access groups:", error);
      flashMessage(
        <span>
          <b>Error refreshing access group list.</b>
        </span>,
        "danger"
      );
      // Consider setting accessGroups to [] or other error state handling
    }
  }, [flashMessage]);

  // API Handler for the archive operation
  const { safeRequest: safeArchiveRequest, isLoading: isArchiving } =
    useApiHandler<ResponseBody>({
      onSuccess: async (res) => {
        flashMessage(<span>{res.msg}</span>, "success");
        await refreshAccessGroups(); // Refresh list after successful archive
      },
      // Default error handling (flash message) from hook is sufficient
    });

  // Definition of columns for the Table component
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

  // Effect hook to fetch initial permissions and access group list on mount
  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        // Check permissions concurrently
        const createPromise = getAccess(1, "Create", "Access Groups")
          .then(() => {
            if (isMounted) setCanCreate(true);
          })
          .catch(() => {
            if (isMounted) setCanCreate(false);
          });
        const editPromise = getAccess(1, "Edit", "Access Groups")
          .then(() => {
            if (isMounted) setCanEdit(true);
          })
          .catch(() => {
            if (isMounted) setCanEdit(false);
          });
        const archivePromise = getAccess(1, "Archive", "Access Groups")
          .then(() => {
            if (isMounted) setCanArchive(true);
          })
          .catch(() => {
            if (isMounted) setCanArchive(false);
          });

        // Fetch initial access groups using the refresh function
        const groupsPromise = refreshAccessGroups();

        // Wait for all initial fetches
        await Promise.all([
          createPromise,
          editPromise,
          archivePromise,
          groupsPromise,
        ]);
      } catch (error) {
        // Catch errors from Promise.all or initial setup if any
        console.error("Error during initial data load:", error);
        if (isMounted) {
          flashMessage(<span>Failed to load initial data.</span>, "danger");
        }
      } finally {
        if (isMounted) {
          setInitialLoadComplete(true);
        }
      }
    };

    void fetchData();

    // Cleanup function to prevent state updates on unmounted component
    return () => {
      isMounted = false;
    };
  }, [refreshAccessGroups, flashMessage]);

  /**
   * Prepares access group data for the Table component.
   * @returns {TableData[][]} Array of rows for the table.
   */
  const getData = (): TableData[][] => {
    // Iterate over the access groups to create table rows
    return accessGroups.map((ag: AccessGroup) => {
      const { app, id, name, permissions } = ag;

      // Map each access group to an array of cell data objects
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
                    to={`/coordinator/admin/access-groups/edit?id=${String(id)}`}
                  >
                    Edit
                  </Link>
                </Button>
              )}
              {canArchive && (
                <AsyncButton
                  variant="danger"
                  size="sm"
                  className="h-full grow"
                  onClick={() => deleteAccessGroup(id)}
                >
                  Archive
                </AsyncButton>
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
   * Archives an access group using the API handler.
   * Confirms with the user before proceeding.
   * Required to return Promise<void> for AsyncButton.
   * @param id - The ID of the access group to archive.
   */
  const deleteAccessGroup = (id: number): Promise<void> => {
    const msg = "Are you sure you want to archive this access group?";

    if (confirm(msg)) {
      return safeArchiveRequest(async () => {
        const body = { app: 1, id };
        return httpClient.request<ResponseBody>("/admin/access-group/archive", {
          method: "POST",
          data: body,
        });
      }).then(() => undefined); // Adapt return type for AsyncButton
    }
    // Return resolved promise if user cancels confirmation (for AsyncButton)
    return Promise.resolve();
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

  // Show loader during initial page load (permissions + data fetch)
  if (!initialLoadComplete) {
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
        {/* Container for the table and potential loading overlay */}
        <div className="relative">
          {" "}
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
          {/* Show overlay loader when the archive operation is in progress */}
          {isArchiving && (
            <div
              className="absolute inset-0 z-10 flex items-center justify-center
                bg-white/75"
            >
              <SmallLoader />
            </div>
          )}
        </div>
      </ListContent>
    </ListView>
  );
};
