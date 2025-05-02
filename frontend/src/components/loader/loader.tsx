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

import * as React from "react";
import { LoaderProps, FullLoaderProps } from "./loader.types";

const Loader = ({ style, msg }: LoaderProps) => {
  return (
    <div id="loader" style={style}>
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
