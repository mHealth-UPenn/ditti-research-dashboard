import { useContext } from "react";
import { FlashMessageContext } from "../contexts/flashMessagesContext";
import { FlashMessageContextType } from "../interfaces";

// Hook for accessing context data
export function useFlashMessages(): FlashMessageContextType {
  const context = useContext(FlashMessageContext);
  if (!context) {
    throw new Error("useFlashMessages must be used within a FlashMessageContext provider");
  }
  return context;
}
