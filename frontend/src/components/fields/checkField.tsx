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

import { CheckFieldProps } from "./fields.types";

export const CheckField = ({
  id,
  prefill,
  label,
  onChange,
}: CheckFieldProps) => {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-1 hidden md:flex">&nbsp;</div>
      <div className="flex grow items-center">
        <div>
          {label && (
            <label className="mr-4" htmlFor={id}>
              {label}
            </label>
          )}
          <input
            type="checkbox"
            checked={prefill}
            onChange={
              onChange
                ? (e) => {
                    onChange((e.target as HTMLInputElement).checked);
                  }
                : () => null
            }
          />
        </div>
      </div>
    </div>
  );
};
