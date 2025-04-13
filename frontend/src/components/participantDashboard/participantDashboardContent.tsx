/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { useState, useMemo, useEffect } from "react";
import { useAuth } from "../../hooks/useAuth";
import { Card } from "../cards/card";
import { CardContentRow } from "../cards/cardContentRow";
import { Title } from "../text/title";
import { Button } from "../buttons/button";
import { LinkComponent } from "../links/linkComponent";
import { Link as RouterLink } from "react-router-dom";
import { ParticipantWearableDataProvider } from "../../contexts/wearableDataContext";
import { WearableVisualization } from "../visualizations/wearableVisualization";
import { useStudySubjects } from "../../hooks/useStudySubjects";
import { SmallLoader } from "../loader/loader";
import { ConsentModal } from "../containers/consentModal/consentModal";
import { makeRequest } from "../../utils";
import { ParticipantStudy } from "../../types/api";
import { QuillView } from "../containers/quillView";

const defaultConsentContentText = "By accepting, you agree that your data will be used solely for research purposes described in our terms. You can withdraw consent at any time.";

export const ParticipantDashboardContent = () => {
  const [isConsentOpen, setIsConsentOpen] = useState<boolean>(false);
  const [consentError, setConsentError] = useState<string>("");
  const [unconsentedStudies, setUnconsentedStudies] = useState<ParticipantStudy[]>([]);

  const { dittiId } = useAuth();
  const { studies, apis, studySubjectLoading, refetch } = useStudySubjects();

  const getStudiesNeedConsent = () => {
    const studiesNeedConsent = studies.filter(s => !s.didConsent);
    if (studiesNeedConsent.length > 0) {
      setUnconsentedStudies(studiesNeedConsent);
    } else {
      setUnconsentedStudies([]);
    }
  };

  // Gather all studies where the user has not consented
  useEffect(getStudiesNeedConsent, [studies]);

  // Use the earliest startsOn date as the beginning of data collection
  const startDate = useMemo(() => {
    if (studies.length === 0) return null;
    return new Date(Math.min(...studies.map(s => new Date(s.startsOn).getTime())));
  }, [studies]);

  // Use the latest expiresOn date as the end of data collection
  const endDate = useMemo(() => {
    if (studies.length === 0) return null;
    const validTimestamps = studies
      .map(s => (s.expiresOn ? new Date(s.expiresOn).getTime() : null))
      .filter(timestamp => timestamp !== null) as number[];

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
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER}/api/fitbit/authorize`;
  };

  // Redirect to form for requesting deletion of account
  const handleClickManageData = () => {
    window.location.href = "https://hosting.med.upenn.edu/forms/DittiApp/view.php?id=10677";
  };

  const handleConsentAccept = async () => {
    if (unconsentedStudies.length === 0) {
      setIsConsentOpen(false);
      return;
    }

    try {
      await Promise.all(
        unconsentedStudies.map(study => {
          return makeRequest(`/participant/study/${study.studyId}/consent`, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ didConsent: true }),
          });
        })
      );

      // Clear error, close modal
      setConsentError("");
      setIsConsentOpen(false);

      // Refetch data to ensure consistency
      await refetch();
      getStudiesNeedConsent();

      // Redirect to Fitbit authorization after successful consent
      handleRedirect();
    } catch (err) {
      console.error(err);
      const errorMsg = "There was a problem updating your consent. Please try again.";
      setConsentError(errorMsg);
    }
  };

  const handleConsentClose = () => {
    setIsConsentOpen(false);
    setConsentError("You must accept the consent terms to connect your Fitbit API, please try again.");
  };

  // If there are no unconsented studies, proceed to Fitbit flow
  // otherwise, prompt them to consent
  const handleConnectFitBitClick = () => {
    if (unconsentedStudies.length === 0) {
      handleRedirect();
    } else {
      setIsConsentOpen(true);
    }
  };

  // Build HTML for all unconsented studies at once
  const consentContentHtml = useMemo(() => {
    if (studies.length === 0) {
      return `<p>You are not enrolled in any studies. Please enroll in a study to connect your FitBit data.</p>`;
    }
    if (unconsentedStudies.length === 0) {
      return `<p>You have already consented to all your studies.</p>`;
    }

    // Build a combined block of all unconsented study info
    let content = "";
    unconsentedStudies.forEach(study => {
      // This gets sanitized in QuillView
      const consentText = study.consentInformation || defaultConsentContentText || "";    
      content += `<h4>${study.studyName}</h4><div>${consentText}</div>`;
    });
    return content;
  }, [studies, unconsentedStudies]);

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
                <span className="absolute top-full mt-2 text-danger text-xs right-0">
                  {consentError}
                </span>
              )}
            </div>
          )}
        </CardContentRow>

        {/* Information to display if the Fitbit API is connected */}
        {fitbitConnected && (
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
        )}
      </Card>

      {/* Data summary and study information to show if Fitbit is connected */}
      {fitbitConnected && (
        <Card width="sm">
          <CardContentRow>
            <Title>Your Data</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <div className="flex flex-col mb-4">
                <span>Data being collected:</span>
                {scope.map((s, i) => (
                  <span key={i} className="font-bold capitalize">
                    &nbsp;&nbsp;&nbsp;&nbsp;{s}
                  </span>
                ))}
              </div>
              <div className="flex flex-col">
                <span>Between these dates:</span>
                <span className="font-bold">
                  &nbsp;&nbsp;&nbsp;&nbsp;{startDate ? startDate.toLocaleDateString() : "N/A"}
                  {" - "}
                  {endDate ? endDate.toLocaleDateString() : "N/A"}
                </span>
              </div>
            </div>
          </CardContentRow>
          <CardContentRow>
            <Title>Why are we collecting your data?</Title>
          </CardContentRow>
          <CardContentRow>
            <QuillView
              className="text-sm"
              content={studies.length > 0
                ? (studies[0].dataSummary || "No data summary available.")
                : "No data summary available."
              } />
          </CardContentRow>
          <CardContentRow>
            <Title>Manage my data</Title>
          </CardContentRow>
          <CardContentRow>
            <LinkComponent onClick={handleClickManageData}>
              Request deletion of my account or data.
            </LinkComponent>
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
      )}

      {/* Consent Modal */}
      <ConsentModal
        isOpen={isConsentOpen}
        onAccept={handleConsentAccept}
        onDeny={handleConsentClose}
        onClose={handleConsentClose}
        contentHtml={consentContentHtml}
      />
    </>
  );
};
