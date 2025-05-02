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

export const ListView = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="flex h-[calc(calc(100vh-8rem)-1px)] w-full flex-col
        overflow-scroll overflow-x-hidden bg-white lg:bg-[transparent] lg:px-12"
    >
      {children}
    </div>
  );
};
