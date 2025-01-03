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
