// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useContext } from "react";
import { IBreadcrumb, NavbarContextType } from "../interfaces";
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

  useEffect(() => {
    let updatedBreadcrumbs = matches
      .filter(match => match.handle ? (match.handle as IHandle).breadcrumbs : false)
      .flatMap(match => (match.handle as IHandle).breadcrumbs);

    if (studyCrumb) {
      updatedBreadcrumbs = updatedBreadcrumbs.map(b =>
        b.name === "<Study>" ? studyCrumb : b
      );
    }

    setBreadcrumbs(updatedBreadcrumbs);
  }, [matches, studyCrumb]);

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
