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
import { LoaderProps, FullLoaderProps } from "./loader.types";

const Loader = ({ style, msg }: LoaderProps) => {
  return (
    <div id="loader" style={style as React.CSSProperties}>
      <div className="lds-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      {msg ? <span>{msg}</span> : null}
    </div>
  );
};

export const SmallLoader = () => {
  return (
    <div className="loader-container">
      <Loader style={{}} />
    </div>
  );
};

export const FullLoader = ({ loading, msg }: FullLoaderProps) => {
  const loadingStyle: React.CSSProperties = {
    alignItems: "center",
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
    justifyContent: "center",
    height: "100%",
    position: "absolute",
    width: "100%",
    zIndex: 100,
  };

  const fadingStyle: React.CSSProperties = {
    alignItems: "center",
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
    justifyContent: "center",
    height: "100%",
    opacity: 0,
    position: "absolute",
    transition: "opacity 500ms ease-in",
    width: "100%",
    pointerEvents: "none",
    zIndex: 100,
  };

  const style = loading ? loadingStyle : fadingStyle;
  return <Loader style={style} msg={msg} />;
};
