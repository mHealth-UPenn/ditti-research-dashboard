import { useContext } from "react";
import { FlashMessageContext } from "../contexts/flashMessagesContext";
import { FlashMessageContextValue } from "../contexts/flashMessagesContext.types";

/**
 * Hook for accessing context data
 * @returns The current flash messages context.
 */
export function useFlashMessages(): FlashMessageContextValue {
  const context = useContext(FlashMessageContext);
  if (!context) {
    throw new Error(
      "useFlashMessages must be used within a FlashMessageContext provider"
    );
  }
  return context;
}
