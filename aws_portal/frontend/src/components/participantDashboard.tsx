import React, { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { makeRequest } from "../utils";

interface ApiData {
  api_name: string;
  scope: string;
  expires_at: string | null;
}

interface StudyData {
  study_name: string;
  study_id: number;
  study_start_date: string;
  study_end_date: string;
}

const ParticipantDashboard: React.FC = () => {
  const [participantData, setParticipantData] = useState<{
    email: string;
    user_id: number;
    apis: ApiData[];
    studies: StudyData[];
  } | null>(null);
  const [sleepList, setSleepList] = useState(null);

  const { cognitoLogout } = useAuth();

  useEffect(() => {
    fetchParticipantData();
    fetchSleepList();
  }, []);

  const authorizeFitbit = () => {
    window.location.href = "http://localhost:5000/cognito/fitbit/authorize";
  };

  const revokeFitbit = async () => {
    const res = await makeRequest("/participant/api/Fitbit", { method: "DELETE" });
    console.log("Revoke Fitbit: ", res);
    fetchParticipantData();
    fetchSleepList();
  };

  const fetchParticipantData = async () => {
    const res = await makeRequest("/participant", { method: "GET" });
    setParticipantData(res); // Store the participant data in state
  };

  const fetchSleepList = async () => {
    try {
      const res = await makeRequest("/cognito/fitbit/sleep_list", { method: "GET" });
      setSleepList(res);
    } catch (error) {
      console.error("Error fetching participant data:", error);
      setSleepList(null);
    }
  };

  // Check if Fitbit access is authorized
  const isFitbitAuthorized = participantData?.apis.some(api => api.api_name === "Fitbit");

  return (
    <div className="dashboard-container">
      <h1>Participant Dashboard</h1>
      <button onClick={cognitoLogout}>Logout</button>
      {isFitbitAuthorized ? (
        <button onClick={revokeFitbit}>Revoke access to my Fitbit data</button>
      ) : (
        <button onClick={authorizeFitbit}>Authorize access to my Fitbit data</button>
      )}

      {participantData && (
        <div className="participant-info">
          <h2>Participant Information</h2>
          <p><strong>Email:</strong> {participantData.email}</p>
          <p><strong>User ID:</strong> {participantData.user_id}</p>

          <h3>API Access Details</h3>
          {participantData.apis.map((api, index) => (
            <div key={index}>
              <p><strong>API Name:</strong> {api.api_name}</p>
              <p><strong>Scope:</strong> {api.scope}</p>
              <p><strong>Expiration:</strong> {api.expires_at || "No expiration date"}</p>
            </div>
          ))}

          <h3>Study Details</h3>
          {participantData.studies.map((study, index) => (
            <div key={index}>
              <p><strong>Study Name:</strong> {study.study_name}</p>
              <p><strong>Study ID:</strong> {study.study_id}</p>
              <p><strong>Start Date:</strong> {study.study_start_date}</p>
              <p><strong>End Date:</strong> {study.study_end_date}</p>
            </div>
          ))}
        </div>
      )}

      {sleepList && (
        <div className="sleep-list">
          <h2>Sleep List Data</h2>
          <pre>{JSON.stringify(sleepList, null, 2)}</pre> {/* Display raw JSON */}
        </div>
      )}
    </div>
  );
};

export default ParticipantDashboard;
