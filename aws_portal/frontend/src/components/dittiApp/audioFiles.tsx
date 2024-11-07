import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess, makeRequest } from "../../utils";
import { AudioFile, ViewProps } from "../../interfaces";
import AudioFileUpload from "./audioFileUpload";
import Button from "../buttons/button";
import AdminView from "../containers/admin/adminView";
import AdminContent from "../containers/admin/adminContent";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { APP_ENV } from "../../environment";


const AudioFiles: React.FC<ViewProps> = ({
  handleClick,
  goBack,
  flashMessage,
}) => {
  const [canCreateAudioFiles, setCanCreateAudioFiles] = useState<boolean>(false);
  const [canDeleteAudioFiles, setCanDeleteAudioFiles] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const { audioFiles, refreshAudioFiles } = useDittiDataContext();

  const columns: Column[] = [
    {
      name: "Title",
      searchable: true,
      sortable: true,
      width: 20
    },
    {
      name: "Category",
      searchable: true,
      sortable: true,
      width: 20
    },
    {
      name: "Availability",
      searchable: false,
      sortable: true,
      width: 20
    },
    {
      name: "Studies",
      searchable: true,
      sortable: true,
      width: 20
    },
    {
      name: "Length",
      searchable: false,
      sortable: false,
      width: 10
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10
    }
  ];

  useEffect(() => {
    const promises: Promise<void>[] = [];
    // Get whether user can upload audio files
    promises.push(
      getAccess(2, "Create", "Users")
        .then(() => setCanCreateAudioFiles(true))
        .catch(() => setCanCreateAudioFiles(false))
    );

    // get whether the user can edit subjects
    promises.push(
      getAccess(2, "Delete", "Audio Files")
        .then(() => setCanDeleteAudioFiles(true))
        .catch(() => setCanDeleteAudioFiles(false))
      );

    // when all promises complete, hide the loader
    Promise.all(promises).then(() => setLoading(false));
  }, []);

  const handleDelete = async (id: string, _version: number, name: string) => {
    if (confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`)) {
      try {
        await makeRequest(
          "/aws/audio-file/delete",
          {
            method: "POST",
            body: JSON.stringify({ app: 2, id, _version })
          }
        );
        flashMessage(<span>Audio file deleted successfully</span>, "success");
        setLoading(true);

        refreshAudioFiles()
          .then(() => setLoading(false))
          .catch(() =>
            flashMessage(
              <span>
                And error occured while reloading the page. Please refresh and
                try again.
              </span>,
              "danger"
            )
          );
      } catch (error) {
        console.error(error);
        const e = error as { msg: string };
        flashMessage(<span>An unexpected error occured: {e.msg}</span>, "danger");
      }
    }
  }

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
        length
      } = audioFile;

      return [
        {
          contents: (
            <span>{title}</span>
          ),
          searchValue: title,
          sortValue: title ? title : ""
        },
        {
          contents: (
            <span>{category}</span>
          ),
          searchValue: category,
          sortValue: category ? category : ""
        },
        {
          contents: (
            <span>
              {availability === "all" ? "All users" : "Individual user"}
            </span>
          ),
          searchValue: "",
          sortValue: availability === "all" ? "All users" : "Individual user"
        },
        {
          contents: (
            <span>{(studies?.length && studies[0] !== "all") ? studies.join(", ") : "All studies"}</span>
          ),
          searchValue: studies?.join(),
          sortValue: (studies?.length && studies[0] !== "all") ? studies.join(", ") : "All studies"
        },
        {
          contents: (
            <span>
              {length
                ? `${parseInt((length / 60).toString())}:${(length % 60).toString().padStart(2, "0")}`
                : ""}
            </span>
          ),
          searchValue: "",
          sortValue: "",
        },
        {
          contents: (
            <div className="flex w-full h-full">
              {/* if the user can edit, link to the edit subject page */}
              <Button
                variant="danger"
                size="sm"
                className="h-full flex-grow"
                onClick={() => handleDelete(id || "", _version || 0, fileName || "")}
                disabled={!canDeleteAudioFiles}>
                  Delete
              </Button>
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
        }
      ];
    });

    return data;
  };

  // if the user can enroll subjects, include an enroll button
  const tableControl =
    <Button
      variant="primary"
      onClick={() =>
        handleClick(
          ["Upload"],
          <AudioFileUpload
            goBack={goBack}
            flashMessage={flashMessage}
            handleClick={handleClick} />
        )
      }
      disabled={!(canCreateAudioFiles || APP_ENV === "demo")}
      rounded={true}>
        Upload +
    </Button>

  if (loading) {
    return (
      <AdminView>
        <AdminContent />
      </AdminView>
    );
  }

  return (
    <AdminView>
      <AdminContent>
        <Table
          columns={columns}
          control={tableControl}
          controlWidth={10}
          data={getData()}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault="" />
      </AdminContent>
    </AdminView>
  );
};

export default AudioFiles;
