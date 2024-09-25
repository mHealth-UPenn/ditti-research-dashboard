import React, { useState, useEffect, ChangeEvent, createRef } from "react";
import TextField from "../fields/textField";
import { Study, ResponseBody, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";
import Select from "../fields/select";
import RadioField from "../fields/radioField";
import CloseIcon from '@mui/icons-material/Close';


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
  const [files, setFiles] = useState<{ name: string; size: string; }[]>([]);
  const [loading, setLoading] = useState(true);

  const fileInputRef = createRef<HTMLInputElement>();

  // Initialize the list of studies
  useEffect(() => {
    makeRequest("/db/get-studies?app=2")
      .then(setStudies)
      .then(() => setLoading(false));
  }, []);

  /**
   * POST changes to the backend.
   */
  const post = async (): Promise<void> => {
    const data = {
      // title,
      category,
      fileName: "fileName",
      availability,
      studies,
    };

    const body = {
      app: 2,  // Ditti Dashboard = 2
      create: data
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    await makeRequest("aws/audio-file/create", opts)
      .then(handleSuccess)
      .catch(handleFailure);
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

  const handleSelectFiles = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles([...e.target.files].map( file => {
        const size = (file.size / (1024 * 1024)).toFixed(1) + ' MB';
        const name = file.name.split(".").slice(0, -1).join();
        return { name, size };
      }));
    }
  };

  const handleTitleKeyup = (text: string, i: number) => {
    const updatedFiles = [...files];
    files[i].name = text;
    setFiles(updatedFiles);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] overflow-scroll overflow-x-hidden bg-white lg:bg-transparent lg:flex-row xl:px-12">
      <div className="p-12 flex-grow bg-white lg:overflow-y-scroll">
        {/* the enroll subject form */}
        {
          loading ?
          <SmallLoader /> :
          <>
            <h1 className="text-xl font-bold border-b border-solid border-[#B3B3CC]">
              Upload Audio File
            </h1>
            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
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

            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
                <RadioField
                  id="availability-radio"
                  label="Availability"
                  onChange={handleClickAvailability}
                  values={["All Users", "Individual"]}
                  prefill="All Users"
                />
              </div>
              <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
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
            <div className="flex flex-col md:flex-row">
              <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
                <RadioField
                  id="studies-radio"
                  label="Studies"
                  onChange={handleClickStudies}
                  values={["All Studies", "Select Studies"]}
                  prefill="All Studies"
                />
              </div>
              <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
                <div style={{ marginBottom: "0.5rem" }}>
                  <b>Select studies...</b>
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
              {
                Boolean(selectedStudies.size) &&
                <div className="flex flex-col md:flex-row">
                  <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
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
              <div className="flex flex-col md:flex-row">
                <div className="flex w-full flex-col mb-8 md:pr-4 xl:mx-8 md:w-1/2">
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
                  {
                    Boolean(files.length) &&
                    <div className="flex flex-col md:flex-row">
                      {files.map((file, i) =>
                        <div key={i}>
                          <div className="flex justify-between w-full mb-1 md:pr-4 xl:mx-8 md:w-1/2">
                            <span className="font-bold">{file.name}</span>
                            <span>{file.size}</span>
                          </div>
                          <div className="flex w-full flex-col mb-4 md:pr-4 xl:mx-8 md:w-1/2">
                            <TextField
                              id={`file-${file.name}`}
                              type="text"
                              value={file.name}
                              onKeyup={(text: string) => handleTitleKeyup(text, i)}>
                                <span className="flex items-center px-2 bg-light h-full">Title</span>
                            </TextField>
                          </div>
                        </div>
                      )}
                    </div>
                  }
              </div>
            </div>
          </>
        }
      </div>

      {/* the subject summary */}
      <div className="flex flex-col flex-shrink-0 px-16 py-8 w-full lg:px-8 lg:w-[20rem] xl:w-[24rem] bg-[#33334D] text-white lg:max-h-[calc(100vh-8rem)] xl:p-12">
        <h1 className="border-b border-solid border-white text-xl font-bold">Audio File Summary</h1>
        <div className="flex flex-col md:flex-row lg:flex-col lg:max-h-[calc(100vh-17rem)] lg:h-full lg:justify-between">
          <div className="flex-grow mb-8 lg:overflow-y-scroll">
            Title:
            <br />
            {/* &nbsp;&nbsp;&nbsp;&nbsp;{title} */}
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
            {availability === ""
              ? "All users"
              : `Individual - ${availability}`}
            <br />
            <br />
            Studies:
            <br />
            {
              selectedStudies.size ?
              studies.filter(study => selectedStudies.has(study.id)).map((s, i) =>
                <span key={`study-${i}`}>
                  {Boolean(i) && <br />}
                  &nbsp;&nbsp;&nbsp;&nbsp;{s.acronym}: {s.name}
                </span>
              ) :
              <span>&nbsp;&nbsp;&nbsp;&nbsp;All Studies</span>
            }
            <br />
            <br />
            File:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;filename.mp3 - 8.2mb
            <br />
          </div>
          <div className="flex flex-col md:w-1/2 lg:w-full justify-end">
            <AsyncButton
              className="p-4"
              onClick={post}
              text="Upload"
              type="primary"/>
            <div className="mt-6 text-sm">
              <i>
              Audio file details cannot be changed after upload. The file must be
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
