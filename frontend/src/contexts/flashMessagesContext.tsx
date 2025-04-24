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
import { createContext, useState, PropsWithChildren, createRef } from "react";
import {
  FlashMessageContextValue,
  FlashMessageModel,
} from "./flashMessagesContext.types";
import { FlashMessage } from "../components/flashMessage/flashMessage";
import { FlashMessageVariant } from "../components/flashMessage/flashMessage.types";

export const FlashMessageContext = createContext<
  FlashMessageContextValue | undefined
>(undefined);

// FlashMessageContextProvider component that wraps children with studies context.
export function FlashMessageContextProvider({
  children,
}: PropsWithChildren<unknown>) {
  const [flashMessages, setFlashMessages] = useState<FlashMessageModel[]>([]);

  const flashMessage = (
    msg: React.ReactElement,
    variant: FlashMessageVariant
  ) => {
    const updatedFlashMessages = [...flashMessages];
    const containerRef = createRef<HTMLDivElement>();

    // Set the element's key to 0 or the last message's key + 1
    const id = updatedFlashMessages.length
      ? updatedFlashMessages[updatedFlashMessages.length - 1].id + 1
      : 0;

    const element = (
      <FlashMessage
        key={id}
        variant={variant}
        containerRef={containerRef}
        onClose={() => closeMessage(id)}
      >
        {msg}
      </FlashMessage>
    );

    // Add the message to the page
    updatedFlashMessages.push({ id, element, containerRef });
    setFlashMessages(updatedFlashMessages);
  };

  const closeMessage = (id: number) => {
    setFlashMessages((prevFlashMessages) => {
      let updatedFlashMessages = [...prevFlashMessages];
      updatedFlashMessages = updatedFlashMessages.filter((fm) => fm.id != id);
      return updatedFlashMessages;
    });
  };

  return (
    <FlashMessageContext.Provider value={{ flashMessages, flashMessage }}>
      {children}
    </FlashMessageContext.Provider>
  );
}
