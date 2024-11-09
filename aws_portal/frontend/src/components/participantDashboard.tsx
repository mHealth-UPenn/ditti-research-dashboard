import React from 'react';
import { useAuth } from '../hooks/useAuth';

const ParticipantDashboard: React.FC = () => {
  const { cognitoLogout } = useAuth();

  const handleRedirect = () => {
    window.location.href = 'http://localhost:5000/cognito/fitbit/authorize';
  };

  return (
    <div className="dashboard-container">
      <h1>Participant Dashboard</h1>
      <button onClick={cognitoLogout}>
        Logout
      </button>
      <button onClick={handleRedirect}>
        Authorize Fitbit
      </button>
    </div>
  );
};

export default ParticipantDashboard;
