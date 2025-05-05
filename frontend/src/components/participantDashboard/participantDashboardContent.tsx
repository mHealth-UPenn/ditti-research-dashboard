/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
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
import { httpClient } from "../../lib/http";
import { ParticipantStudy, ResponseBody } from "../../types/api";
import { QuillView } from "../containers/quillView/quillView";
import { useApiHandler } from "../../hooks/useApiHandler";

const defaultConsentContentText =
  "By accepting, you agree that your data will be used solely for research purposes described in our terms. You can withdraw consent at any time.";

export const ParticipantDashboardContent = () => {
  const [isConsentOpen, setIsConsentOpen] = useState<boolean>(false);
  const [consentError, setConsentError] = useState<string>("");
  const [studiesNeedingConsent, setStudiesNeedingConsent] = useState<
    ParticipantStudy[]
  >([]);

  const { dittiId } = useAuth();
  const { studies, apis, studySubjectLoading, refetch } = useStudySubjects();

  const { safeRequest: safeUpdateConsent } = useApiHandler({
    // Success message handled implicitly by redirect/UI change
    // Error message handled by hook + specific error state
    onError: (error) => {
      setConsentError(error.message || "Failed to update consent.");
    },
    onSuccess: async () => {
      setIsConsentOpen(false);
      setConsentError("");
      // Refetch data to ensure consistency
      await refetch();
      handleRedirect();
    },
  });

  // Recalculate studies needing consent when the main studies list changes
  useEffect(() => {
    const filteredStudies = studies.filter((s) => !s.didConsent);
    if (filteredStudies.length > 0) {
      setStudiesNeedingConsent(filteredStudies);
    } else {
      setStudiesNeedingConsent([]);
    }
  }, [studies]); // Depend only on studies

  // Use the earliest startsOn date as the beginning of data collection
  const startDate = useMemo(() => {
    if (studies.length === 0) return null;
    return new Date(
      Math.min(...studies.map((s) => new Date(s.startsOn).getTime()))
    );
  }, [studies]);

  // Use the latest expiresOn date as the end of data collection
  const endDate = useMemo(() => {
    if (studies.length === 0) return null;
    const validTimestamps = studies
      .map((s) => (s.expiresOn ? new Date(s.expiresOn).getTime() : null))
      .filter((timestamp) => timestamp !== null);

    if (validTimestamps.length === 0) {
      return null; // No valid dates
    }

    return new Date(Math.max(...validTimestamps)); // Get the latest date
  }, [studies]);

  const scope = useMemo(
    () => [...new Set(apis.map((api) => api.scope).flat())],
    [apis]
  );

  // For now assume we are only connecting Fitbit API
  const fitbitConnected = apis.length > 0;

  // Redirect after authenticating with Fitbit
  const handleRedirect = () => {
    window.location.href = `${String(import.meta.env.VITE_FLASK_SERVER)}/api/fitbit/authorize`;
  };

  // Redirect to form for requesting deletion of account
  const handleClickManageData = () => {
    window.location.href =
      "https://hosting.med.upenn.edu/forms/DittiApp/view.php?id=10677";
  };

  const handleConsentAccept = async () => {
    if (studiesNeedingConsent.length === 0) {
      setIsConsentOpen(false);
      return;
    }

    setConsentError(""); // Clear previous errors

    await safeUpdateConsent(async () => {
      // Map each study consent update to an httpClient call
      const consentPromises = studiesNeedingConsent.map((study) =>
        httpClient.request<ResponseBody>( // Use httpClient
          `/participant/study/${String(study.studyId)}/consent`,
          {
            method: "PATCH",
            data: { didConsent: true }, // Use data property
          }
        )
      );

      // Wait for all consent updates to complete
      await Promise.all(consentPromises);

      // Error/Success handling is now managed by the useApiHandler hook
    });
  };

  const handleConsentClose = () => {
    setIsConsentOpen(false);
    // Set a specific error message related to consent denial
    setConsentError(
      "You must accept the consent terms to connect your Fitbit API. Please try again."
    );
  };

  // If there are no studies needing consent, proceed to Fitbit flow
  // otherwise, prompt them to consent
  const handleConnectFitBitClick = () => {
    setConsentError(""); // Clear consent error on attempt
    if (studiesNeedingConsent.length === 0) {
      handleRedirect();
    } else {
      setIsConsentOpen(true);
    }
  };

  // Build HTML for all studies needing consent at once
  const consentContentHtml = useMemo(() => {
    if (studiesNeedingConsent.length === 0) {
      return `<p>You have already consented to all your studies.</p>`;
    }

    // Build a combined block of all study info needing consent
    let content = "";
    studiesNeedingConsent.forEach((study) => {
      // This gets sanitized in QuillView
      const consentText = study.consentInformation ?? defaultConsentContentText;
      content += `<h4>${study.studyName}</h4><div>${consentText}</div>`;
    });
    return content;
  }, [studiesNeedingConsent]);

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
            <div className="relative flex flex-col items-end">
              <Button onClick={handleConnectFitBitClick} rounded={true}>
                Connect FitBit
              </Button>
              {/* Error message without reserving space */}
              {consentError && (
                <span
                  className="absolute right-0 top-full mt-2 text-xs text-danger"
                >
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
              <div className="mb-4 flex flex-col">
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
                  &nbsp;&nbsp;&nbsp;&nbsp;
                  {startDate ? startDate.toLocaleDateString() : "N/A"}
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
              content={
                studies.length > 0
                  ? (studies[0].dataSummary ?? "No data summary available.")
                  : "No data summary available."
              }
            />
          </CardContentRow>
          <CardContentRow>
            <Title>Manage my data</Title>
          </CardContentRow>
          <CardContentRow>
            <LinkComponent
              onClick={() => {
                handleClickManageData();
              }}
            >
              Request deletion of my account or data.
            </LinkComponent>
          </CardContentRow>
          <CardContentRow>
            <Title>Legal</Title>
          </CardContentRow>
          <CardContentRow>
            <div className="flex flex-col">
              <RouterLink className="link" to="/terms-of-use">
                Terms of Use
              </RouterLink>
              <RouterLink className="link" to="/privacy-policy">
                Privacy Policy
              </RouterLink>
            </div>
          </CardContentRow>
        </Card>
      )}

      {/* Consent Modal */}
      <ConsentModal
        isOpen={isConsentOpen}
        onAccept={() => void handleConsentAccept()}
        onDeny={handleConsentClose}
        onClose={handleConsentClose}
        contentHtml={consentContentHtml}
      />
    </>
  );
};
