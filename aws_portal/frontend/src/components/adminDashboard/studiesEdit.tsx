import React, { useEffect, useState } from "react";
import TextField from "../fields/textField";
import { ResponseBody, Study, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

/**
 * The form's prefill
 */
interface StudyPrefill {
  name: string;
  acronym: string;
  dittiId: string;
  email: string;
}

/**
 * studyId: the database primary key, 0 if creating a new entry
 */
interface StudiesEditProps extends ViewProps {
  studyId: number;
}

const StudiesEdit: React.FC<StudiesEditProps> = ({ studyId, goBack, flashMessage }) => {
  const [state, setState] = useState<StudyPrefill & { loading: boolean }>({
    name: "",
    acronym: "",
    dittiId: "",
    email: "",
    loading: true,
  });

  useEffect(() => {
    // set any form prefill data and hide the loader
    getPrefill().then((prefill: StudyPrefill) =>
      setState(prevState => ({ ...prevState, ...prefill, loading: false }))
    );
  }, [studyId]);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<StudyPrefill> => {
    const id = studyId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/study?app=1&id=" + id).then(makePrefill)
      : {
          name: "",
          acronym: "",
          dittiId: "",
          email: "",
        };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (res: Study[]): StudyPrefill => {
    const study = res[0];
    return {
      name: study.name,
      acronym: study.acronym,
      dittiId: study.dittiId,
      email: study.email,
    };
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async (): Promise<void> => {
    const { acronym, dittiId, email, name } = state;
    const data = { acronym, ditti_id: dittiId, email, name };
    const id = studyId;
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data }),
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/study/edit" : "/admin/study/create";

    await makeRequest(url, opts)
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

  const { name, acronym, dittiId, email, loading } = state;
  const buttonText = studyId ? "Update" : "Create";

  return (
    <div className="page-container" style={{ flexDirection: "row" }}>
      {/* the edit/create form */}
      <div className="page-content bg-white">
        {loading ? (
          <SmallLoader />
        ) : (
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {studyId ? "Edit " : "Create "} Study
              </h1>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="name"
                    type="text"
                    placeholder=""
                    prefill={name}
                    label="Name"
                    onKeyup={(text: string) =>
                      setState(prevState => ({ ...prevState, name: text }))
                    }
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <TextField
                    id="email"
                    type="text"
                    placeholder=""
                    prefill={email}
                    label="Team Email"
                    onKeyup={(text: string) =>
                      setState(prevState => ({ ...prevState, email: text }))
                    }
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="acronym"
                    type="text"
                    placeholder=""
                    prefill={acronym}
                    label="Acronym"
                    onKeyup={(text: string) =>
                      setState(prevState => ({ ...prevState, acronym: text }))
                    }
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <TextField
                    id="dittiId"
                    type="text"
                    placeholder=""
                    prefill={dittiId}
                    label="Ditti ID"
                    onKeyup={(text: string) =>
                      setState(prevState => ({ ...prevState, dittiId: text }))
                    }
                    feedback=""
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="admin-form-summary bg-dark">
        {/* the edit/create summary */}
        <h1 className="border-white-b">Study Summary</h1>
        <span>
          Name:
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;{name}
          <br />
          <br />
          Team Email:
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;{email}
          <br />
          <br />
          Acronym:
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;{acronym}
          <br />
          <br />
          Ditti ID:
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;{dittiId}
          <br />
        </span>
        <AsyncButton onClick={post} text={buttonText} type="primary" />
      </div>
    </div>
  );
};

export default StudiesEdit;
