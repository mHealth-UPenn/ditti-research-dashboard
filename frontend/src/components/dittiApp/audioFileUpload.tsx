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

import { useState, ChangeEvent, createRef } from "react";
import { TextField } from "../fields/textField";
import { httpClient } from "../../lib/http";
import { SelectField } from "../fields/selectField";
import { RadioField } from "../fields/radioField";
import CloseIcon from "@mui/icons-material/Close";
import axios from "axios";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { FormSummary } from "../containers/forms/formSummary";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import { FormSummarySubtext } from "../containers/forms/formSummarySubtext";
import { Button } from "../buttons/button";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { useDittiData } from "../../hooks/useDittiData";
import { SmallLoader } from "../loader/loader";
import { APP_ENV } from "../../environment";
import { useStudies } from "../../hooks/useStudies";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useNavigate } from "react-router-dom";
import { FileMetadata } from "./dittiApp.types";
import { ResponseBody } from "../../types/api";
import { useApiHandler } from "../../hooks/useApiHandler";

export const AudioFileUpload = () => {
  const [category, setCategory] = useState("");
  const [availability, setAvailability] = useState("All Users");
  const [dittiId, setDittiId] = useState("");
  const [studiesRadio, setStudiesRadio] = useState("All Studies");
  const [selectedStudies, setSelectedStudies] = useState<Set<number>>(
    new Set()
  );
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<number[]>([]);
  const [canUpload, setCanUpload] = useState(false);
  const [categoryFeedback, setCategoryFeedback] = useState<string>("");
  const [availabilityFeedback, setAvailabilityFeedback] = useState<string>("");
  const [studiesFeedback, setStudiesFeedback] = useState<string>("");

  const fileInputRef = createRef<HTMLInputElement>();

  const { dataLoading, audioFiles } = useDittiData();
  const { studiesLoading, studies } = useStudies();

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  const existingFiles = new Set();
  audioFiles.forEach((af) => existingFiles.add(af.fileName));

  const { safeRequest: safeUploadProcess, isLoading: isUploading } =
    useApiHandler({
      successMessage: "All files successfully uploaded.",
      errorMessage: (error) => `Upload process failed: ${error.message}`,
      onSuccess: () => {
        navigate(-1);
      },
    });

  /**
   * Get a set of presigned URLs for uploading audio files to S3.
   * @returns string[]: The array of presigned URLs
   */
  const getPresignedUrls = async (): Promise<string[]> => {
    const filesData = selectedFiles.map((file) => ({
      key: file.name,
      type: file.type,
    }));

    try {
      const res = await httpClient.request<{ urls: string[] }>(
        "/aws/audio-file/get-presigned-urls",
        {
          method: "POST",
          data: { app: 2, files: filesData }, // Use data property
        }
      );
      return res.urls;
    } catch (error) {
      // Error will be caught by safeUploadProcess
      console.error("Failed to get presigned URLs:", error);
      throw error; // Re-throw the original error
    }
  };

  /**
   * Upload all selected audio files using a set of presigned URLs. This
   * function uses axios to update upload progress for each file. Files
   * are uploaded in parallel and an error is thrown if any fail.
   * @param urls string[]
   */
  const uploadFiles = async (urls: string[]) => {
    const progressArray: number[] = Array<number>(selectedFiles.length).fill(0);
    setUploadProgress(progressArray);

    const uploadPromises = selectedFiles.map((file, index) => {
      return axios.put(urls[index], file, {
        headers: {
          "Content-Type": file.type,
        },
        onUploadProgress: (progressEvent) => {
          let progress = 0; // Default to 0
          if (progressEvent.total) {
            progress = Math.round(
              (progressEvent.loaded / progressEvent.total) * 100
            );
          } else if (progressEvent.loaded > 0) {
            // If total is unknown but we loaded some bytes, estimate as 100?
            // Or handle differently - for now, let's cap at 99 if total unknown
            progress = 99;
          }
          progressArray[index] = progress;
          setUploadProgress([...progressArray]);
        },
      });
    });

    try {
      await Promise.all(uploadPromises);
      // If all succeed, ensure progress is 100%
      setUploadProgress(Array(selectedFiles.length).fill(100));
    } catch (error) {
      // Error will be caught by safeUploadProcess
      console.error("Error during file upload:", error);
      // Axios errors might need specific parsing here if not handled by global interceptor
      throw error; // Re-throw the original error (could be AxiosError)
    }
  };

  const insertFiles = async (): Promise<void> => {
    const selectedStudyAcronyms = studies
      .filter((s) => selectedStudies.has(s.id))
      .map((s) => s.acronym);

    if (files.length !== selectedFiles.length) {
      throw new Error("Mismatch between file metadata and selected files.");
    }

    const dataToInsert = selectedFiles.map((file, i) => ({
      availability: availability === "All Users" ? "all" : dittiId,
      category: category,
      fileName: file.name,
      // Use selected acronyms, default to ["all"] if none selected or "All Studies" chosen
      studies:
        selectedStudyAcronyms.length > 0 && studiesRadio !== "All Studies"
          ? selectedStudyAcronyms
          : ["all"],
      length: files[i].length,
      title: files[i].title,
    }));

    const body = {
      app: 2, // Ditti Dashboard = 2
      create: dataToInsert,
    };

    try {
      await httpClient.request<ResponseBody>("/aws/audio-file/create", {
        method: "POST",
        data: body, // Use data property
      });
    } catch (error) {
      // Error will be caught by safeUploadProcess
      console.error("Failed to insert file records:", error);
      throw error; // Re-throw original error
    }
  };

  /**
   * Handles when the user clicks "Upload." This function does nothing if the
   * user did not select any files. This function attempts to get presigned URLs
   * for all selected files and attempts to upload them using these files.
   * @returns
   */
  const handleUpload = async () => {
    // Reset previous feedback
    setCategoryFeedback("");
    setAvailabilityFeedback("");
    setStudiesFeedback("");

    // Validate form fields
    let isValid = true;
    if (category.trim() === "") {
      setCategoryFeedback("Category is required.");
      isValid = false;
    }
    if (availability === "Individual" && dittiId.trim() === "") {
      setAvailabilityFeedback(
        "Ditti ID is required for Individual availability."
      );
      isValid = false;
    }
    if (studiesRadio === "Select Studies" && selectedStudies.size === 0) {
      setStudiesFeedback(
        "At least one study must be selected, or choose 'All Studies'."
      );
      isValid = false;
    }
    if (selectedFiles.length === 0) {
      flashMessage(<span>Please select files to upload.</span>, "danger");
      isValid = false;
    }

    if (files.some((file) => file.exists)) {
      flashMessage(
        <span>
          One or more selected files already exist. Please remove them or
          rename.
        </span>,
        "danger"
      );
      isValid = false;
    }

    if (!isValid) {
      flashMessage(
        <span>Please correct the errors in the form.</span>,
        "danger"
      );
      return;
    }

    await safeUploadProcess(async () => {
      setUploadProgress([]);
      const urls = await getPresignedUrls();
      await uploadFiles(urls);
      await insertFiles();
    });
  };

  const selectStudy = (id: number): void => {
    setSelectedStudies((prevSelectedStudies) => {
      const newSelectedStudies = new Set(prevSelectedStudies);
      newSelectedStudies.add(id);
      return newSelectedStudies;
    });
  };

  const removeStudy = (id: number): void => {
    setSelectedStudies((prevSelectedStudies) => {
      const newSelectedStudies = new Set(prevSelectedStudies);
      newSelectedStudies.delete(id);
      return newSelectedStudies;
    });
  };

  const handleClickAvailability = (e: ChangeEvent<HTMLInputElement>) => {
    setAvailability(e.target.value);
    setStudiesRadio("All Studies");
    setSelectedStudies(new Set());

    if (e.target.value == "All Users") {
      setDittiId("");
    }
  };

  const handleClickStudies = (e: ChangeEvent<HTMLInputElement>) => {
    setStudiesRadio(e.target.value);
    setAvailability("All Users");
    setDittiId("");

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
  };

  const handleSelectFiles = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const arr = Array.from(e.target.files);
      const files = await Promise.all(
        arr.map(async (file) => {
          const size = (file.size / (1024 * 1024)).toFixed(1) + " MB";
          const title = file.name.split(".").slice(0, -1).join();
          const length = await getAudioDuration(file);
          const exists = existingFiles.has(file.name);
          return { name: file.name, title, size, length, exists };
        })
      );

      setFiles(files);
      setSelectedFiles(arr);

      if (!files.some((file) => file.exists)) {
        setCanUpload(true);
      }
    } else {
      setCanUpload(false);
    }
  };

  const handleTitleKeyup = (text: string, i: number) => {
    const updatedFiles = [...files];
    updatedFiles[i] = { ...files[i], title: text };
    setFiles(updatedFiles);
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    // If there are hours, include them in the output (HH:MM:SS)
    if (hours > 0) {
      return `${hours.toString()}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }

    // Otherwise, just return MM:SS
    return `${minutes.toString()}:${secs.toString().padStart(2, "0")}`;
  };

  const percentComplete = uploadProgress.length
    ? Math.floor(uploadProgress.reduce((a, b) => a + b) / uploadProgress.length)
    : 0;

  if (studiesLoading || dataLoading) {
    return (
      <FormView>
        <Form>
          <SmallLoader />
        </Form>
      </FormView>
    );
  }

  return (
    <FormView>
      <Form>
        <FormTitle>Upload Audio File</FormTitle>

        {/* Category field */}
        <FormRow>
          <FormField>
            <TextField
              id="category"
              type="text"
              placeholder=""
              label="Category"
              onKeyup={setCategory}
              feedback={categoryFeedback}
              value={category}
            />
          </FormField>
        </FormRow>

        {/* Availability & Ditti ID fields */}
        <FormRow>
          <FormField>
            <RadioField
              id="availability-radio"
              label="Availability"
              onChange={handleClickAvailability}
              values={["All Users", "Individual"]}
              checked={availability}
            />
          </FormField>
          <FormField>
            <TextField
              id="availability"
              type="text"
              label="Ditti ID"
              value={dittiId}
              onKeyup={setDittiId}
              disabled={availability === "All Users"}
              feedback={availabilityFeedback}
            />
          </FormField>
        </FormRow>

        {/* Studies & select studies fields */}
        <FormRow>
          <FormField>
            <RadioField
              id="studies-radio"
              label="Studies"
              onChange={handleClickStudies}
              values={["All Studies", "Select Studies"]}
              checked={studiesRadio}
            />
          </FormField>
          <FormField>
            <div className="mb-1">Add study</div>
            <div className="border-light">
              <SelectField
                id={0}
                opts={studies.map((s) => {
                  return { value: s.id, label: s.acronym };
                })}
                placeholder="Select studies..."
                callback={selectStudy}
                disabled={studiesRadio === "All Studies"}
              />
            </div>
            {studiesFeedback !== "" && (
              <span className="text-sm text-[red]">{studiesFeedback}</span>
            )}
          </FormField>
        </FormRow>
        {!!selectedStudies.size && (
          <FormRow>
            <FormField>
              <div className="mb-1">
                <p>Selected studies</p>
              </div>
              {studies
                .filter((study) => selectedStudies.has(study.id))
                .map((s, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="truncate">{`${s.acronym}: ${s.name}`}</span>
                    <div
                      className="cursor-pointer p-2"
                      onClick={() => {
                        removeStudy(s.id);
                      }}
                    >
                      <CloseIcon color="warning" />
                    </div>
                  </div>
                ))}
            </FormField>
          </FormRow>
        )}

        {/* Select audio files field */}
        <FormRow>
          <FormField>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              accept=".mp3"
              onChange={(e) => {
                void handleSelectFiles(e);
              }}
            />
            <label htmlFor="audio-file-upload" className="mb-1">
              Select audio files
            </label>
            <Button
              variant="tertiary"
              onClick={handleClickChooseFiles}
              className="w-max"
              size="sm"
              rounded={true}
            >
              Choose files
            </Button>
          </FormField>
        </FormRow>

        {/* Selected audio files list */}
        {Boolean(files.length) && (
          <FormRow>
            <FormField>
              <span className="mb-1">Audio files</span>
              {files.map((file, i) => (
                <div key={i} className="w-full">
                  <div className="mb-1 flex w-full justify-between">
                    <span className="truncate">{file.name}</span>
                    <span className="w-max shrink-0">
                      {file.size} - {formatDuration(file.length)}
                    </span>
                  </div>
                  <div className="mb-4 flex w-full flex-col">
                    {file.exists ? (
                      <span className="text-sm text-[red]">
                        An audio file with this name already exists.
                        <br />
                        Rename this file or delete the existing file and try
                        again.
                      </span>
                    ) : (
                      <TextField
                        id={`file-${file.name}`}
                        type="text"
                        value={file.title}
                        onKeyup={(text: string) => {
                          handleTitleKeyup(text, i);
                        }}
                      >
                        <span
                          className="flex h-full items-center bg-extra-light
                            px-2"
                        >
                          Title
                        </span>
                      </TextField>
                    )}
                  </div>
                </div>
              ))}
            </FormField>
          </FormRow>
        )}
      </Form>

      {/* the subject summary */}
      <FormSummary>
        <FormSummaryTitle>Audio File Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Files:
            <br />
            {files.map((file, i) => (
              <span key={i}>
                {Boolean(i) && (
                  <>
                    <br />
                    <br />
                  </>
                )}
                &nbsp;&nbsp;&nbsp;&nbsp;{file.title}
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{file.size} -{" "}
                {formatDuration(file.length)}
              </span>
            ))}
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
            {studiesRadio === "All Studies" ? (
              <span>&nbsp;&nbsp;&nbsp;&nbsp;All Studies</span>
            ) : (
              studies
                .filter((study) => selectedStudies.has(study.id))
                .map((s, i) => (
                  <span key={`study-${i.toString()}`}>
                    {Boolean(i) && <br />}
                    &nbsp;&nbsp;&nbsp;&nbsp;{s.acronym}: {s.name}
                  </span>
                ))
            )}
          </FormSummaryText>
          <div>
            {
              // Upload progress bar
              isUploading && (
                <div className="mb-4 flex w-full flex-col">
                  <div className="mb-1 flex w-full justify-between">
                    <span>Uploading...</span>
                    <span>{percentComplete}%</span>
                  </div>
                  <span
                    className={"h-[4px] bg-white transition-all duration-500"}
                    style={{
                      width: percentComplete
                        ? `${percentComplete.toString()}%`
                        : 0,
                    }}
                  />
                </div>
              )
            }
            <FormSummaryButton
              onClick={handleUpload}
              disabled={!canUpload || isUploading || APP_ENV === "demo"}
            >
              {isUploading
                ? `Uploading... ${percentComplete.toString()}%`
                : "Upload"}
            </FormSummaryButton>
            {APP_ENV === "demo" && (
              <FormSummarySubtext>
                Audio file uploads are disabled in demo mode.
              </FormSummarySubtext>
            )}
            <FormSummarySubtext>
              Audio file details cannot be changed after upload. The files must
              be deleted and uploaded again.
            </FormSummarySubtext>
          </div>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
