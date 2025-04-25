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

import { useState, useEffect } from "react";
import { DataRetrievalTask } from "../../types/api";
import { getAccess, makeRequest } from "../../utils";
import { Column, TableData } from "../table/table.types";
import { Table } from "../table/table";
import { AdminNavbar } from "./adminNavbar";
import { SmallLoader } from "../loader/loader";
import { ListView } from "../containers/lists/listView";
import { ListContent } from "../containers/lists/listContent";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { AsyncButton } from "../buttons/asyncButton";

/**
 * Defines the table columns for displaying data retrieval tasks.
 */
const COLUMNS: Column[] = [
  { name: "ID", searchable: false, sortable: true, width: 5 },
  { name: "Status", searchable: false, sortable: true, width: 10 },
  { name: "Created On", searchable: false, sortable: true, width: 15 },
  { name: "Completed On", searchable: false, sortable: true, width: 15 },
  { name: "Log File", searchable: true, sortable: false, width: 15 },
  { name: "Error Code", searchable: true, sortable: false, width: 10 },
  { name: "", searchable: false, sortable: false, width: 5 },
];

/**
 * Converts API status to a human-readable format.
 * @param status - The status string from the API.
 * @returns A more readable status string.
 */
function humanReadableStatus(status: DataRetrievalTask["status"]): string {
  switch (status) {
    case "Pending":
      return "Pending";
    case "InProgress":
      return "In Progress";
    case "Success":
      return "Success";
    case "Failed":
      return "Failed";
    case "CompletedWithErrors":
      return "Completed With Errors";
    default:
      return status;
  }
}

/**
 * Converts an ISO date string to a human-readable format.
 * @param isoDate - The ISO date string.
 * @returns An object containing the display string and the original ISO string for sorting.
 */
function formatDate(isoDate: string | null): {
  display: string;
  sortValue: string;
} {
  if (!isoDate) return { display: "N/A", sortValue: "" };

  const date = new Date(isoDate);
  const display = date.toLocaleString();
  return { display, sortValue: isoDate };
}

/**
 * Component to display data retrieval tasks in the Admin Dashboard.
 * @param flashMessage - Function to display flash messages.
 * @param goBack - Function to navigate back.
 * @param handleClick - Function to handle navigation link clicks.
 */
export const DataRetrievalTasks = () => {
  const [canInvoke, setCanInvoke] = useState<boolean>(false);
  const [tasks, setTasks] = useState<DataRetrievalTask[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const { flashMessage } = useFlashMessages();

  const fetchData = async () => {
    try {
      // Fetch data retrieval tasks (View permission is handled by the server)
      const response = await makeRequest("/data_processing_task/?app=1");
      // Cast to DataRetrievalTask[] using unknown as intermediate type
      const data = response as unknown as DataRetrievalTask[];
      setTasks(data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
      flashMessage(
        <span>
          <b>An error occurred loading data retrieval tasks.</b>
          <br />
          {error instanceof Error ? error.message : "Unknown error"}
        </span>,
        "danger"
      );
    }
  };

  useEffect(() => {
    const invoke = getAccess(1, "Invoke", "Data Retrieval Task")
      .then(() => {
        setCanInvoke(true);
      })
      .catch(() => {
        setCanInvoke(false);
      });

    void Promise.all([invoke, fetchData()]).finally(() => {
      setLoading(false);
    });
  }, [flashMessage]);

  const handleForceStop = async (id: number) => {
    await makeRequest(`/data_processing_task/force-stop`, {
      method: "POST",
      body: JSON.stringify({
        app: 1,
        function_id: id,
      }),
    }).finally(() => {
      setLoading(true);
      void fetchData().finally(() => {
        setLoading(false);
      });
    });
  };

  /**
   * Transforms tasks into table data format.
   * @returns An array of table rows.
   */
  const getData = (): TableData[][] => {
    return tasks.map((task) => {
      const statusDisplay = humanReadableStatus(task.status);
      const created = formatDate(task.createdOn);
      const completed = formatDate(task.completedOn);

      return [
        {
          contents: <span>{task.id}</span>,
          searchValue: task.id.toString(),
          sortValue: task.id,
        },
        {
          contents: <span>{statusDisplay}</span>,
          searchValue: statusDisplay,
          sortValue: statusDisplay,
        },
        {
          contents: <span>{created.display}</span>,
          searchValue: created.display,
          sortValue: created.sortValue,
        },
        {
          contents: <span>{completed.display}</span>,
          searchValue: completed.display,
          sortValue: completed.sortValue,
        },
        {
          contents: task.logFile ? (
            <span>{task.logFile}</span>
          ) : (
            <span>N/A</span>
          ),
          searchValue: task.logFile ?? "",
          sortValue: task.logFile ?? "",
        },
        {
          contents: <span>{task.errorCode ?? "N/A"}</span>,
          searchValue: task.errorCode ?? "",
          sortValue: task.errorCode ?? "",
        },
        {
          contents: (
            <div className="flex size-full">
              {task.status === "InProgress" && canInvoke && (
                <AsyncButton
                  variant="danger"
                  size="sm"
                  className="h-full grow"
                  onClick={() => handleForceStop(task.id)}
                >
                  Force Stop
                </AsyncButton>
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

  const tableControl = <></>;

  const navbar = <AdminNavbar activeView="Data Retrieval Tasks" />;

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
          controlWidth={0}
          data={getData()}
          includeControl={false}
          includeSearch={true}
          paginationPer={10}
          sortDefault="ID"
        />
      </ListContent>
    </ListView>
  );
};
