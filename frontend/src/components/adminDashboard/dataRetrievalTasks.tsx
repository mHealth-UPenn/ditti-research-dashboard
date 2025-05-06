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

import { useState, useEffect, useCallback } from "react";
import { DataRetrievalTask } from "../../types/api";
import { getAccess } from "../../utils";
import { httpClient } from "../../lib/http";
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

  const fetchData = useCallback(async () => {
    try {
      // Fetch data retrieval tasks (View permission is handled by the server)
      const response = await httpClient.request<DataRetrievalTask[]>(
        "/data_processing_task/?app=1"
      );
      setTasks(response);
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
  }, [flashMessage]);

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
  }, [fetchData]);

  const handleForceStop = async (taskId: number) => {
    await httpClient
      .request(`/data_processing_task/force-stop`, {
        method: "POST",
        data: { app: 1, function_id: taskId },
      })
      .finally(() => {
        setLoading(true);
        // Refetch data regardless of the stop request's success/failure.
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
