import React, { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import ViewContainer from '../containers/viewContainer';
import Card from '../cards/card';
import CardContentRow from '../cards/cardContentRow';
import Title from '../text/title';
import Button from '../buttons/button';
import Link from '../links/link';


const ParticipantDashboard: React.FC = () => {
  const [fitbitConnected, setFitbitConnected] = useState(false);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [scope, setScope] = useState<string[]>([]);
  const [dataSummary, setDataSummary] = useState("");
  const [loading, setLoading] = useState(true);

  const { cognitoLogout, dittiId } = useAuth();

  useEffect(() => {
    const init = async () => {
      // TODO: pull data here
      const start = new Date();
      const end = new Date();
      start.setDate(1);
      end.setDate(28);

      setFitbitConnected(true);
      setStartDate(start);
      setEndDate(end);
      setScope(["Sleep"]);
      setDataSummary(`
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eget nisi
        elit. Donec molestie, mauris sed sollicitudin convallis, mauris odio
        convallis dolor, sit amet rhoncus dolor felis vel dui. Nam scelerisque
        arcu nisi, ut mattis nibh suscipit sit amet. Ut lacinia facilisis
        vulputate. Sed vitae enim turpis. Sed in molestie lacus, id tincidunt
        enim. In posuere tempus egestas.
      `);
      setLoading(false);
    };

    init();
  }, []);

  const handleRedirect = () => {
    window.location.href = "http://localhost:5000/cognito/fitbit/authorize";
  };

  const handleClickManageData = () => {
    window.location.href = "https://hosting.med.upenn.edu/forms/DittiApp/view.php?id=10677";
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

      <ViewContainer navbar={false}>
        <Card width="md">
          <CardContentRow>
            <Title>Your User ID: {dittiId}</Title>
            {!fitbitConnected &&
              <Button onClick={handleRedirect} rounded={true}>Connect FitBit</Button>
            }
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <span>Expires on: <b>January 1, 2025</b></span>
              <span>We will no longer collect your data after this date.</span>
            </div>
          </CardContentRow>
        </Card>
        <Card width="sm">
          <CardContentRow>
            <Title>Your Data</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <div className="flex flex-col mb-4">
                <span>Data being collected:</span>
                {scope.map((s, i) =>
                  <span key={i} className="font-bold">
                    &nbsp;&nbsp;&nbsp;&nbsp;{s}
                  </span>
                )}
              </div>
              <div className="flex flex-col">
                <span>Between these dates:</span>
                <span className="font-bold">
                  &nbsp;&nbsp;&nbsp;&nbsp;{startDate?.toLocaleDateString()} - {endDate?.toLocaleDateString()}
                </span>
              </div>
            </div>
          </CardContentRow>
          <CardContentRow>
            <Title>Why are we collecting your data?</Title>
          </CardContentRow>
          <CardContentRow>
            <span>{dataSummary}</span>
          </CardContentRow>
          <CardContentRow>
            <Title>Manage my data</Title>
          </CardContentRow>
          <CardContentRow>
            <Link onClick={handleClickManageData}>
              Request deletion of my account or data.
            </Link>
          </CardContentRow>
        </Card>
      </ViewContainer>
    </main>
  );
};

export default ParticipantDashboard;
