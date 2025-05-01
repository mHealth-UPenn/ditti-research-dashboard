import { useEffect, useState } from "react";
import { getAccess } from "../../utils";
import { Card } from "../cards/card";
import { ViewContainer } from "../containers/viewContainer/viewContainer";
import { CardContentRow } from "../cards/cardContentRow";
import { Title } from "../text/title";
import { ActiveIcon } from "../icons/activeIcon";
import { useStudies } from "../../hooks/useStudies";
import { SmallLoader } from "../loader/loader";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { LinkComponent } from "../links/linkComponent";
import { Link } from "react-router-dom";
import { WearableStudyDetails } from "./wearableDashboard.types";

export function WearableStudies() {
  const [canViewWearableData, setCanViewWearableData] = useState<Set<number>>(
    new Set()
  );
  const [loading, setLoading] = useState(true);

  const { studies, studiesLoading } = useStudies();
  const { studySubjects, studySubjectLoading } = useCoordinatorStudySubjects();

  // The summary details to show for each study
  const wearableDetails: WearableStudyDetails = {};
  for (const ss of studySubjects) {
    // Count `hasApi` if the current subject has at least 1 API connected and is active in at least one study
    const hasApi = Number(
      Boolean(ss.apis.length) &&
        ss.studies.some((s) => new Date(s.expiresOn) > new Date())
    );

    for (const join of ss.studies) {
      if (
        Object.prototype.hasOwnProperty.call(wearableDetails, join.study.id)
      ) {
        wearableDetails[join.study.id].numSubjects += 1;
        wearableDetails[join.study.id].numSubjectsWithApi += hasApi;
      } else {
        wearableDetails[join.study.id] = {
          numSubjects: 1,
          numSubjectsWithApi: hasApi,
        };
      }
    }
  }

  // Get which studies the current user can view wearable data for on load
  useEffect(() => {
    const updatedCanViewWearableData = new Set<number>();
    const promises: Promise<unknown>[] = [];

    studies.forEach((s) =>
      promises.push(
        getAccess(3, "View", "Wearable Data", s.id)
          .then(() => updatedCanViewWearableData.add(s.id))
          .catch(() => updatedCanViewWearableData.delete(s.id))
      )
    );

    Promise.all(promises)
      .then(() => {
        setCanViewWearableData(updatedCanViewWearableData);
      })
      .catch(console.error)
      .finally(() => {
        setLoading(false);
      });
  }, [studies]);

  if (loading || studiesLoading || studySubjectLoading) {
    return (
      <ViewContainer>
        <Card width="md">
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <ViewContainer>
      <Card width="md">
        <CardContentRow>
          <Title>Studies</Title>
        </CardContentRow>
        {
          // For each study the user has access to
          studies.map((s) => {
            return (
              <CardContentRow key={s.id} className="border-b border-light">
                <div className="flex items-start">
                  {/* Active icon */}
                  {canViewWearableData.has(s.id) ? (
                    <ActiveIcon active={true} className="mr-2" />
                  ) : (
                    // Optimistic hydration
                    <ActiveIcon active={false} className="mr-2" />
                  )}

                  {/* link to study summary */}
                  <div className="flex flex-col">
                    <Link
                      to={`/coordinator/wearable/study?sid=${String(s.id)}`}
                    >
                      <LinkComponent>{s.acronym}</LinkComponent>
                    </Link>
                    <span className="text-sm">{s.name}</span>
                  </div>
                </div>

                {/* Study summary details */}
                <div className="flex flex-col">
                  <div className="text-sm font-bold">
                    {s.id in wearableDetails
                      ? wearableDetails[s.id].numSubjectsWithApi
                      : 0}{" "}
                    subjects with connected APIs
                  </div>
                  <div className="text-sm">
                    {s.id in wearableDetails
                      ? wearableDetails[s.id].numSubjects
                      : 0}{" "}
                    enrolled subjects
                  </div>
                </div>
              </CardContentRow>
            );
          })
        }
      </Card>
    </ViewContainer>
  );
}
