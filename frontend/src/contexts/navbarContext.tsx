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

import { createContext, useState, useEffect, PropsWithChildren } from "react";
import { useMatches } from "react-router-dom";
import { NavbarContextValue, Breadcrumb, Handle } from "./navbarContext.types";

export const NavbarContext = createContext<NavbarContextValue | undefined>(
  undefined
);

const formatString = (
  template: string,
  values: Record<string, string>
): string => {
  return template.replace(/\{(\w+)\}/g, (_, key) => values[key] || "");
};

// NavbarContextProvider component that wraps children with studies context.
export function NavbarContextProvider({
  children,
}: PropsWithChildren<unknown>) {
  const matches = useMatches();

  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([]);
  const [studySlug, setStudySlug] = useState("");
  const [sidParam, setSidParam] = useState("");
  const [dittiIdParam, setDittiIdParam] = useState("");

  // Format any breadcrumbs with `studySlug`, `sidParam`, and `dittiIdParam`
  useEffect(() => {
    let updatedBreadcrumbs = matches
      .filter((match) =>
        match.handle ? (match.handle as Handle).breadcrumbs : false
      )
      .flatMap((match) => (match.handle as Handle).breadcrumbs);

    const formatValues = {
      study: studySlug,
      sid: sidParam,
      dittiId: dittiIdParam,
    };

    updatedBreadcrumbs = updatedBreadcrumbs.map((breadcrumb) => ({
      name: formatString(breadcrumb.name, formatValues),
      link: breadcrumb.link
        ? formatString(breadcrumb.link, formatValues)
        : null,
    }));

    setBreadcrumbs(updatedBreadcrumbs);
  }, [matches, studySlug, dittiIdParam]);

  return (
    <NavbarContext.Provider
      value={{
        breadcrumbs,
        setStudySlug,
        setSidParam,
        setDittiIdParam,
      }}
    >
      {children}
    </NavbarContext.Provider>
  );
}
