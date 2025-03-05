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

// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useContext } from "react";
import { IBreadcrumb, NavbarContextType } from "../interfaces";
import { useMatches } from "react-router-dom";

export const NavbarContext = createContext<NavbarContextType | undefined>(undefined);

interface IHandle {
  breadcrumbs: IBreadcrumb[];
}


const formatString = (template: string, values: Record<string, string>): string => {
  return template.replace(/\{(\w+)\}/g, (_, key) => values[key] || "");
}


// NavbarContextProvider component that wraps children with studies context.
export default function NavbarContextProvider({
  children
}: PropsWithChildren<unknown>) {
  const matches = useMatches();

  const [breadcrumbs, setBreadcrumbs] = useState<IBreadcrumb[]>([]);
  const [studySlug, setStudySlug] = useState("");
  const [sidParam, setSidParam] = useState("");
  const [dittiIdParam, setDittiIdParam] = useState("");

  // Format any breadcrumbs with `studySlug`, `sidParam`, and `dittiIdParam`
  useEffect(() => {
    let updatedBreadcrumbs = matches
      .filter(match => match.handle ? (match.handle as IHandle).breadcrumbs : false)
      .flatMap(match => (match.handle as IHandle).breadcrumbs);

    const formatValues = {
      study: studySlug,
      sid: sidParam,
      dittiId: dittiIdParam,
    };
    
    updatedBreadcrumbs = updatedBreadcrumbs.map(breadcrumb => ({
      name: formatString(breadcrumb.name, formatValues),
      link: breadcrumb.link
        ? formatString(breadcrumb.link, formatValues)
        : null,
    }));

    setBreadcrumbs(updatedBreadcrumbs);
  }, [matches, studySlug, dittiIdParam]);

  return (
    <NavbarContext.Provider value={{
        breadcrumbs,
        setStudySlug,
        setSidParam,
        setDittiIdParam }}>
          {children}
    </NavbarContext.Provider>
  );
}


// Hook for accessing context data
export function useNavbarContext() {
  const context = useContext(NavbarContext);
  if (!context) {
    throw new Error("useNavbarContext must be used within a NavbarContext provider");
  }
  return context;
}
