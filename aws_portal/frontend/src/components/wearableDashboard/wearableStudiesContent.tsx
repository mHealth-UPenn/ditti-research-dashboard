import { useEffect, useState } from "react";
import { IWearableDetails, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Card from "../cards/card";
import ViewContainer from "../containers/viewContainer";
import CardContentRow from "../cards/cardContentRow";
import Title from "../text/title";
import ActiveIcon from "../icons/activeIcon";
import Link from "../links/link";
import WearableStudySummary from "./wearableStudySummary";
import { useStudiesContext } from "../../contexts/studiesContext";
import { SmallLoader } from "../loader";


export default function WearableStudiesContent({
  flashMessage,
  goBack,
  handleClick
}: ViewProps) {
  const [canViewWearableData, setCanViewWearableData] = useState<Set<number>>(new Set());
  const [wearableDetails, setWearableDetails] = useState<IWearableDetails>({});
  const [loading, setLoading] = useState(true);
  
  const { studies, studiesLoading } = useStudiesContext();

  useEffect(() => {
    const updatedCanViewWearableData: Set<number> = new Set();

    const promises: Promise<unknown>[] = [];
    
    studies.forEach(s =>
      promises.push(
        getAccess(3, "View", "Wearable Data", s.id)
          .then(() => updatedCanViewWearableData.add(s.id))
          .catch(() => updatedCanViewWearableData.delete(s.id))
      )
    );

    promises.push(
      makeRequest("/db/get-study-wearable-details")
        .then((res: IWearableDetails) => setWearableDetails(res))
        .catch(() => console.error("Error retrieving study wearable details. Check permissions."))
    )
    Promise.all(promises).then(() => {
      setCanViewWearableData(updatedCanViewWearableData);
      setLoading(false);
    });
  }, [studies]);

  /**
   * Handle when a user clicks on a study
   * @param id - the study's database primary key
   */
  const handleClickStudy = (id: number): void => {
    // get the study
    const study = studies.find((s) => s.id === id);

    if (study) {
      // set the view
      const view = (
        <WearableStudySummary
          flashMessage={flashMessage}
          handleClick={handleClick}
          goBack={goBack}
          studyId={study.id}
        />
      );

      handleClick([study.acronym], view, false);
    }
  };

  if (loading || studiesLoading) {
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
          // for each study the user has access to
          studies.map((s) => {
            return (
              <CardContentRow key={s.id} className="border-b border-light">
                <div className="flex items-start">
                  {/* active tapping icon */}
                  {canViewWearableData.has(s.id) ?
                    <ActiveIcon active={true} className="mr-2" /> :
                    // Optimistic hydration
                    <ActiveIcon active={false} className="mr-2" />
                  }
                  {/* link to study summary */}
                  <div className="flex flex-col">
                    <Link onClick={() => handleClickStudy(s.id)}>
                      {s.acronym}
                    </Link>
                    <span className="text-sm">{s.name}</span>
                  </div>
                </div>
                <div className="flex flex-col">
                  <div className="text-sm font-bold">
                    {
                      s.id in wearableDetails
                      ? wearableDetails[s.id].numSubjectsWithApi
                      : 0
                    } subjects with connected APIs
                  </div>
                  <div className="text-sm">
                    {
                      s.id in wearableDetails
                      ? wearableDetails[s.id].numSubjects
                      : 0
                    } enrolled subjects
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
