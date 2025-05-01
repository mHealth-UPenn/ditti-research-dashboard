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
