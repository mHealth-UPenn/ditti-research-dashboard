import * as React from "react";
import Button, { ButtonProps } from "./button";
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

/**
 * id: an id of the item that will be toggled by the button
 * getActive: gets whether the toggled item is currently active
 * add: adds the item
 * remove: removes the item
 */
interface ToggleButtonProps extends ButtonProps {
  id: number;
  active: boolean;
  add: (id: number) => void;
  remove: (id: number) => void;
}

const ToggleButton: React.FC<ToggleButtonProps> = ({
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
        onClick={() => remove(id)}
        fullWidth={fullWidth}
        fullHeight={fullHeight}>
          <CheckCircleOutlineIcon />
      </Button>
    );
  }

  return (
    <Button
      variant="secondary"
      onClick={() => add(id)}
      fullWidth={fullWidth}
      fullHeight={fullHeight}>
        Add +
    </Button>
  );
};

export default ToggleButton;
