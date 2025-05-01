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

import { useEffect, useState } from "react";
import Right from "../icons/right.svg?react";
import { SmallLoader } from "./loader/loader";
import { getAccess } from "../utils";
import { Card } from "./cards/card";
import { CardContentRow } from "./cards/cardContentRow";
import { ViewContainer } from "./containers/viewContainer/viewContainer";
import { Link } from "react-router-dom";

/**
 * Home component: renders available apps for the user
 */
export const Apps = () => {
  const [apps, setApps] = useState([
    {
      breadcrumbs: ["Ditti App"],
      name: "Ditti App Dashboard",
      link: "/coordinator/ditti",
    },
    {
      breadcrumbs: ["Wearable Dashboard"],
      name: "Wearable Dashboard",
      link: "/coordinator/wearable",
    },
    {
      breadcrumbs: ["Admin Dashboard", "Accounts"],
      name: "Admin Dashboard",
      link: "/coordinator/admin",
    },
  ]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // check whether the user can view the admin dashboard
    const admin = getAccess(1, "View", "Admin Dashboard").catch(() => {
      setApps((prevApps) =>
        prevApps.filter((app) => app.name !== "Admin Dashboard")
      );
    });

    // check whether the user can view the ditti app dashboard
    const ditti = getAccess(2, "View", "Ditti App Dashboard").catch(() => {
      setApps((prevApps) =>
        prevApps.filter((app) => app.name !== "Ditti App Dashboard")
      );
    });

    // check whether the user can view the ditti app dashboard
    const wear = getAccess(3, "View", "Wearable Dashboard").catch(() => {
      setApps((prevApps) =>
        prevApps.filter((app) => app.name !== "Wearable Dashboard")
      );
    });

    // when all promises resolve, hide the loader
    void Promise.all([admin, ditti, wear]).then(() => {
      setLoading(false);
    });
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
          className="hover:ring-inse cursor-pointer hover:ring hover:ring-light"
        >
          <Link to={app.link}>
            <CardContentRow>
              <p className="text-xl">{app.name}</p>
            </CardContentRow>
            <div className="mt-24 flex w-full justify-end">
              <Right />
            </div>
          </Link>
        </Card>
      ))}
    </ViewContainer>
  );
};
