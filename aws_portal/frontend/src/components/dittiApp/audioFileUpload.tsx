import React, { useState, useEffect } from "react";
import TextField from "../fields/textField";
import {
  Study,
  AboutSleepTemplate,
  ResponseBody,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import CheckField from "../fields/checkField";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";
import Select from "../fields/select";


const AudioFileUpload: React.FC<ViewProps> = ({
  goBack,
  flashMessage,
}) => {
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [availability, setAvailability] = useState("");
  const [studies, setStudies] = useState<Study[]>([]);
  const [selectedStudies, setSelectedStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(true);

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
      title,
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

  /**
   * Assign an about sleep template to the user
   * @param id - the template's database primary key
   */
  const selectStudy = (id: number): void => {
    const selectedStudy = studies.filter(study => study.id === id)[0];
    if (selectedStudy) {
      const updatedSelectedStudies = [...selectedStudies];
      updatedSelectedStudies.push(selectedStudy);
      setSelectedStudies(updatedSelectedStudies);
    }
  };

  /**
   * Assign an about sleep template to the user
   * @param id - the template's database primary key
   */
  const removeStudy = (id: number): void => {
    const updatedSelectedStudies = selectedStudies
      .filter(study => study.id !== id);
    setSelectedStudies(updatedSelectedStudies);
  };

  return (
    <div className="page-container" style={{ flexDirection: "row" }}>
      <div className="page-content bg-white">
        {/* the enroll subject form */}
        {loading ? (
          <SmallLoader />
        ) : (
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                Upload Audio File
              </h1>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="title"
                    type="text"
                    placeholder=""
                    label="Title"
                    onKeyup={setTitle}
                    feedback=""
                  />
                </div>

                <div className="admin-form-field">
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

              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="availabilityRadio"
                    type="text"
                    placeholder=""
                    label="Availability"
                    onKeyup={() => ""}
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <TextField
                    id="availability"
                    type="text"
                    placeholder=""
                    label="Ditti ID"
                    onKeyup={setAvailability}
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="studiesRadio"
                    type="text"
                    placeholder=""
                    label="Studies"
                    onKeyup={() => ""}
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <div style={{ marginBottom: "0.5rem" }}>
                    <b>Select studies...</b>
                  </div>
                  <div className="border-light">
                    <Select
                      id={0}
                      opts={studies.map(
                        s => {return { value: s.id, label: s.acronym }}
                      )}
                      placeholder="Select study..."
                      callback={selectStudy}
                      getDefault={() => -1}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* the subject summary */}
      <div className="admin-form-summary bg-dark">
        <h1 className="border-white-b">Audio File Summary</h1>
        <span>
          Title:
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;{title}
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
          {selectedStudies.length ? (
            selectedStudies.map((s, i) => {
              return (
                <span key={`study-${i}`}>
                  &nbsp;&nbsp;&nbsp;&nbsp;{s.acronym}
                </span>
              );
            })
          ) : (
            <span>&nbsp;&nbsp;&nbsp;&nbsp;All Studies</span>
          )}
          <br />
          <br />
          File:
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;filename.mp3 - 8.2mb
          <br />
        </span>
        <AsyncButton onClick={post} text="Upload" type="primary" />
        <div style={{ marginTop: "1.5rem" }}>
          <i>
          Audio file details cannot be changed after upload. The file must be
          deleted and uploaded again.
          </i>
        </div>
      </div>
    </div>
  );
};

export default AudioFileUpload;
