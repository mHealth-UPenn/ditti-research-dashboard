import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import Card from '../cards/card';
import CardContentRow from '../cards/cardContentRow';
import Title from '../text/title';
import Button from '../buttons/button';
import Link from '../links/linkComponent';
import { Link as RouterLink } from "react-router-dom";
import { ParticipantWearableDataProvider } from '../../contexts/wearableDataContext';
import WearableVisualization from '../visualizations/wearableVisualization';
import { useStudySubjectContext } from '../../contexts/studySubjectContext';
import { SmallLoader } from '../loader';
import ConsentModal from '../containers/consentModal'

const ParticipantDashboardContent = () => {
  const [isConsentOpen, setIsConsentOpen] = useState<boolean>(false);
  const [consentError, setConsentError] = useState<string>("");

  const { dittiId } = useAuth();
  const { studies, apis, studySubjectLoading } = useStudySubjectContext();

  // Use the earliest `startsOn` date as the beginning of data collection
  const startDate = new Date(Math.min(...studies.map(s => new Date(s.startsOn).getTime())));

  // Use the latest `expiresOn` date as the end of data collection
  const endDate = (() => {
    const validTimestamps = studies
      .map(s => (s.expiresOn ? new Date(s.expiresOn).getTime() : null)) // Map to timestamps, handle undefined
      .filter(timestamp => timestamp !== null) as number[]; // Filter out nulls and assert as number[]
  
    if (validTimestamps.length === 0) {
      return null; // No valid dates
    }
  
    return new Date(Math.max(...validTimestamps)); // Get the latest date
  })();
  
  const scope = [...new Set(apis.map(api => api.scope).flat())];
  

  // For now assume we are only connecting Fitbit API
  const fitbitConnected = apis.length > 0;

  // Redirect after authenticating with Fitbit
  const handleRedirect = () => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/cognito/fitbit/authorize`;
  };

  // Redirect to form for requesting deletion of account
  const handleClickManageData = () => {
    window.location.href = "https://hosting.med.upenn.edu/forms/DittiApp/view.php?id=10677";
  };

  // Handlers for Consent Modal actions
  const handleConsentAccept = () => {
    setIsConsentOpen(false);
    setConsentError('');
    handleRedirect();
  };

  const handleConsentDeny = () => {
    setIsConsentOpen(false);
    setConsentError('You must consent to connect your FitBit data.');
  };

  const handleConsentClose = () => {
    setIsConsentOpen(false);
    setConsentError('You must choose an option to continue.');
  };

  // Handler for Connect FitBit button click
  const handleConnectFitBitClick = () => {
    setIsConsentOpen(true);
  };

  if (studySubjectLoading) {
    return (
      <>
        <Card width="md">
          <SmallLoader />
        </Card>
        <Card width="sm">
          <SmallLoader />
        </Card>
      </>
    );
  }

  return (
    <>
      <Card width="md">

        {/* Title */}
        <CardContentRow className="justify-between">
          <Title>Your User ID: {dittiId}</Title>
          {!fitbitConnected && (
            <div className="flex flex-col items-end relative">
              <Button onClick={handleConnectFitBitClick} rounded={true}>
                Connect FitBit
              </Button>
              {/* Error message without reserving space */}
              {consentError && (
                <span className="absolute top-full mt-2 text-red-500 text-sm right-0">
                  {consentError}
                </span>
              )}
            </div>
          )}
        </CardContentRow>

        {/* Information to display if the Fitbit API is connected */}
        {fitbitConnected &&
          <>
            <CardContentRow>
              <div className="flex flex-col">
                <span>
                  Expires on:{" "}
                  <b>
                    {endDate
                      ? endDate.toLocaleDateString("en-US", {
                          month: "long",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "No expiration date available"}
                  </b>
                </span>
                <span>
                  {endDate
                    ? "We will no longer collect your data after this date."
                    : "We will no longer collect your data if disconnected."}
                </span>
              </div>
            </CardContentRow>

            {/* Data visualization */}
            <CardContentRow>
              <ParticipantWearableDataProvider>
                <WearableVisualization />
              </ParticipantWearableDataProvider>
            </CardContentRow>
          </>
        }
      </Card>

      {/* Data summary and study information to show if Fitbit is connected */}
      {fitbitConnected &&
        <Card width="sm">
          <CardContentRow>
            <Title>Your Data</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <div className="flex flex-col mb-4">
                <span>Data being collected:</span>
                {scope.map((s, i) =>
                  <span key={i} className="font-bold capitalize">
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
            <span>{studies.length && studies[0].dataSummary}</span>
          </CardContentRow>
          <CardContentRow>
            <Title>Manage my data</Title>
          </CardContentRow>
          <CardContentRow>
            <Link onClick={handleClickManageData}>
              Request deletion of my account or data.
            </Link>
          </CardContentRow>
          <CardContentRow>
            <Title>Legal</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <RouterLink className="link" to="/terms-of-use">Terms of Use</RouterLink>
              <RouterLink className="link" to="/privacy-policy">Privacy Policy</RouterLink>
            </div>
          </CardContentRow>
        </Card>
      }

      {/* Consent Modal */}
      <ConsentModal
        isOpen={isConsentOpen}
        onAccept={handleConsentAccept}
        onDeny={handleConsentDeny}
        onClose={handleConsentClose}
        contentHtml={`
          <p>
            By accepting, you agree that your data will be used solely for 
            research purposes described in our terms. You can withdraw consent at any time.
          </p>
        `}
      />
    </>
  );
};

export default ParticipantDashboardContent;
