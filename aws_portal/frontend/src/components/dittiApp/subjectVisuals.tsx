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
import { AudioTapDetails, Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import TextField from "../fields/textField";
import SubjectsEdit from "./subjectsEdit";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import { ReactComponent as ZoomIn } from "../../icons/zoomIn.svg";
import { ReactComponent as ZoomOut } from "../../icons/zoomOut.svg";
import {
  add,
  differenceInMinutes,
  differenceInMilliseconds,
  format,
  isWithinInterval,
  sub
} from "date-fns";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import "./subjectVisuals.css";
import { getAccess } from "../../utils";
import { SmallLoader } from "../loader";

/**
 * A period of time when a subject is considered to be actively tapping
 * start: the start time
 * stop: the stop time
 * rate: the tapping rate during this bout
 */
interface Bout {
  start: Date;
  stop: Date;
  rate: number;
}

/**
 * getTaps: get tap data
 * studyDetails: details of the subject's study
 * user: details of the subject
 */
interface SubjectVisualsProps extends ViewProps {
  getTaps: () => TapDetails[];
  getAudioTaps: () => AudioTapDetails[];
  studyDetails: Study;
  user: UserDetails;
}

const SubjectVisuals: React.FC<SubjectVisualsProps> = ({
  getTaps,
  getAudioTaps,
  studyDetails,
  user,
  flashMessage,
  goBack,
  handleClick
}) => {
  const [canEdit, setCanEdit] = useState(false);
  const [start, setStart] = useState(sub(new Date(new Date().setHours(9, 0, 0, 0)), { hours: 24 }));
  const [stop, setStop] = useState(new Date(new Date().setHours(9, 0, 0, 0)));
  const [taps, setTaps] = useState(() => getTaps().filter((t) => t.dittiId === user.userPermissionId));
  const [audioTaps, setAudioTaps] = useState(() => getAudioTaps().filter((t) => t.dittiId === user.userPermissionId));
  const [bouts, setBouts] = useState<Bout[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setBouts(getBouts(taps));

    getAccess(2, "Edit", "Participants", studyDetails.id)
      .then(() => {
        setCanEdit(true);
        setLoading(false);
      })
      .catch(() => {
        setCanEdit(false);
        setLoading(false);
      });
  }, [studyDetails.id, taps]);

  const getBouts = (taps: TapDetails[]): Bout[] => {
    const bouts: Bout[] = [];
    let first: Date;
    let current: Date;
    let last: Date;
    let group: Date[];
    let count = 0;

    taps.forEach((t) => {

      // on first iteration
      if (!count) {
        first = t.time;
        group = [first];
        count = 1;
        return;
      }

      current = t.time;

      // if this tap is less than one minute after the first tap
      if (differenceInMilliseconds(current, first) < 60000) {
        last = current;
        group.push(current);
        count += 1;
      }

      // else if there were 5 taps or more in the first minute and less than 30
      // minutes have passed between this tap and the last tap then the bout
      // begins at the first tap
      else if (
        count >= 5 &&
        differenceInMilliseconds(current, last) < 1800000
      ) {
        last = current;
        group.push(current);
        count += 1;
      }

      // else if there were 5 taps or more in the first minute and more than 10
      // minutes have passed then the bout ends at 10 minutes after the last
      // tap
      else if (count >= 5 && differenceInMilliseconds(last, first) > 60000) {
        bouts.push({
          start: first,
          stop: add(last, { minutes: 30 }),
          rate: count / differenceInMinutes(last, first)
        });
        first = current;
        group = [first];
        count = 1;
      }

      // else if there were less than 5 taps in the first minute or tapping
      // lasted for less than one minute then no bout has begun
      else {
        group = group.filter(
          (t) => differenceInMilliseconds(current, t) < 60000
        );

        if (group.length) {
          first = group[0];
          count = group.length;
        } else {
          first = current;
          group = [first];
          count = 1;
        }
      }
    });

    return bouts;
  };

  const downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const id = studyDetails.acronym;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);

    const tapsData = taps.map(t => {
      return [t.dittiId, t.time, t.timezone, "", ""];
    });

    const audioTapsData = audioTaps.map(t => {
      return [t.dittiId, t.time, t.timezone, t.action, t.audioFileTitle];
    });

    const data = tapsData.concat(audioTapsData).sort((a, b) => {
      if (a[1] > b[1]) return 1;
      else if (a[1] < b[1]) return -1;
      else return 0;
    })

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 },
      { header: "Timezone", width: 30 },
      { header: "Audio Tap Action", width: 15 },
      { header: "Audio File Title", width: 20 },
    ];

    sheet.getColumn("B").numFmt = "DD/MM/YYYY HH:mm:ss";

    // add data to the workbook
    sheet.addRows(data);

    // write the workbook to a blob
    workbook.xlsx.writeBuffer().then((data) => {
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      // download the blob
      saveAs(blob, fileName + ".xlsx");
    });
  };

  const decrement = (): void => {
    const difference = differenceInMinutes(stop, start);

    setStart(sub(start, { minutes: difference / 6 }));
    setStop(sub(stop, { minutes: difference / 6 }));
  };

  const increment = (): void => {
    const difference = differenceInMinutes(stop, start);

    setStart(add(start, { minutes: difference / 6 }));
    setStop(add(stop, { minutes: difference / 6 }));
  };

  const updateStart = (text: string): void => {
    const newStart = new Date(text);
    if (newStart && newStart < sub(stop, { hours: 1 })) {
      setStart(new Date(text));
    }
  };

  const updateStop = (text: string): void => {
    const newStop = new Date(text);
    if (newStop && newStop > add(start, { hours: 1 })) {
      setStop(new Date(text));
    }
  };

  const zoomIn = (): void => {
    if (differenceInMinutes(stop, start) > 60) {
      setStart(add(start, { hours: 1 }));
      setStop(sub(stop, { hours: 1 }));
    }
  };

  const zoomOut = (): void => {
    setStart(sub(start, { hours: 1 }));
    setStop(add(stop, { hours: 1 }));
  };

  const getTapsDisplay = (): React.ReactElement => {
    const difference = differenceInMinutes(stop, start);

    // get all taps that are within the time window
    const tapsFiltered = taps.filter((t) =>
      isWithinInterval(t.time, { start, end: stop })
    );

    let i = start;

    // cluster taps into 60 evenly-spaced time intervals
    const groups: { start: Date; stop: Date; taps: TapDetails[] }[] = [];
    while (i < stop) {
      const groupStart = i;
      i = add(i, { minutes: difference / 60 });

      const groupTaps = tapsFiltered.filter((t) =>
        isWithinInterval(t.time, { start: groupStart, end: i })
      );

      const group = { start: groupStart, stop: i, taps: groupTaps };
      groups.push(group);
    }

    // get the maximum height of the y-axis, which must be at least 10
    const maxTaps = Math.max(10, ...groups.map((g) => g.taps.length));

    // the width of each vertical bar such that when stacked horizontally they
    // will span the entire display
    const barWidth = 100 / groups.length + "%";

    // render each bar
    const bars = groups.map((g, i) => {

      // set the height of the vertical bar
      const height = maxTaps ? (g.taps.length / maxTaps) * 100 + "%" : "0%";
      return (
        <div
          key={i}
          style={{ height, width: barWidth }}
          className="bg-dark bar"
        ></div>
      );
    });

    // to modify assign the spacing required to render 10 evenly-spaced ticks
    const mody = Math.ceil(maxTaps / 10);
    const yTicks: { count: number; height: string }[] = [];

    // create the y-axis ticks
    Array.from(Array(maxTaps + 1).keys())
      .slice(1)
      .forEach((i) => {

        // if this tap is not sufficiently spaced from the previous tick
        if (i % mody) return;
        const last = yTicks[yTicks.length - 1];
        const height = maxTaps ? (i / maxTaps) * 100 + "%" : "100%";
        const tick = { count: i, height };
        if (!last || i !== last.count) yTicks.push(tick);
      });

    // render the y-axis ticks
    const yTickElems = yTicks.map((yt, i) => {
      return (
        <React.Fragment key={i}>
          <div
            className="border-dark-t y-axis-tick"
            style={{
              bottom: `calc(${yt.height} - 1px)`
            }}
          ></div>
          <div
            className="y-axis-tick-label"
            style={{
              bottom: `calc(${yt.height} - 0.5rem)`
            }}
          >
            {yt.count}
          </div>
        </React.Fragment>
      );
    });

    const xTicks: { time: Date; width: string }[] = [];

    // create 16 evenly-spaced x-axis ticks
    Array.from(Array(16).keys())
      .slice(1)
      .forEach((i) => {

        // get the group that this tick will start at
        const ix = Math.ceil((i / 15) * groups.length) - 1;

        // set the tick's location to the start of the group
        const time = groups[ix].start;
        const last = xTicks[xTicks.length - 1];
        const tick = { time, width: (ix / groups.length) * 100 + "%" };
        if (!last || time !== last.time) xTicks.push(tick);
      });

    // render the x-axis ticks
    const xTickElems = xTicks.map((xt, i) => {
      return (
        <React.Fragment key={i}>
          <div
            className="border-dark-r x-axis-tick"
            style={{
              left: `calc(${xt.width} - 1px)`
            }}
          ></div>
          <div
            className="x-axis-tick-label"
            style={{
              left: `calc(${xt.width} - 0.5rem)`
            }}
          >
            {format(xt.time, "E MMM d'\n'h:mm a")}
          </div>
        </React.Fragment>
      );
    });

    const hLines: string[] = [];

    // create horizontal lines for the display
    Array.from(Array(maxTaps + 1).keys())
      .slice(1)
      .forEach((i) => {

        // create a horizontal line every 20 taps
        if (i % 20) return;
        const last = hLines[hLines.length - 1];

        // the line's position on the display
        const height = maxTaps ? (i / maxTaps) * 100 + "%" : "100%";
        if (!last || height !== last) hLines.push(height);
      });

    // render the horizontal lines
    const hLineElems = hLines.map((hl, i) => {
      return <div key={i} className="hline" style={{ bottom: hl }}></div>;
    });

    const vLines: { left: string; bold: boolean }[] = [];

    // create vertical lines for the display on every hour
    let j = new Date(add(start, { hours: 1 }).setMinutes(0, 0, 0));
    while (j < stop) {
      const thisDifference = differenceInMinutes(j, start);

      // create a bold line every 24 hours
      const bold = Boolean(j.getHours() % 24);

      // the line's position on the display
      const left = (thisDifference / difference) * 100 + "%";
      vLines.push({ left, bold });
      j = new Date(add(j, { hours: 1 }).setMinutes(0, 0, 0));
    }

    // render the vertical lines
    const vlineElems = vLines.map((vl, i) => {
      return (
        <div
          key={i}
          className="vline border-light-r"
          style={{
            left: vl.left,
            borderRightWidth: vl.bold ? "1px" : "3px",
            borderRightStyle: vl.bold ? "dashed" : "solid"
          }}
        ></div>
      );
    });

    return (
      <div className="taps-display-container">
        <div className="taps-display-top">

          {/* the y-axis */}
          <div className="y-axis">
            <div className="y-axis-label">
              <span>Taps</span>
            </div>
            <div>{yTickElems}</div>
          </div>

          {/* the display */}
          <div
            className="taps-display border-dark"
            style={{ position: "relative" }}
          >
            {bars}
            {hLineElems}
            {vlineElems}
          </div>
        </div>

        {/* the x-axis */}
        <div className="taps-display-bottom">
          <div className="x-axis-pad"></div>
          <div className="x-axis">
            <div className="x-axis-label">
              <span>Time</span>
            </div>
            <div>{xTickElems}</div>
          </div>
        </div>
      </div>
    );
  };

  const getBoutsDisplay = (): React.ReactElement => {
    const difference = differenceInMilliseconds(stop, start);

    // get all bouts that are within the time window
    const boutsFiltered = bouts.filter(
      (b) => start < b.stop && b.start < stop
    );

    // render the shaded bouts in the bouts display
    const boutElems = boutsFiltered.map((b, index) => {

      // if the bout starts after the start of the time window, find its
      // starting position as a percentage of the bouts display
      const left =
        start < b.start
          ? (differenceInMilliseconds(b.start, start) / difference) * 100
          : 0;

      // if the bout ends before the stop time of the time window, find its end
      // position as a percentage of the bouts display
      const width =
        b.stop < stop
          ? (differenceInMilliseconds(b.stop, start) / difference) * 100 - left
          : 100 - left;
      return (
        <div
          key={index}
          className="bout bg-dark"
          style={{ left: left + "%", width: `calc(${width + "%"} - 1rem)` }}
        >

          {/* display the tapping rate and length of bout */}
          <span>
            {b.rate.toLocaleString("en-US", { maximumSignificantDigits: 2 }) +
              " taps/min"}
            <br />
            {differenceInMinutes(b.stop, b.start) + " mins"}
          </span>
        </div>
      );
    });

    return (
      <div className="bouts-display-container mb-2">
        <div className="y-axis">
          <div className="y-axis-label">
            <span>
              Tapping
              <br />
              Bouts
            </span>
          </div>
        </div>
        <div className="bouts-display border-dark">{boutElems}</div>
      </div>
    );
  };

  const getAudioTapsDisplay = (): React.ReactElement => {
    const difference = differenceInMilliseconds(stop, start);

    // get all audio taps that are within the time window
    const audioTapsFiltered = audioTaps.filter(
      (b) => start < b.time && b.time < stop
    );

    const audioTapElems = audioTapsFiltered.map((at, index) => {
      const left =
        start < at.time
          ? (differenceInMilliseconds(at.time, start) / difference) * 100
          : 0;

      return (
        <div
          key={index}
          className="audio-tap bg-dark absolute h-full"
          style={{ left: left + "%", width: "2px" }} />
      );
    });

    return (
      <div className="bouts-display-container">
        <div className="y-axis">
          <div className="y-axis-label">
            <span>
              Audio Taps
            </span>
          </div>
        </div>
        <div className="bouts-display border-dark relative">{audioTapElems}</div>
      </div>
    );
  };

  const adjustedStart = new Date(
    start.getTime() - start.getTimezoneOffset() * 60000
  );

  const adjustedStop = new Date(
    stop.getTime() - stop.getTimezoneOffset() * 60000
  );

  const expTimeDate = new Date(user.expTime);
  const expTimeAdjusted = new Date(
    expTimeDate.getTime() - expTimeDate.getTimezoneOffset() * 60000
  );

  const dateOpts = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  };

  const expTimeFormatted = expTimeAdjusted.toLocaleDateString(
    "en-US",
    dateOpts as Intl.DateTimeFormatOptions
  );

  return (
    <div className="card-container">
      <div className="card-row">
        <div className="card-l bg-white shadow">
          {loading ? (
            <SmallLoader />
          ) : (
            <React.Fragment>

              {/* the subject's details */}
              <div className="subject-header">
                <div className="card-title flex-space">
                  <span>{user.userPermissionId}</span>

                  {/* download the subject's data as excel */}
                  <button
                    className="button-primary button-lg"
                    style={{ width: "12rem" }}
                    onClick={downloadExcel}
                  >
                    Download Excel
                  </button>
                </div>
                <div className="subject-header-info">
                  <div>
                    Expires on: <b>{expTimeFormatted}</b>
                  </div>

                  {/* if the user can edit, show the edit button */}
                  {canEdit ? (
                    <button
                      className="button-secondary button-lg"
                      onClick={() =>
                        handleClick(
                          ["Edit"],
                          <SubjectsEdit
                            // dittiId={user.userPermissionId}
                            // studyDetails={studyDetails}
                            // flashMessage={flashMessage}
                            // goBack={goBack}
                            // handleClick={handleClick}
                          />
                        )
                      }
                      style={{ width: "12rem" }}
                    >
                      Edit Details
                    </button>
                  ) : null}
                </div>
              </div>

              {/* the display and controls */}
              <div className="subject-display-container">
                <div className="subject-display-title">Visual Summary</div>

                {/* display controls */}
                <div className="subject-display-controls">

                  {/* control the start time */}
                  <div className="subject-display-field">
                    <span>Start:</span>
                    <TextField
                      type="datetime-local"
                      value={adjustedStart.toISOString().substring(0, 16)}
                      onKeyup={updateStart}
                    />
                  </div>

                  {/* control the end time */}
                  <div className="subject-display-field">
                    <span>Stop:</span>
                    <TextField
                      type="datetime-local"
                      value={adjustedStop.toISOString().substring(0, 16)}
                      onKeyup={updateStop}
                    />
                  </div>

                  {/* move and zoom the window */}
                  <div className="subject-display-buttons">
                    <button
                      className="button-secondary"
                      onClick={decrement}
                    >
                      <Left />
                    </button>
                    <button
                      className="button-secondary"
                      onClick={increment}
                    >
                      <Right />
                    </button>
                    <button
                      className="button-secondary"
                      onClick={zoomIn}
                      disabled={differenceInMinutes(stop, start) < 180}
                    >
                      <ZoomIn style={{ height: "66%", margin: "auto" }} />
                    </button>
                    <button
                      className="button-secondary"
                      onClick={zoomOut}
                    >
                      <ZoomOut style={{ height: "66%", margin: "auto" }} />
                    </button>
                  </div>
                </div>

                {/* the taps and bouts displays */}
                <div className="subject-display">
                  {getTapsDisplay()}
                  {getBoutsDisplay()}
                  {getAudioTapsDisplay()}
                </div>
              </div>
            </React.Fragment>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubjectVisuals;
