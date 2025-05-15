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
  return template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] || "");
};

// NavbarContextProvider component that wraps children with studies context.
export function NavbarContextProvider({ children }: PropsWithChildren) {
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
  }, [matches, studySlug, dittiIdParam, sidParam]);

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
