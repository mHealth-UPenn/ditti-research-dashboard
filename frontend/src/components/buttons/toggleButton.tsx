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
