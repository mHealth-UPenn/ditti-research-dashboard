import React, { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import ViewContainer from '../containers/viewContainer';
import Card from '../cards/card';
import CardContentRow from '../cards/cardContentRow';
import Title from '../text/title';
import Button from '../buttons/button';


const ParticipantDashboard: React.FC = () => {
  const [fitbitConnected, setFitbitConnected] = useState(false);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [scope, setScope] = useState<string[]>([]);
  const [dataSummary, setDataSummary] = useState("");
  const [loading, setLoading] = useState(true);

  const { cognitoLogout, dittiId } = useAuth();

  const handleRedirect = () => {
    window.location.href = 'http://localhost:5000/cognito/fitbit/authorize';
  };

  return (
    <main className="flex flex-col h-screen">
      {/* the header */}
      <div className="bg-secondary text-white flex items-center justify-between flex-shrink-0 h-16">
        <div className="flex flex-col text-2xl ml-8">
          <span className="mr-2">Ditti</span>
          <span className="text-sm whitespace-nowrap overflow-hidden">Participant Dashboard</span>
        </div>
        <div className="mr-8">
          <Button variant="tertiary" size="sm" rounded={true} onClick={cognitoLogout}>Logout</Button>
        </div>
      </div>

      <ViewContainer>
        <Card width="md">
          <CardContentRow>
            <Title>Your User ID: {dittiId}</Title>
            <Button onClick={handleRedirect} rounded={true}>Connect FitBit</Button>
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <span>Expires on: <b>January 1, 2025</b></span>
              <span>We will no longer collect your data after this date.</span>
            </div>
          </CardContentRow>
        </Card>
      </ViewContainer>
    </main>
  );
};

export default ParticipantDashboard;
