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
import { createContext, useState, PropsWithChildren, useContext, createRef } from "react";
import { FlashMessageContextType, IFlashMessage } from "../interfaces";
import FlashMessage, { FlashMessageVariant } from "../components/flashMessage/flashMessage";

export const FlashMessageContext = createContext<FlashMessageContextType | undefined>(undefined);


// FlashMessageContextProvider component that wraps children with studies context.
export default function FlashMessageContextProvider({
  children
}: PropsWithChildren<unknown>) {
  const [flashMessages, setFlashMessages] = useState<IFlashMessage[]>([]);

  const flashMessage = (msg: React.ReactElement, variant: FlashMessageVariant) => {
    const updatedFlashMessages = [...flashMessages];
    const containerRef = createRef<HTMLDivElement>();

    // Set the element's key to 0 or the last message's key + 1
    const id = updatedFlashMessages.length
      ? updatedFlashMessages[updatedFlashMessages.length - 1].id + 1
      : 0;

    const element =
      <FlashMessage
        key={id}
        variant={variant}
        containerRef={containerRef}
        onClose={() => closeMessage(id)}>
          {msg}
      </FlashMessage>;

    // Add the message to the page
    updatedFlashMessages.push({ id, element, containerRef });
    setFlashMessages(updatedFlashMessages);
  }

  const closeMessage = (id: number) => {
    setFlashMessages(prevFlashMessages => {
      let updatedFlashMessages = [...prevFlashMessages];
      updatedFlashMessages = updatedFlashMessages.filter((fm) => fm.id != id);
      return updatedFlashMessages;
    });
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
