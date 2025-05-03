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

import { useState, useEffect, useCallback } from "react";
import { getAccess } from "../../utils";
import { httpClient } from "../../lib/http";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AdminNavbar } from "./adminNavbar";
import { SmallLoader } from "../loader/loader";
import { Button } from "../buttons/button";
import { AsyncButton } from "../buttons/asyncButton";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useApiHandler } from "../../hooks/useApiHandler";
import { AboutSleepTemplate, ResponseBody } from "../../types/api";

export const AboutSleepTemplates = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<
    AboutSleepTemplate[]
  >([]);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  const { flashMessage } = useFlashMessages();

  /**
   * Fetches the latest templates and updates the state.
   */
  const refreshTemplates = useCallback(async () => {
    try {
      const templates = await httpClient.request<AboutSleepTemplate[]>(
        "/admin/about-sleep-template?app=1"
      );
      setAboutSleepTemplates(templates);
    } catch (error) {
      console.error("Failed to refresh templates:", error);
      flashMessage(
        <span>
          <b>Error refreshing template list.</b>
        </span>,
        "danger"
      );
    }
  }, [flashMessage]);

  // API Handler for the archive operation
  const { safeRequest: safeArchiveRequest, isLoading } =
    useApiHandler<ResponseBody>({
      onSuccess: async (res) => {
        flashMessage(<span>{res.msg}</span>, "success");
        await refreshTemplates(); // Refresh list after successful archive
      },
      // onError is handled by the default hook implementation (shows flash message)
    });

  const columns: Column[] = [
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 90,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ];

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        // Check permissions required for this view
        const canCreatePromise = getAccess(1, "Create", "About Sleep Templates")
          .then(() => {
            if (isMounted) setCanCreate(true);
          })
          .catch(() => {
            if (isMounted) setCanCreate(false);
          });
        const canEditPromise = getAccess(1, "Edit", "About Sleep Templates")
          .then(() => {
            if (isMounted) setCanEdit(true);
          })
          .catch(() => {
            if (isMounted) setCanEdit(false);
          });
        const canArchivePromise = getAccess(
          1,
          "Archive",
          "About Sleep Templates"
        )
          .then(() => {
            if (isMounted) setCanArchive(true);
          })
          .catch(() => {
            if (isMounted) setCanArchive(false);
          });

        // Fetch the initial list of templates
        const fetchTemplatesPromise = refreshTemplates();

        // Wait for all initial setup operations
        await Promise.all([
          canCreatePromise,
          canEditPromise,
          canArchivePromise,
          fetchTemplatesPromise,
        ]);
      } catch (error) {
        console.error("Error during initial data fetch:", error);
        if (isMounted) {
          flashMessage(<span>Failed to load initial data.</span>, "danger");
        }
      } finally {
        if (isMounted) {
          setInitialLoadComplete(true);
        }
      }
    };

    void fetchData(); // Fire off the async function

    // Cleanup function to prevent state updates if component unmounts
    return () => {
      isMounted = false;
    };
  }, [flashMessage, refreshTemplates]);

  /**
   * Prepares template data for the Table component.
   * @returns An array of rows, where each row is an array of TableData objects.
   */
  const getData = (): TableData[][] => {
    return aboutSleepTemplates.map((s: AboutSleepTemplate) => {
      const { id, name } = s;

      // map each row to a set of cells for each table column
      return [
        {
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name,
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
                    to={`/coordinator/admin/about-sleep-templates/edit?id=${String(id)}`}
                  >
                    Edit
                  </Link>
                </Button>
              )}
              {canArchive && (
                // AsyncButton handles its own loading state for the archive action
                <AsyncButton
                  variant="danger"
                  size="sm"
                  className="h-full grow"
                  onClick={() => deleteTemplate(id)}
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
   * Archives a template using the API handler.
   * @param id - the entry's database primary key
   */
  const deleteTemplate = (id: number): Promise<void> => {
    const msg = "Are you sure you want to archive this about sleep template?";
    if (confirm(msg)) {
      // Use the safeRequest from the hook for archiving and return the promise chain
      return safeArchiveRequest(async () => {
        const body = { app: 1, id };
        return httpClient.request<ResponseBody>(
          "/admin/about-sleep-template/archive",
          {
            method: "POST",
            data: body,
          }
        );
      }).then(() => undefined); // Adapt return type for AsyncButton
    }
    // If confirm is false, return a resolved promise to satisfy AsyncButton type
    return Promise.resolve();
  };

  // if the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <Link to={`/coordinator/admin/about-sleep-templates/create`}>
      <Button variant="primary">Create +</Button>
    </Link>
  ) : (
    <></>
  );

  const navbar = <AdminNavbar activeView="About Sleep Templates" />;

  // Show loader until initial permissions and data are fetched
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
        {/* Relative container for the loading overlay */}
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
          {/* Archive operation loading overlay */}
          {isLoading && (
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
