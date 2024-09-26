import React, { useState, useEffect, ChangeEvent, createRef } from "react";
import TextField from "../fields/textField";
import { Study, ResponseBody, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";
import Select from "../fields/select";
import RadioField from "../fields/radioField";
import CloseIcon from "@mui/icons-material/Close";
import axios, { AxiosError } from "axios";


interface IFile {
  name: string;
  title: string;
  size: string;
  length: number;
}


const AudioFileUpload: React.FC<ViewProps> = ({
  goBack,
  flashMessage,
}) => {
  const [category, setCategory] = useState("");
  const [availability, setAvailability] = useState("All Users");
  const [dittiId, setDittiId] = useState("");
  const [studiesRadio, setStudiesRadio] = useState("All Studies");
  const [studies, setStudies] = useState<Study[]>([]);
  const [selectedStudies, setSelectedStudies] = useState<Set<number>>(new Set());
  const [files, setFiles] = useState<IFile[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fileInputRef = createRef<HTMLInputElement>();

  // Initialize the list of studies
  useEffect(() => {
    makeRequest("/db/get-studies?app=2")
      .then(setStudies)
      .then(() => setLoading(false));
  }, []);

  /**
   * Get a set of presigned URLs for uploading audio files to S3.
   * @returns string[]: The array of presigned URLs
   */
  const getPresignedUrls = async () => {
    const files = selectedFiles.map(file => (
      { key: file.name, type: file.type }
    ));

    try {
      const res = await makeRequest(
        "/aws/audio-file/get-presigned-urls",
        {
          method: "POST",
          body: JSON.stringify({ app: 2, files })
        }
      )
      return res.urls as string[];
    } catch (error) {
      const e = error as { msg: string };
      throw new AxiosError(e.msg);
    }
  };

  /**
   * Upload all selected audio files using a set of presigned URLs. This
   * function uses axios to update upload progress for each file. Files
   * are uploaded in parallel and an error is thrown if any fail.
   * @param urls string[]
   */
  const uploadFiles = async (urls: string[]) => {
    const progressArray: number[] = new Array(selectedFiles.length).fill(0);
    setUploadProgress(progressArray);

    const uploadPromises = selectedFiles.map((file, index) => {
      return axios.put(
        urls[index],
        file, {
          headers: {
            "Content-Type": file.type,
          },
          onUploadProgress: (progressEvent) => {
            let progress;

            if (progressEvent.total) {
              progress = (progressEvent.loaded / progressEvent.total) * 100;
            } else {
              progress = 100;
            }

            progressArray[index] = progress;
            setUploadProgress([...progressArray]);
          },
        }
      );
    });

    const responses = await Promise.all(uploadPromises);
    const errors = responses.filter(res => res.status !== 200);

    if (errors.length) {
      const error = errors.map(res => res.data.error).join("\n");
      throw Error(error);
    }
  };

  const insertFiles = async (): Promise<void> => {
    try {
      const selected = studies
        .filter(s => selectedStudies.has(s.id))
        .map(s => s.acronym);

      const data = selectedFiles.map((file, i) => ({
        availability: availability === "All Users" ? "all" : dittiId,
        category: category,
        fileName: file.name,
        studies: selected.length ? selected : ["all"],
        length: 10,
        title: files[i].title,
      }));

      const body = {
        app: 2,  // Ditti Dashboard = 2
        create: data
      };

      const opts = { method: "POST", body: JSON.stringify(body) };
      await makeRequest("/aws/audio-file/create", opts);
    } catch (error) {
      const e = error as { msg: string };
      throw new AxiosError(e.msg);
    }
  };

  /**
   * Handles when the user clicks "Upload." This function does nothing if the
   * user did not select any files. This function attempts to get presigned URLs
   * for all selected files and attempts to upload them using these files.
   * @returns 
   */
  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);

    try {
      const urls = await getPresignedUrls();
      await uploadFiles(urls);
      await insertFiles();
      goBack();
      flashMessage(<span>All files successfully uploaded.</span>, "success");
    } catch (error) {
      const axiosError = error as AxiosError
      console.error("Error uploading files:", error);
      flashMessage(<span>Error uploading files: {axiosError.message}</span>, "danger");
    } finally {
      setUploading(false);
    }
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // go back to the list view and flash a message
    goBack();
    flashMessage(<span>{res.msg}</span>, "success");
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message from the backend or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );
    flashMessage(msg, "danger");
  };

  const selectStudy = (id: number): void => {
    const updatedSelectedStudies = selectedStudies;
    updatedSelectedStudies.add(id);
    setSelectedStudies(updatedSelectedStudies);

    // Set studies to force re-render
    setStudies([...studies]);
  };

  const removeStudy = (id: number): void => {
    const updatedSelectedStudies = selectedStudies
    updatedSelectedStudies.delete(id);
    setSelectedStudies(updatedSelectedStudies);
    setStudies([...studies]);
  };

  const handleClickAvailability = (e: ChangeEvent<HTMLInputElement>) => {
    setAvailability(e.target.value);

    if (e.target.value == "All Users") {
      setDittiId("");
    }
  };

  const handleClickStudies = (e: ChangeEvent<HTMLInputElement>) => {
    setStudiesRadio(e.target.value);

    if (e.target.value === "All Studies") {
      setSelectedStudies(new Set());
    }
  };

  const handleClickChooseFiles = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const getAudioDuration = (file: File): Promise<number> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      // When the file has been read, create an audio element to determine its duration
      reader.onload = (e: ProgressEvent<FileReader>) => {
        const result = e.target?.result as string; // We know this will be a string (data URL)
        const audio = new Audio(result);

        // Ensure the audio metadata is loaded to get the duration
        audio.addEventListener("loadedmetadata", () => {
          resolve(audio.duration); // `audio.duration` is a number in seconds
        });

        // Handle errors during the process
        audio.addEventListener("error", () => {
          reject(new Error("Error loading audio file"));
        });
      };

      // Handle errors while reading the file
      reader.onerror = () => {
        reject(new Error("File reading failed"));
      };

      reader.readAsDataURL(file);
    });
  }

  const handleSelectFiles = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const arr = Array.from(e.target.files);
      const files = await Promise.all(
        arr.map(async file => {
          const size = (file.size / (1024 * 1024)).toFixed(1) + " MB";
          const title = file.name.split(".").slice(0, -1).join();
          const length = await getAudioDuration(file);
          return { name: file.name, title, size, length };
        })
      );

      setFiles(files);
      setSelectedFiles(arr);
    }
  };

  const handleTitleKeyup = (text: string, i: number) => {
    const updatedFiles = [...files];
    files[i].title = text;
    setFiles(updatedFiles);
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
  
    // If there are hours, include them in the output (HH:MM:SS)
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } 
  
    // Otherwise, just return MM:SS
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }

  const percentComplete = uploadProgress.length ? Math.floor(
    uploadProgress.reduce((a, b) => a + b) / uploadProgress.length
  ) : 0;

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] overflow-scroll overflow-x-hidden bg-white lg:bg-transparent lg:flex-row">
      <div className="p-12 flex-grow bg-white lg:overflow-y-scroll">
        {/* the enroll subject form */}
        {
          loading ?
          <SmallLoader /> :
          <>
            <h1 className="text-xl font-bold border-b border-solid border-[#B3B3CC]">
              Upload Audio File
            </h1>

            {/* Category field */}
            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8">
                <TextField
                  id="category"
                  type="text"
                  placeholder=""
                  label="Category"
                  onKeyup={setCategory}
                  feedback=""
                />
              </div>
            </div>

            {/* Availability & Ditti ID fields */}
            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8 md:pr-4 md:w-1/2">
                <RadioField
                  id="availability-radio"
                  label="Availability"
                  onChange={handleClickAvailability}
                  values={["All Users", "Individual"]}
                  prefill="All Users"
                />
              </div>
              <div className="flex w-full flex-col mb-8 md:w-1/2">
                <TextField
                  id="availability"
                  type="text"
                  label="Ditti ID"
                  value={dittiId}
                  onKeyup={setDittiId}
                  disabled={availability === "All Users"}
                />
              </div>
            </div>

            {/* Studies & select studies fields */}
            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8 md:pr-4 md:w-1/2">
                <RadioField
                  id="studies-radio"
                  label="Studies"
                  onChange={handleClickStudies}
                  values={["All Studies", "Select Studies"]}
                  prefill="All Studies"
                />
              </div>
              <div className="flex w-full flex-col mb-8 md:w-1/2">
                <div style={{ marginBottom: "0.5rem" }}>
                  <b>Add study...</b>
                </div>
                <div className={"border-light" + (studiesRadio === "All Studies" ? " bg-light" : "")}>
                  <Select
                    id={0}
                    opts={studies.map(
                      s => {return { value: s.id, label: s.acronym }}
                    )}
                    placeholder="Select studies..."
                    callback={selectStudy}
                    disabled={studiesRadio === "All Studies"}
                  />
                </div>
              </div>
            </div>
            {
              Boolean(selectedStudies.size) &&
              <div className="flex flex-col md:flex-row">
                <div className="flex w-full flex-col mb-8">
                  <div className="mb-1">
                    <b>Selected studies</b>
                  </div>
                  {
                    studies.filter(study => selectedStudies.has(study.id)).map((s, i) =>
                      <div key={i} className="flex items-center justify-between">
                        <span className="truncate">{`${s.acronym}: ${s.name}`}</span>
                        <div
                          className="p-2 cursor-pointer"
                          onClick={() => removeStudy(s.id)}>
                          <CloseIcon color="warning" />
                        </div>
                      </div>
                    )
                  }
                </div>
              </div>
            }

            {/* Select audio files field */}
            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  className="hidden"
                  accept=".mp3"
                  onChange={handleSelectFiles} />
                <label
                  htmlFor="audio-file-upload"
                  className="mb-2 font-bold">
                  Select audio files
                </label>
                <button
                  className="button button-large button-secondary p-4"
                  onClick={handleClickChooseFiles}>
                  Choose files
                </button>
              </div>
            </div>
            {
              Boolean(files.length) &&
              <div className="flex flex-col md:flex-row">
                <div className="flex flex-col w-full">
                  <span className="font-bold mb-1">Audio files</span>
                  {files.map((file, i) =>
                    <div key={i} className="w-full">
                      <div className="flex justify-between w-full mb-1">
                        <span className="truncate">{file.name}</span>
                        <span className="w-max flex-shrink-0">{file.size} - {formatDuration(file.length)}</span>
                      </div>
                      <div className="flex w-full flex-col mb-4">
                        <TextField
                          id={`file-${file.name}`}
                          type="text"
                          value={file.title}
                          onKeyup={(text: string) => handleTitleKeyup(text, i)}>
                            <span className="flex items-center font-bold px-2 bg-light h-full">Title</span>
                        </TextField>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            }
          </>
        }
      </div>

      {/* the subject summary */}
      <div className="flex flex-col flex-shrink-0 px-16 py-12 w-full lg:px-8 lg:w-[20rem] 2xl:w-[28rem] bg-[#33334D] text-white lg:max-h-[calc(100vh-8rem)]">
        <h1 className="border-b border-solid border-white text-xl font-bold">Audio File Summary</h1>
        <div className="flex flex-col md:flex-row lg:flex-col lg:max-h-[calc(100vh-17rem)] lg:h-full lg:justify-between">
          <div className="flex-grow mb-8 lg:overflow-y-scroll truncate">
            Files:
            <br />
            {/* &nbsp;&nbsp;&nbsp;&nbsp;{title} */}
            {
              files.map((file, i) =>
                <span key={i}>
                  {Boolean(i) && <><br /><br /></>}
                  &nbsp;&nbsp;&nbsp;&nbsp;{file.title}
                  <br />
                  &nbsp;&nbsp;&nbsp;&nbsp;{file.size} - {formatDuration(file.length)}
                </span>
              )
            }
            <br />
            <br />
            Category:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{category}
            <br />
            <br />
            Availability
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;
            {availability === "All Users"
              ? "All Users"
              : `Individual - ${dittiId}`}
            <br />
            <br />
            Studies:
            <br />
            {
              studiesRadio === "All Studies" ?
              <span>&nbsp;&nbsp;&nbsp;&nbsp;All Studies</span> :
              studies.filter(study => selectedStudies.has(study.id)).map((s, i) =>
                <span key={`study-${i}`}>
                  {Boolean(i) && <br />}
                  &nbsp;&nbsp;&nbsp;&nbsp;{s.acronym}: {s.name}
                </span>
              )
            }
          </div>
          {
            // Upload progres bar
            uploading &&
            <div className="flex flex-col w-full mb-4">
              <div className="flex justify-between mb-1 w-full">
                <span>Uploading...</span>
                <span>{percentComplete}%</span>
              </div>
              <span className={`h-[4px] bg-white transition-all duration-500`}
                style={{ width: percentComplete ? `${percentComplete}%` : 0 }}/>
            </div>
          }
          <div className="flex flex-col md:w-1/2 lg:w-full justify-end">
            <AsyncButton
              className="p-4"
              onClick={handleUpload}
              text="Upload"
              type="primary"/>
            <div className="mt-6 text-sm">
              <i>
              Audio file details cannot be changed after upload. The files must be
              deleted and uploaded again.
              </i>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioFileUpload;
