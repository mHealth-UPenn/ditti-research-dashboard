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

import Header from "./header";
import Navbar from "./navbar";
import "./dashboard.css";
import { Outlet } from "react-router-dom";
import NavbarContextProvider from "../contexts/navbarContext";
import { useFlashMessageContext } from "../contexts/flashMessagesContext";


const Dashboard = () => {
  const { flashMessages } = useFlashMessageContext();

  return (
    <main className="flex flex-col h-screen">
      {/* header with the account menu  */}
      <Header />
      <div className="flex flex-grow max-h-[calc(100vh-4rem)]">

        {/* list of studies on the left of the screen */}
        {/* <StudiesMenu
          setView={setStudy}
          flashMessage={flashMessage}
          handleClick={setView}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          goBack={goBack} /> */}

        {/* main dashboard */}
        <div className="flex flex-col flex-grow max-w-[calc(100vw-16rem) overflow-hidden relative">
          <NavbarContextProvider>
            <Navbar />

            {/* flash messages */}
            {!!flashMessages.length &&
              <div className="flash-message-container">
                {flashMessages.map((fm) => fm.element)}
              </div>
            }
            <Outlet />
          </NavbarContextProvider>
        </div>
      </div>
    </main>
  );
};


export default Dashboard;
