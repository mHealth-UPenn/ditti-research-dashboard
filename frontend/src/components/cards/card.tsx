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

import { PropsWithChildren } from "react";
import { CardProps } from "./cards.types";

const widthMap = {
  lg: "w-full lg:px-6",
  md: "w-full md:px-6 lg:w-2/3",
  sm: "w-full md:px-6 md:w-1/2 lg:w-1/3",
};

export const Card = ({
  width = "lg",
  className = "",
  onClick,
  children,
}: PropsWithChildren<CardProps>) => {
  return (
    <div className={widthMap[width]}>
      <div
        className={`mb-8 w-full overflow-x-scroll rounded-xl bg-white p-8
          shadow-lg lg:mb-0 ${className}`}
        onClick={onClick}
      >
        {children}
      </div>
    </div>
  );
};
