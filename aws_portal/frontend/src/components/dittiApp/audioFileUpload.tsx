import React, { useState, ChangeEvent, createRef, useEffect } from "react";
import TextField from "../fields/textField";
import { Study, ResponseBody, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import AsyncButton from "../buttons/asyncButton";
import Select from "../fields/select";
import RadioField from "../fields/radioField";
import CloseIcon from "@mui/icons-material/Close";
import axios, { AxiosError } from "axios";
import FormView from "../containers/forms/formView";
import Form from "../containers/forms/form";
import FormTitle from "../text/formTitle";
import FormRow from "../containers/forms/formRow";
import FormField from "../containers/forms/formField";
import FormSummary from "../containers/forms/formSummary";
import FormSummaryTitle from "../text/formSummaryTitle";
import FormSummaryText from "../containers/forms/formSummaryText";
import FormSummaryButton from "../containers/forms/formSummaryButton";
import FormSummarySubtext from "../containers/forms/formSummarySubtext";
import Button from "../buttons/button";
import FormSummaryContent from "../containers/forms/formSummaryContent";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { SmallLoader } from "../loader";


interface IFile {
  name: string;
  title: string;
  size: string;
  length: number;
  exists: boolean;
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
  const [uploading, setUploading] = useState(false);
  const [canUpload, setCanUpload] = useState(false);
  const [categoryFeedback, setCategoryFeedback] = useState<string>("");
  const [availabilityFeedback, setAvailabilityFeedback] = useState<string>("");
  const [studiesFeedback, setStudiesFeedback] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const fileInputRef = createRef<HTMLInputElement>();

  const { audioFiles } = useDittiDataContext();
  const existingFiles = new Set();
  audioFiles.forEach(af => existingFiles.add(af.fileName))

  useEffect(() => {
    makeRequest("/db/get-studies?app=2")
      .then((res: Study[]) => {
        setStudies(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
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
        length: files[i].length,
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
    // Validate the form
    let isValid = true;
    setCategoryFeedback("");
    setAvailabilityFeedback("");
    setStudiesFeedback("");

    if (category === "") {
      setCategoryFeedback("Enter a category.");
      isValid = false;
    }
    if (availability === "Individual" && dittiId === "") {
      setAvailabilityFeedback("Enter a Ditti ID or select All Users");
      isValid = false;
    }
    if (studiesRadio === "Select Studies" && !selectedStudies.size) {
      setStudiesFeedback("Select at least one study or All Studies.");
      isValid = false;
    }
    if (selectedFiles.length === 0 || !isValid) {
      flashMessage(<span>Please fix errors in the form.</span>, "danger");
      return;
    }

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
  }

  const handleSelectFiles = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const arr = Array.from(e.target.files);
      const files = await Promise.all(
        arr.map(async file => {
          const size = (file.size / (1024 * 1024)).toFixed(1) + " MB";
          const title = file.name.split(".").slice(0, -1).join();
          const length = await getAudioDuration(file);
          const exists = existingFiles.has(file.name);
          return { name: file.name, title, size, length, exists };
        })
      );

      setFiles(files);
      setSelectedFiles(arr);
      
      if (!files.some(file => file.exists)) {
        setCanUpload(true);
      }
    } else {
      setCanUpload(false);
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

  if (loading) {
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
              value={category} />
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
              feedback={availabilityFeedback} />
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
            <div className="mb-1">
              Add study...
            </div>
            <div className="border-light">
              <Select
                id={0}
                opts={studies.map(
                  s => {return { value: s.id, label: s.acronym }}
                )}
                placeholder="Select studies..."
                callback={selectStudy}
                disabled={studiesRadio === "All Studies"}/>
            </div>
            {/* feedback on error TODO: Fix the select field so this does not have to be here */}
            {studiesFeedback !== "" && <span className="text-sm text-[red]">{studiesFeedback}</span>}
          </FormField>
        </FormRow>
        {!!selectedStudies.size &&
          <FormRow>
            <FormField>
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
            </FormField>
          </FormRow>
        }

        {/* Select audio files field */}
        <FormRow>
          <FormField>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              accept=".mp3"
              onChange={handleSelectFiles} />
            <label
              htmlFor="audio-file-upload"
              className="mb-1">
              Select audio files
            </label>
            <Button
              variant="secondary"
              onClick={handleClickChooseFiles}>
                Choose files
            </Button>
          </FormField>
        </FormRow>

        {/* Selected audio files list */}
        {
          Boolean(files.length) &&
          <FormRow>
            <FormField>
              <span className="font-bold mb-2">Audio files</span>
              {files.map((file, i) =>
                <div key={i} className="w-full">
                  <div className="flex justify-between w-full mb-1">
                    <span className="truncate">{file.name}</span>
                    <span className="w-max flex-shrink-0">{file.size} - {formatDuration(file.length)}</span>
                  </div>
                  <div className="flex w-full flex-col mb-4">
                    {
                      file.exists ?
                      <span className="text-sm text-[red]">
                        An audio file with this name already exists.<br />
                        Rename this file or delete the existing file and try
                        again.
                      </span> :
                      <TextField
                        id={`file-${file.name}`}
                        type="text"
                        value={file.title}
                        onKeyup={(text: string) => handleTitleKeyup(text, i)}>
                          <span className="flex items-center px-2 bg-light h-full">Title</span>
                      </TextField>
                    }
                  </div>
                </div>
              )}
            </FormField>
          </FormRow>
        }
      </Form>

      {/* the subject summary */}
      <FormSummary>
        <FormSummaryTitle>Audio File Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
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
          </FormSummaryText>
          <div>
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
            <FormSummaryButton>
              <AsyncButton
                className="p-4"
                onClick={handleUpload}
                disabled={!canUpload}>
                  Upload
              </AsyncButton>
            </FormSummaryButton>
            <FormSummarySubtext>
              Audio file details cannot be changed after upload. The files must be
              deleted and uploaded again.
            </FormSummarySubtext>
          </div>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};

export default AudioFileUpload;
