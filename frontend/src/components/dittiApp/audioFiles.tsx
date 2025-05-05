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

import { useEffect, useState } from "react";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { httpClient } from "../../lib/http";
import { Button } from "../buttons/button";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { APP_ENV } from "../../environment";
import { Link } from "react-router-dom";
import { useDittiData } from "../../hooks/useDittiData";
import { ResponseBody } from "../../types/api";
import { useApiHandler } from "../../hooks/useApiHandler";

export const AudioFiles = () => {
  const [canCreateAudioFiles, setCanCreateAudioFiles] =
    useState<boolean>(false);
  const [canDeleteAudioFiles, setCanDeleteAudioFiles] =
    useState<boolean>(false);

  const { dataLoading, audioFiles, refreshAudioFiles } = useDittiData();

  // Handler for deleting audio files
  const { safeRequest: safeDelete, isLoading: isDeleting } =
    useApiHandler<ResponseBody>({
      successMessage: "Audio file deleted successfully.", // Assuming success
      errorMessage: (error) => `Failed to delete audio file: ${error.message}`,
      onSuccess: async () => {
        await refreshAudioFiles(); // Refresh data via context hook
      },
    });

  const columns: Column[] = [
    {
      name: "Title",
      searchable: true,
      sortable: true,
      width: 20,
    },
    {
      name: "Category",
      searchable: true,
      sortable: true,
      width: 20,
    },
    {
      name: "Availability",
      searchable: false,
      sortable: true,
      width: 20,
    },
    {
      name: "Studies",
      searchable: true,
      sortable: true,
      width: 20,
    },
    {
      name: "Length",
      searchable: false,
      sortable: false,
      width: 10,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ];

  useEffect(() => {
    let isMounted = true; // Prevent state updates on unmounted component
    // Fetch permissions on mount
    const checkPermissions = async () => {
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

      try {
        const dittiAppId = 2; // Ditti App = 2
        const createPerm = checkPermission(dittiAppId, "Create", "Audio Files"); // Check correct resource name if needed
        const deletePerm = checkPermission(dittiAppId, "Delete", "Audio Files");

        const [canCreate, canDelete] = await Promise.all([
          createPerm,
          deletePerm,
        ]);
        if (isMounted) {
          setCanCreateAudioFiles(canCreate);
          setCanDeleteAudioFiles(canDelete);
        }
      } catch (error) {
        console.error("Error checking permissions:", error);
        // Handle permission check errors silently or show a generic message
        if (isMounted) {
          setCanCreateAudioFiles(false);
          setCanDeleteAudioFiles(false);
        }
      }
    };

    void checkPermissions();

    return () => {
      isMounted = false; // Cleanup function
    };
  }, []); // Run permission check only once on mount

  const handleDelete = async (id: string, _version: number, name: string) => {
    if (
      confirm(
        `Are you sure you want to delete ${name || "this audio file"}? This action cannot be undone.`
      )
    ) {
      // Use the safeDelete handler
      await safeDelete(() =>
        httpClient.request<ResponseBody>("/aws/audio-file/delete", {
          method: "POST",
          data: { app: 2, id, _version },
        })
      );
    }
  };

  /**
   * Get the data for the audio file table
   * @returns - The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    const data: TableData[][] = audioFiles.map((audioFile) => {
      const { id, _version, title, category, availability, studies, length } =
        audioFile;

      return [
        {
          contents: <span>{title}</span>,
          searchValue: title,
          sortValue: title ?? "",
        },
        {
          contents: <span>{category}</span>,
          searchValue: category,
          sortValue: category ?? "",
        },
        {
          contents: (
            <span>
              {availability === "all" ? "All users" : "Individual user"}
            </span>
          ),
          searchValue: "",
          sortValue: availability === "all" ? "All users" : "Individual user",
        },
        {
          contents: (
            <span>
              {studies?.length && studies[0] !== "all"
                ? studies.join(", ")
                : "All studies"}
            </span>
          ),
          searchValue: studies?.join() ?? "",
          sortValue:
            studies?.length && studies[0] !== "all"
              ? studies.join(", ")
              : "All studies",
        },
        {
          contents: (
            <span>
              {length
                ? `${parseInt((length / 60).toString()).toString()}:${(length % 60).toString().padStart(2, "0")}`
                : ""}
            </span>
          ),
          searchValue: "",
          sortValue: "",
        },
        {
          contents: (
            <div className="flex size-full">
              {/* if the user can edit, link to the edit subject page */}
              <Button
                variant="danger"
                size="sm"
                className="h-full grow"
                onClick={() =>
                  void handleDelete(id ?? "", _version ?? 0, title ?? "")
                }
                disabled={!canDeleteAudioFiles || isDeleting}
              >
                Delete
              </Button>
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
        },
      ];
    });

    return data;
  };

  // if the user can enroll subjects, include an enroll button
  const tableControl = (
    <Link to="/coordinator/ditti/audio/upload">
      <Button
        variant="primary"
        disabled={!(canCreateAudioFiles || APP_ENV === "demo")}
        rounded={true}
      >
        Upload +
      </Button>
    </Link>
  );

  if (dataLoading) {
    return (
      <ListView>
        <ListContent />
      </ListView>
    );
  }

  return (
    <ListView>
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
