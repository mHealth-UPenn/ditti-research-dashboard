import * as React from "react";
import { Button } from "./button";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import { ToggleButtonProps } from "./buttons.types";

export const ToggleButton: React.FC<ToggleButtonProps> = ({
  id,
  active,
  add,
  remove,
  fullWidth,
  fullHeight,
}) => {
  if (active) {
    return (
      <Button
        variant="success"
        onClick={() => {
          remove(id);
        }}
        fullWidth={fullWidth}
        fullHeight={fullHeight}
      >
        <CheckCircleOutlineIcon />
      </Button>
    );
  }

  return (
    <Button
      variant="secondary"
      onClick={() => {
        add(id);
      }}
      fullWidth={fullWidth}
      fullHeight={fullHeight}
    >
      Add +
    </Button>
  );
};
