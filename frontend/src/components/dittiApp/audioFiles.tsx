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
import { getAccess, makeRequest } from "../../utils";
import { Button } from "../buttons/button";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { APP_ENV } from "../../environment";
import { Link } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useDittiData } from "../../hooks/useDittiData";

export const AudioFiles = () => {
  const [canCreateAudioFiles, setCanCreateAudioFiles] =
    useState<boolean>(false);
  const [canDeleteAudioFiles, setCanDeleteAudioFiles] =
    useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const { dataLoading, audioFiles, refreshAudioFiles } = useDittiData();
  const { flashMessage } = useFlashMessages();

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
    const promises: Promise<void>[] = [];
    // Get whether user can upload audio files
    promises.push(
      getAccess(2, "Create", "Participants")
        .then(() => {
          setCanCreateAudioFiles(true);
        })
        .catch(() => {
          setCanCreateAudioFiles(false);
        })
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "Delete", "Audio Files")
        .then(() => {
          setCanDeleteAudioFiles(true);
        })
        .catch(() => {
          setCanDeleteAudioFiles(false);
        })
    );

    // when all promises complete, hide the loader
    void Promise.all(promises).then(() => {
      setLoading(false);
    });
  }, []);

  const handleDelete = async (id: string, _version: number, name: string) => {
    if (
      confirm(
        `Are you sure you want to delete ${name}? This action cannot be undone.`
      )
    ) {
      try {
        await makeRequest("/aws/audio-file/delete", {
          method: "POST",
          body: JSON.stringify({ app: 2, id, _version }),
        });
        flashMessage(<span>Audio file deleted successfully</span>, "success");
        setLoading(true);

        refreshAudioFiles()
          .then(() => {
            setLoading(false);
          })
          .catch(() => {
            flashMessage(
              <span>
                And error occurred while reloading the page. Please refresh and
                try again.
              </span>,
              "danger"
            );
          });
      } catch (error) {
        console.error(error);
        const e = error as { msg: string };
        flashMessage(
          <span>An unexpected error occurred: {e.msg}</span>,
          "danger"
        );
      }
    }
  };

  /**
   * Get the data for the audio file table
   * @returns - The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    const data: TableData[][] = audioFiles.map((audioFile) => {
      const {
        id,
        _version,
        fileName,
        title,
        category,
        availability,
        studies,
        length,
      } = audioFile;

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
          searchValue: studies?.join(),
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
                  void handleDelete(id ?? "", _version ?? 0, fileName ?? "")
                }
                disabled={!canDeleteAudioFiles}
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

  if (loading || dataLoading) {
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
