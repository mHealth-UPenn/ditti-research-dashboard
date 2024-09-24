import React, { useEffect, useState } from "react";
import "./home.css";
import { ReactComponent as Right } from "../icons/right.svg";
import { AudioFile, TapDetails, ViewProps } from "../interfaces";
import StudiesView from "./dittiApp/studies";
import Accounts from "./adminDashboard/accounts";
import { SmallLoader } from "./loader";
import { getAccess } from "../utils";

/**
 * getTapsAsync: queries AWS for tap data
 * getTaps: get tap data locally after querying AWS
 */
interface HomeProps extends ViewProps {
  getTapsAsync: () => Promise<TapDetails[]>;
  getTaps: () => TapDetails[];
  getAudioFilesAsync: () => Promise<AudioFile[]>;
  getAudioFiles: () => AudioFile[];
}

/**
 * Home component: renders available apps for the user
 */
const Home: React.FC<HomeProps> = ({
  getTapsAsync,
  getTaps,
  getAudioFilesAsync,
  getAudioFiles,
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
          getTapsAsync={getTapsAsync}
          getTaps={getTaps}
          getAudioFilesAsync={getAudioFilesAsync}
          getAudioFiles={getAudioFiles}
          handleClick={handleClick}
          goBack={goBack}
          flashMessage={flashMessage}
        />
      ),
    },
    {
      breadcrumbs: ["Admin Dashboard", "Accounts"],
      name: "Admin Dashboard",
      view: (
        <Accounts
          handleClick={handleClick}
          goBack={goBack}
          flashMessage={flashMessage}
        />
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

    // when all promises resolve, hide the loader
    Promise.all([admin, ditti]).then(() => setLoading(false));
  }, []);

  /**
   * Render the apps on the page
   * @returns - apps to be rendered on the page
   */
  const getApps = () => {
    return apps.map((app, i) => (
      <div
        key={i}
        className="p-6 m-8 w-[24rem] bg-white shadow cursor-pointer bg-white shadow"
        onClick={() => handleClick(app.breadcrumbs, app.view)}
      >
        <div className="text-lg font-bold mb-24">
          <span>{app.name}</span>
        </div>
        <div className="float-right link-svg">
          <Right />
        </div>
      </div>
    ));
  };

  return (
    <div className="flex flex-col p-6 max-h-[calc(calc(100vh-8rem)-1px)] overflow-scroll overflow-x-hidden">
      <div className="flex items-start flex-wrap">
        {loading ? (
          <div className="p-6 m-8 w-[24rem] bg-white shadow">
            <SmallLoader />
          </div>
        ) : (
          getApps()
        )}
      </div>
    </div>
  );
};

export default Home;
