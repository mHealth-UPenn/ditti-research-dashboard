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

import React, { useState, useEffect } from "react";
import { getAccess, makeRequest } from "../../utils";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AdminNavbar } from "./adminNavbar";
import { SmallLoader } from "../loader/loader";
import { Button } from "../buttons/button";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { Link } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { AboutSleepTemplate, ResponseBody } from "../../types/api";

export const AboutSleepTemplates = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canEdit, setCanEdit] = useState(false);
  const [canArchive, setCanArchive] = useState(false);
  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<
    AboutSleepTemplate[]
  >([]);
  const [loading, setLoading] = useState(true);
  const { flashMessage } = useFlashMessages();

  const columns: Column[] = [
    {
      name: "Name",
      searchable: true,
      sortable: true,
      width: 90,
    },
    {
      name: "",
      searchable: false,
      sortable: false,
      width: 10,
    },
  ];

  useEffect(() => {
    // check whether the user has permission to create
    const create = getAccess(1, "Create", "About Sleep Templates")
      .then(() => {
        setCanCreate(true);
      })
      .catch(() => {
        setCanCreate(false);
      });

    // check whether the user has permissions to edit
    const edit = getAccess(1, "Edit", "About Sleep Templates")
      .then(() => {
        setCanEdit(true);
      })
      .catch(() => {
        setCanEdit(false);
      });

    // check whether the user has permissions to archive
    const archive = getAccess(1, "Archive", "About Sleep Templates")
      .then(() => {
        setCanArchive(true);
      })
      .catch(() => {
        setCanArchive(false);
      });

    // get the table's data
    const fetchTemplates = makeRequest(
      "/admin/about-sleep-template?app=1"
    ).then((templates) => {
      setAboutSleepTemplates(templates as unknown as AboutSleepTemplate[]);
    });

    // when all requests are complete, hide the loading screen
    Promise.all([create, edit, archive, fetchTemplates])
      .then(() => {
        setLoading(false);
      })
      .catch((error: unknown) => {
        console.error("Error loading templates:", error);
        setLoading(false);
      });
  }, []);

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  const getData = (): TableData[][] => {
    return aboutSleepTemplates.map((s: AboutSleepTemplate) => {
      const { id, name } = s;

      // map each row to a set of cells for each table column
      return [
        {
          contents: <span>{name}</span>,
          searchValue: name,
          sortValue: name,
        },
        {
          contents: (
            <div className="flex size-full">
              {canEdit && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-full grow"
                  fullWidth={true}
                  fullHeight={true}
                >
                  <Link
                    className="flex size-full items-center justify-center"
                    to={`/coordinator/admin/about-sleep-templates/edit?id=${String(id)}`}
                  >
                    Edit
                  </Link>
                </Button>
              )}
              {canArchive && (
                <Button
                  variant="danger"
                  size="sm"
                  className="h-full grow"
                  onClick={() => {
                    deleteTemplate(id);
                  }}
                >
                  Archive
                </Button>
              )}
            </div>
          ),
          searchValue: "",
          sortValue: "",
          paddingX: 0,
          paddingY: 0,
        },
      ];
    });
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  const deleteTemplate = (id: number): void => {
    // prepare the request
    const body = { app: 1, id }; // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    // confirm deletion
    const msg = "Are you sure you want to archive this about sleep template?";

    if (confirm(msg))
      makeRequest("/admin/about-sleep-template/archive", opts)
        .then(handleSuccess)
        .catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // show the loading screen
    setLoading(true);
    flashMessage(<span>{res.msg}</span>, "success");

    // refresh the table's data
    makeRequest("/admin/about-sleep-template?app=1")
      .then((templates) => {
        setAboutSleepTemplates(templates as unknown as AboutSleepTemplate[]);
        setLoading(false);
      })
      .catch((error: unknown) => {
        console.error("Error refreshing templates:", error);
        setLoading(false);
      });
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message returned from the endpoint or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg || "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  // if the user has permission to create, show the create button
  const tableControl = canCreate ? (
    <Link to={`/coordinator/admin/about-sleep-templates/create`}>
      <Button variant="primary">Create +</Button>
    </Link>
  ) : (
    <React.Fragment />
  );

  const navbar = <AdminNavbar activeView="About Sleep Templates" />;

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
          columns={columns}
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
