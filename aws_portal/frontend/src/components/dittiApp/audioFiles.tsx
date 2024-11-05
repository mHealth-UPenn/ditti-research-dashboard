import React, { useEffect, useState } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess, makeRequest } from "../../utils";
import { AudioFile, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";
import AudioFileUpload from "./audioFileUpload";


const AudioFiles: React.FC<ViewProps> = ({
  handleClick,
  goBack,
  flashMessage,
}) => {
  const [canCreate, setCanCreate] = useState<boolean>(false);
  const [canDelete, setCanDelete] = useState<boolean>(false);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

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
    // Get whether user can upload audio files
    const getCreate = getAccess(2, "Create", "Users")
      .then(() => setCanCreate(true))
      .catch(() => setCanCreate(false));

    // get whether the user can edit subjects
    const getEdit = getAccess(2, "Delete", "Audio Files")
      .then(() => setCanDelete(true))
      .catch(() => setCanDelete(false));

    const getAudioFiles = makeRequest("/aws/get-audio-files?app=2");

    // when all promises complete, hide the loader
    Promise.all([getCreate, getEdit, getAudioFiles]).then(
      ([create, edit, audioFilesData]) => {
        setAudioFiles(audioFilesData);
        setLoading(false);
      }
    );

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
        makeRequest("/aws/get-audio-files?app=2")
          .then(audioFilesData => {
            setAudioFiles(audioFilesData);
            setLoading(false);
          })
          .catch(() => {
            flashMessage(<span>And error occured while reloading the page. Please refresh and try again.</span>, "danger");
          });
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
            <div className="flex-left table-data">
                <span>{title}</span>
            </div>
          ),
          searchValue: title,
          sortValue: title ? title : ""
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{category}</span>
            </div>
          ),
          searchValue: category,
          sortValue: category ? category : ""
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {availability === "all" ? "All users" : "Individual user"}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: availability === "all" ? "All users" : "Individual user"
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{(studies?.length && studies[0] !== "all") ? studies.join(", ") : "All studies"}</span>
            </div>
          ),
          searchValue: studies?.join(),
          sortValue: (studies?.length && studies[0] !== "all") ? studies.join(", ") : "All studies"
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {length
                  ? `${parseInt((length / 60).toString())}:${(length % 60).toString().padStart(2, "0")}`
                  : ""}
                </span>
            </div>
          ),
          searchValue: "",
          sortValue: "",
        },
        {
          contents: (
            <div className="flex-left table-control">

              {/* if the user can edit, link to the edit subject page */}
              {canDelete ? (
                <button
                  className="button-danger"
                  onClick={() => handleDelete(id || "", _version || 0, fileName || "")}
                >
                  Delete
                </button>
              ) : null}
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });

    return data;
  };

  // if the user can enroll subjects, include an enroll button
  const tableControl = canCreate ? (
    <button
      className="button-primary"
      onClick={() =>
        handleClick(
          ["Upload"],
          <AudioFileUpload
            goBack={goBack}
            flashMessage={flashMessage}
            handleClick={handleClick}
          />
        )
      }
    >
      Upload
    </button>
  ) : (
    <React.Fragment />
  );

  return (
    <div className="page-container">
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

export default AudioFiles;
