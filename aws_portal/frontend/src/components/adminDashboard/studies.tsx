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
import { useState, useEffect } from "react";
import { ResponseBody, Study } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import { SmallLoader } from "../loader";
import Button from "../buttons/button";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";

const COLUMNS: Column[] = [
  { name: "Acronym", searchable: true, sortable: true, width: 10 },
  { name: "Name", searchable: true, sortable: true, width: 30 },
  { name: "Ditti ID", searchable: true, sortable: true, width: 10 },
  { name: "Email", searchable: true, sortable: true, width: 20 },
  { name: "Default Enrollment Period", searchable: false, sortable: true, width: 15 },
  { name: "QI", searchable: false, sortable: true, width: 5 },
  { name: "", searchable: false, sortable: false, width: 10 },
];
import { Link } from "react-router-dom";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";

const Studies = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(true);
  const { flashMessage } = useFlashMessageContext();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check create, edit, and archive permissions
        await Promise.all([
          getAccess(1, "Create", "Studies").then(() => setCanCreate(true)),
          getAccess(1, "Edit", "Studies").then(() => setCanEdit(true)),
          getAccess(1, "Archive", "Studies").then(() => setCanArchive(true)),
          makeRequest("/admin/study?app=1").then((data) => setStudies(data))
        ]);
      } catch (error) {
        console.error("Error fetching permissions or data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    return studies.map((s: Study) => {
      const { acronym, dittiId, email, id, name, defaultExpiryDelta, isQi } = s;
      return [
        {
          contents: <span>{acronym}</span>,
          searchValue: acronym,
          sortValue: acronym
        },
        {
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name
        },
        {
          contents: <span>{dittiId}</span>,
          searchValue: dittiId,
          sortValue: dittiId
        },
        {
          contents: <span>{email}</span>,
          searchValue: email,
          sortValue: email
        },
        {
          contents: <span>{defaultExpiryDelta} days</span>,
          searchValue: defaultExpiryDelta.toString(),
          sortValue: defaultExpiryDelta
        },
        {
          contents: <span>{isQi ? "Yes" : "No"}</span>,
          searchValue: isQi ? "Yes" : "No",
          sortValue: isQi ? "Yes" : "No"
        },
        {
          contents: (
            <div className="flex w-full h-full">
              {canEdit && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full flex-grow"
                  fullWidth={true}
                  fullHeight={true}>
                    <Link
                      className="w-full h-full flex items-center justify-center"
                      to={`/coordinator/admin/studies/edit?id=${id}`}>
                        Edit
                    </Link>
                </Button>
              )}
              {canArchive && (
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full flex-grow"
                  onClick={() => deleteStudy(id)}
                >
                  Archive
                </Button>
              )}
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0
        }
      ];
    });
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteStudy = async (id: number) => {
    // Confirm deletion
    const msg = "Are you sure you want to archive this study?";
    if (!confirm(msg)) return;

    // Prepare and send the request
    const body = { app: 1, id }; // Admin Dashboard = 1
    await makeRequest("/admin/study/archive", { 
      method: "POST", 
      body: JSON.stringify(body) 
    }).then(handleSuccess).catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param id - the archived study id
   */
  const handleSuccess = async () => {
    flashMessage(<span>Study archived successfully.</span>, "success");

    // show the loading screen
    setLoading(true);

    // refresh the table's data
    makeRequest("/admin/study?app=1").then((studies) => {
      setStudies(studies);
      setLoading(false);
    });
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );
    flashMessage(msg, "danger");
  };

  const tableControl = canCreate ? (
    <Link to={`/coordinator/admin/studies/create`}>
      <Button variant="primary">
        Create +
      </Button>
    </Link>
  ) : (
    <React.Fragment />
  );

  const navbar = <Navbar activeView="Studies" />

  if (loading) {
    return (
      <ListView>
        {navbar}
        <ListContent>
          <SmallLoader />
        </ListContent>
      </ListView>
    );
  }

  return (
    <ListView>
      {navbar}
      <ListContent>
        <Table
          columns={COLUMNS}
          control={tableControl}
          controlWidth={10}
          data={getData()}
          includeControl={true}
          includeSearch={true}
          paginationPer={10}
          sortDefault=""
        />
      </ListContent>
    </ListView>
  );
};

export default Studies;
