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

import { Header } from "../header";
import { Navbar } from "../navbar";
import "./dashboard.css";
import { Outlet } from "react-router-dom";
import { NavbarContextProvider } from "../../contexts/navbarContext";
import { useFlashMessages } from "../../hooks/useFlashMessages";

export const Dashboard = () => {
  const { flashMessages } = useFlashMessages();

  return (
    <main className="flex h-screen flex-col">
      {/* header with the account menu  */}
      <Header />
      <div className="flex max-h-[calc(100vh-4rem)] grow">
        {/* list of studies on the left of the screen */}
        {/* <StudiesMenu
          setView={setStudy}
          flashMessage={flashMessage}
          handleClick={setView}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          goBack={goBack} /> */}

        {/* main dashboard */}
        <div
          className="max-w-[calc(100vw-16rem) relative flex grow flex-col
            overflow-hidden"
        >
          <NavbarContextProvider>
            <Navbar />

            {/* flash messages */}
            {!!flashMessages.length && (
              <div className="flash-message-container">
                {flashMessages.map((fm) => fm.element)}
              </div>
            )}
            <Outlet />
          </NavbarContextProvider>
        </div>
      </div>
    </main>
  );
};
