import * as React from "react";
import { ReactComponent as Check } from "../../icons/check.svg";
import Button, { ButtonProps } from "./button";

/**
 * id: an id of the item that will be toggled by the button
 * getActive: gets whether the toggled item is currently active
 * add: adds the item
 * remove: removes the item
 */
interface ToggleButtonProps extends ButtonProps {
  id: number;
  getActive: (id: number) => boolean;
  add: (id: number, callback: (active: boolean) => void) => void;
  remove: (id: number, callback: (active: boolean) => void) => void;
}

const ToggleButton: React.FC<ToggleButtonProps> = ({
  id,
  getActive,
  add,
  remove,
  fullWidth,
  fullHeight,
}) => {
  // get whether the toggled item is currently active
  const [active, setActive] = React.useState<boolean>(getActive(id));
  
  /**
   * Update the button's active state
   */
  const update = (active: boolean) => {
    setActive(active);
  };

  return active ? (
    <Button
      variant="success"
      onClick={() => remove(id, update)}
      fullWidth={fullWidth}
      fullHeight={fullHeight}>
        <Check />
    </Button>
  ) : (
    <Button
      variant="secondary"
      onClick={() => add(id, update)}
      fullWidth={fullWidth}
      fullHeight={fullHeight}>
        Add +
    </Button>
  );
};

export default ToggleButton;
