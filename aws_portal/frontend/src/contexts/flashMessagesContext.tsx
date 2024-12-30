// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext, createRef } from "react";
import { makeRequest } from "../utils";
import { IBreadcrumb, FlashMessageContextType, Study, IFlashMessage } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";
import { useMatches } from "react-router-dom";
import FlashMessage, { FlashMessageVariant } from "../components/flashMessage/flashMessage";

export const FlashMessageContext = createContext<FlashMessageContextType | undefined>(undefined);

interface IHandle {
  breadcrumbs: IBreadcrumb[];
}


// FlashMessageContextProvider component that wraps children with studies context.
export default function FlashMessageContextProvider({
  children
}: PropsWithChildren<unknown>) {
  const [flashMessages, setFlashMessages] = useState<IFlashMessage[]>([]);

  const flashMessage = (msg: React.ReactElement, variant: FlashMessageVariant) => {
    const updatedFlashMessages = [...flashMessages];
    const containerRef = createRef<HTMLDivElement>();
    const closeRef = createRef<HTMLDivElement>();

    // Set the element's key to 0 or the last message's key + 1
    const id = updatedFlashMessages.length
      ? updatedFlashMessages[updatedFlashMessages.length - 1].id + 1
      : 0;

    const element =
      <FlashMessage
        key={id}
        variant={variant}
        containerRef={containerRef}
        closeRef={closeRef}>
          {msg}
      </FlashMessage>;

    if (closeRef.current) {
      closeRef.current.onclick = () => closeMessage(id);
    }

    if (containerRef.current) {
      setTimeout(() => containerRef.current!.style.opacity = "0", 3000);
      setTimeout(() => closeMessage(id), 5000);
    }

    // Add the message to the page
    updatedFlashMessages.push({ id, element, containerRef, closeRef });
    setFlashMessages(updatedFlashMessages);
  }

  const closeMessage = (id: number) => {
    let updatedFlashMessages = [...flashMessages];
    updatedFlashMessages = updatedFlashMessages.filter((fm) => fm.id != id);
    setFlashMessages(updatedFlashMessages);
  }

  return (
    <FlashMessageContext.Provider value={{ flashMessages, flashMessage }}>
      {children}
    </FlashMessageContext.Provider>
  );
}


// Hook for accessing context data
export function useFlashMessageContext() {
  const context = useContext(FlashMessageContext);
  if (!context) {
    throw new Error("useFlashMessageContext must be used within a FlashMessageContext provider");
  }
  return context;
}
