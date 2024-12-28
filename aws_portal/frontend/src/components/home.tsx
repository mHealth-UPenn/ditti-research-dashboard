import React, { useEffect, useState } from "react";
import { ReactComponent as Right } from "../icons/right.svg";
import { ViewProps } from "../interfaces";
import StudiesView from "./dittiApp/studies";
import Accounts from "./adminDashboard/accounts";
import { SmallLoader } from "./loader";
import { getAccess } from "../utils";
import Card from "./cards/card";
import CardContentRow from "./cards/cardContentRow";
import ViewContainer from "./containers/viewContainer";
import WearableStudies from "./wearableDashboard/wearableStudies";

/**
 * Home component: renders available apps for the user
 */
const Home: React.FC<ViewProps> = ({
  flashMessage,
  goBack,
  handleClick
}) => {
  // apps are hardcoded here because for now there is no real need to add more
  // than two
  const [apps, setApps] = useState([
    {
      breadcrumbs: ["Ditti App"],
      name: "Ditti App Dashboard",
      view: (
        <StudiesView
          handleClick={handleClick}
          goBack={goBack}
          flashMessage={flashMessage} />
      ),
    },
    {
      breadcrumbs: ["Admin Dashboard", "Accounts"],
      name: "Admin Dashboard",
      view: (
        <Accounts />
      ),
    },
    {
      breadcrumbs: ["Wearable Dashboard"],
      name: "Wearable Dashboard",
      view: (
        <WearableStudies
          handleClick={handleClick}
          goBack={goBack}
          flashMessage={flashMessage} />
      ),
    },
  ]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // check whether the user can view the admin dashboard
    const admin = getAccess(1, "View", "Admin Dashboard").catch(() => {
      setApps((prevApps) => prevApps.filter((app) => app.name !== "Admin Dashboard"));
    });

    // check whether the user can view the ditti app dashboard
    const ditti = getAccess(2, "View", "Ditti App Dashboard").catch(() => {
      setApps((prevApps) => prevApps.filter((app) => app.name !== "Ditti App Dashboard"));
    });

    // check whether the user can view the ditti app dashboard
    const wear = getAccess(3, "View", "Wearable Dashboard").catch(() => {
      setApps((prevApps) => prevApps.filter((app) => app.name !== "Wearable Dashboard"));
    });

    // when all promises resolve, hide the loader
    Promise.all([admin, ditti, wear]).then(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <ViewContainer>
        <Card width="sm">
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <ViewContainer>
      {apps.map((app, i) => (
        <Card
          key={i}
          width="sm"
          className="cursor-pointer hover:ring hover:ring-inse hover:ring-light"
          onClick={() => handleClick(app.breadcrumbs, app.view)}>
            <CardContentRow>
              <p className="text-xl">{app.name}</p>
            </CardContentRow>
            <div className="flex justify-end w-full mt-24">
              <Right />
            </div>
        </Card>
      ))}
    </ViewContainer>
  );
};

export default Home;
