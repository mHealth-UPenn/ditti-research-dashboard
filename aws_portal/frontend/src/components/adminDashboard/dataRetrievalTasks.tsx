import * as React from "react";
import { useState, useEffect } from "react";
import { ViewProps, DataRetrievalTask } from "../../interfaces";
import { makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import { SmallLoader } from "../loader";
import ListView from "../containers/lists/listView";
import ListContent from "../containers/lists/listContent";

/**
 * Defines the table columns for displaying data retrieval tasks.
 */
const COLUMNS: Column[] = [
  { name: "ID", searchable: false, sortable: true, width: 5 },
  { name: "Status", searchable: false, sortable: true, width: 15 },
  // { name: "Billed (ms)", searchable: false, sortable: true, width: 10 },
  { name: "Created On", searchable: false, sortable: true, width: 15 },
  // { name: "Updated On", searchable: false, sortable: true, width: 15 },
  { name: "Completed On", searchable: false, sortable: true, width: 15 },
  { name: "Log File", searchable: true, sortable: false, width: 20 },
  { name: "Error Code", searchable: true, sortable: false, width: 5 },
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
function formatDate(isoDate: string | null): { display: string; sortValue: string } {
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
const DataRetrievalTasks: React.FC<ViewProps> = ({ flashMessage, goBack, handleClick }) => {
  const [tasks, setTasks] = useState<DataRetrievalTask[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch data retrieval tasks (View permission is handled by the server)
        const data: DataRetrievalTask[] = await makeRequest("/data_processing_task/?app=1");
        setTasks(data);
      } catch (error: any) {
        console.error("Error fetching tasks:", error);
        flashMessage(
          <span>
            <b>An error occurred loading data retrieval tasks.</b>
            <br />
            {error instanceof Error ? error.message : "Unknown error"}
          </span>,
          "danger"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [flashMessage]);

  /**
   * Transforms tasks into table data format.
   * @returns An array of table rows.
   */
  const getData = (): TableData[][] => {
    return tasks.map((task) => {
      const statusDisplay = humanReadableStatus(task.status);
      const created = formatDate(task.createdOn);
      const updated = formatDate(task.updatedOn);
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
        // {
        //   contents: <span>{task.billedMs || 0}</span>,
        //   searchValue: (task.billedMs || 0).toString(),
        //   sortValue: task.billedMs || 0,
        // },
        {
          contents: <span>{created.display}</span>,
          searchValue: created.display,
          sortValue: created.sortValue,
        },
        // {
        //   contents: <span>{updated.display}</span>,
        //   searchValue: updated.display,
        //   sortValue: updated.sortValue,
        // },
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
          searchValue: task.logFile || "",
          sortValue: task.logFile || "",
        },
        {
          contents: <span>{task.errorCode || "N/A"}</span>,
          searchValue: task.errorCode || "",
          sortValue: task.errorCode || "",
        },
      ];
    });
  };

  const tableControl = <></>;

  const navbar = (
    <Navbar active="Data Retrieval Tasks" flashMessage={flashMessage} goBack={goBack} handleClick={handleClick} />
  );

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

export default DataRetrievalTasks;
