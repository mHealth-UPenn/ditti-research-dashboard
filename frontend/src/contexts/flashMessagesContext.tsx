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
export function FlashMessageContextProvider({ children }: PropsWithChildren) {
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
        onClose={() => {
          closeMessage(id);
        }}
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
