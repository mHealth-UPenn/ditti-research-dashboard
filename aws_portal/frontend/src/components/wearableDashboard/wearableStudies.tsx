import React, { useEffect, useState } from "react";
import { Study, ViewProps } from "../../interfaces";
import { getAccess } from "../../utils";
import Card from "../cards/card";
import ViewContainer from "../containers/viewContainer";
import CardContentRow from "../cards/cardContentRow";
import Title from "../text/title";
import ActiveIcon from "../icons/activeIcon";
import Link from "../links/link";


export default function WearableStudies({ handleClick }: ViewProps) {
  const [canViewWearableData, setCanViewWearableData] = useState<Set<number>>(new Set());
  const studies: Study[] = [];

  useEffect(() => {
    const updateCanViewWearableData = async () => {
      const updatedCanViewWearableData: Set<number> = new Set();
      const promises = studies.map(s => {
        return getAccess(2, "View", "Wearable Data", s.id)
          .then(() => updatedCanViewWearableData.add(s.id))
          .catch(() => updatedCanViewWearableData.delete(s.id));
      });
      await Promise.all(promises)
      setCanViewWearableData(updatedCanViewWearableData)
    }
    updateCanViewWearableData();
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
        <React.Fragment />
        // <WearableStudySummary
        //   flashMessage={flashMessage}
        //   handleClick={handleClick}
        //   goBack={goBack}
        //   studyId={study.id}
        // />
      );

      handleClick([study.acronym], view, false);
    }
  };

  // if (loading) {
  //   return (
  //     <ViewContainer>
  //       <Card width="md">
  //         <SmallLoader />
  //       </Card>
  //     </ViewContainer>
  //   );
  // }

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
              </CardContentRow>
            );
          })
        }
      </Card>
    </ViewContainer>
  );
};
