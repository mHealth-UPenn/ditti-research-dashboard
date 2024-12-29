// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { IBreadcrumb, NavbarContextType, Study } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";
import { useMatches } from "react-router-dom";

export const NavbarContext = createContext<NavbarContextType | undefined>(undefined);

interface IHandle {
  breadcrumbs: IBreadcrumb[];
}


// NavbarContextProvider component that wraps children with studies context.
export default function NavbarContextProvider({
  children
}: PropsWithChildren<unknown>) {
  const matches = useMatches();

  const [breadcrumbs, setBreadcrumbs] = useState<IBreadcrumb[]>([]);
  const [studyCrumb, setStudyCrumb] = useState<IBreadcrumb | null>(null);
  // const [breadcrumbsAreSet, setBreadcrumbsAreSet] = useState(false);

  // const breadcrumbTokens = new Set(["<Study>"]);

  useEffect(() => {
    // if (!breadcrumbs.length) {
    let updatedBreadcrumbs = matches
      .filter(match => match.handle ? (match.handle as IHandle).breadcrumbs : false)
      .flatMap(match => (match.handle as IHandle).breadcrumbs);

    if (studyCrumb) {
      updatedBreadcrumbs = updatedBreadcrumbs.map(b =>
        b.name === "<Study>" ? studyCrumb : b
      );
    }

    setBreadcrumbs(updatedBreadcrumbs);
    // } else {
    //   const newBreadcrumbs = (matches[matches.length - 1].handle as IHandle)?.breadcrumbs;

    //   if (newBreadcrumbs && newBreadcrumbs.length) {
    //     let updatedBreadcrumbs: IBreadcrumb[] = [];
    //     for (let i = 0; i < breadcrumbs.length; i++) {
    //       if (breadcrumbs[i].name == newBreadcrumbs[0].name) {
    //         updatedBreadcrumbs = breadcrumbs.slice(0, i);
    //         break;
    //       }
    //     }
    //     updatedBreadcrumbs.push(...newBreadcrumbs);
    //     setBreadcrumbs(updatedBreadcrumbs);
    //   }

    //   // if (!breadcrumbs.some(b => breadcrumbTokens.has(b.name))) {
    //   //   setBreadcrumbsAreSet(true);
    //   // }
    // }
  }, [matches, studyCrumb]);

  const addBreadcrumb = (breadcrumb: IBreadcrumb) => {
    const updatedBreadcrumbs = [...breadcrumbs];
    updatedBreadcrumbs.push(breadcrumb);
    setBreadcrumbs(updatedBreadcrumbs);
    // setBreadcrumbsAreSet(true);
  };

  return (
    <NavbarContext.Provider value={{ breadcrumbs, setStudyCrumb }}>
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
