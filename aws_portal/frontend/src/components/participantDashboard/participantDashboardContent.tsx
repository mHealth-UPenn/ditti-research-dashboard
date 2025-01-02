import { useState, useMemo, useEffect } from 'react';
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

const defaultConsentContentText = "By accepting, you agree that your data will be used solely for research purposes described in our terms. You can withdraw consent at any time.";

const ParticipantDashboardContent = () => {
  const [isConsentOpen, setIsConsentOpen] = useState<boolean>(false);
  const [consentError, setConsentError] = useState<string>("");

  const { dittiId } = useAuth();
  const { studies, apis, studySubjectLoading } = useStudySubjectContext();

  useEffect(() => {
    console.log(studies);
  }, [studies]);

  // Use the earliest startsOn date as the beginning of data collection
  const startDate = useMemo(() => {
    if (studies.length === 0) return null;
    return new Date(Math.min(...studies.map(s => new Date(s.startsOn).getTime())));
  }, [studies]);

  // Use the latest expiresOn date as the end of data collection
  const endDate = useMemo(() => {
    if (studies.length === 0) return null;
    const validTimestamps = studies
      .map(s => (s.expiresOn ? new Date(s.expiresOn).getTime() : null)) // Map to timestamps, handle undefined
      .filter(timestamp => timestamp !== null) as number[]; // Filter out nulls and assert as number[]

    if (validTimestamps.length === 0) {
      return null; // No valid dates
    }

    return new Date(Math.max(...validTimestamps)); // Get the latest date
  }, [studies]);

  const scope = useMemo(() => [...new Set(apis.map(api => api.scope).flat())], [apis]);

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

  // TODO: Update study consent in database

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
    if (studies.length === 0) {
      setConsentError('You are not enrolled in any studies.');
      return;
    }
    setIsConsentOpen(true);
  };

  // Generate the contentHtml based on the number of enrolled studies
  const consentContentHtml = useMemo(() => {
    if (studies.length === 0) {
      return `<p>You are not enrolled in any studies. Please enroll in a study to connect your FitBit data.</p>`;
    } else if (studies.length === 1) {
      return `<h4>${studies[0].studyName}</h4><p>${studies[0].consentInformation || defaultConsentContentText}</p>`;
    } else {
      let content = '';
      studies.forEach(study => {
        content += `<h4>${study.studyName}</h4><p>${study.consentInformation || defaultConsentContentText}</p>`;
      });
      return content;
    }
  }, [studies]);

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
                  &nbsp;&nbsp;&nbsp;&nbsp;{startDate ? startDate.toLocaleDateString() : 'N/A'} - {endDate ? endDate.toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </CardContentRow>
          <CardContentRow>
            <Title>Why are we collecting your data?</Title>
          </CardContentRow>
          <CardContentRow>
            <span>{studies.length > 0 ? studies[0].dataSummary : 'No data summary available.'}</span>
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
        contentHtml={consentContentHtml}
      />
    </>
  );
};

export default ParticipantDashboardContent;
