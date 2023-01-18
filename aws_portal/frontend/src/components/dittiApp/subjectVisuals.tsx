import * as React from "react";
import { Component } from "react";
import { Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
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
  studyDetails: Study;
  user: UserDetails;
}

/**
 * canEdit: whether the user can edit subjects
 * start: the start time of the display
 * stop: the stop time of the display
 * taps: taps to display
 * bouts: bouts to display
 * loading: whether to show the loader
 */
interface SubjectVisualsState {
  canEdit: boolean;
  start: Date;
  stop: Date;
  taps: TapDetails[];
  bouts: Bout[];
  loading: boolean;
}

class SubjectVisuals extends React.Component<
  SubjectVisualsProps,
  SubjectVisualsState
> {
  constructor(props: SubjectVisualsProps) {
    super(props);
    const { userPermissionId } = props.user;

    // get this subject's taps only
    const taps = props.getTaps().filter((t) => t.dittiId == userPermissionId);

    // start from 9am yesterday to 9am today
    this.state = {
      canEdit: false,
      start: sub(new Date(new Date().setHours(9, 0, 0, 0)), { hours: 24 }),
      stop: new Date(new Date().setHours(9, 0, 0, 0)),
      taps: taps,
      bouts: this.getBouts(taps),
      loading: true
    };
  }

  componentDidMount() {

    // get whether the user can edit subjects then hide the loader
    getAccess(2, "Edit", "Users", this.props.studyDetails.id)
      .then(() => this.setState({ canEdit: true, loading: false }))
      .catch(() => this.setState({ canEdit: false, loading: false }));
  }

  /**
   * Get all bouts from a set of taps
   * @param taps - the taps to calculate bouts for
   * @returns - the bouts for this set of taps
   */
  getBouts = (taps: TapDetails[]): Bout[] => {
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

  /**
   * Download all of the subject's data as excel
   */
  downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const id = this.props.user.userPermissionId;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);
    const data = this.state.taps.map((t) => {

      // localize tap timestamps
      const time = t.time.getTime() - t.time.getTimezoneOffset() * 60000;
      return [t.dittiId, new Date(time)];
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 }
    ];

    sheet.getColumn("B").numFmt = "DD/MM/YYYY HH:mm:ss";
    sheet.addRows(data);

    workbook.xlsx.writeBuffer().then((data) => {
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      // dowload the excel file
      saveAs(blob, fileName + ".xlsx");
    });
  };

  /**
   * Move the display left by 1/6 of the current time window. For example, if
   * the current time window is 60 minutes, the move left by 10 minutes.
   */
  decrement = (): void => {
    let { start, stop } = this.state;
    const difference = differenceInMinutes(stop, start);

    start = sub(start, { minutes: difference / 6 });
    stop = sub(stop, { minutes: difference / 6 });
    this.setState({ start, stop });
  };

  /**
   * Move the display right by 1/6 of the current time window. For example, if
   * the current time window is 60 minutes, the move right by 10 minutes.
   */
  increment = (): void => {
    let { start, stop } = this.state;
    const difference = differenceInMinutes(stop, start);

    start = add(start, { minutes: difference / 6 });
    stop = add(stop, { minutes: difference / 6 });
    this.setState({ start, stop });
  };

  /**
   * Set the start time of the display window
   * @param text - output from an HTML5 date field
   */
  setStart = (text: string) => {
    if (new Date(text) && new Date(text) < sub(this.state.stop, { hours: 1 }))
      this.setState({ start: new Date(text) });
  };

  /**
   * Set the stop time of the display window
   * @param text - output from an HTML5 date field
   */
  setStop = (text: string) => {
    if (new Date(text) && new Date(text) > add(this.state.start, { hours: 1 }))
      this.setState({ stop: new Date(text) });
  };

  /**
   * Decrease the window size by two hours, one hour on each side. If the
   * resulting window size is 60 minutes or less, don't zoom in
   */
  zoomIn = (): void => {
    let { start, stop } = this.state;

    start = add(start, { hours: 1 });
    stop = sub(stop, { hours: 1 });
    if (differenceInMinutes(stop, start) > 60) this.setState({ start, stop });
  };

  /**
   * Increase the window size by two hours, one hour on each side
   */
  zoomOut = (): void => {
    let { start, stop } = this.state;

    start = sub(start, { hours: 1 });
    stop = add(stop, { hours: 1 });
    this.setState({ start, stop });
  };

  /**
   * Render the taps display
   * @returns - the taps display
   */
  getTapsDisplay = (): React.ReactElement => {
    const { start, stop, taps } = this.state;
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

    // to mody assign the spacing required to render 10 evenly-spaced ticks
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
        if (!last || i != last.count) yTicks.push(tick);
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
        if (!last || time != last.time) xTicks.push(tick);
      });

    // render the x-axis ticks
    const xTickElems = xTicks.map((xt, i) => {
      return (
        <React.Fragment>
          <div
            key={i}
            className="border-dark-r x-axis-tick"
            style={{
              left: `calc(${xt.width} - 1px)`
            }}
          ></div>
          <div
            key={i + "label"}
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

        // the lines position on the display
        const height = maxTaps ? (i / maxTaps) * 100 + "%" : "100%";
        if (!last || height != last) hLines.push(height);
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

          {/* the dispaly */}
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

  /**
   * Render the bouts display
   * @returns - the bouts display
   */
  getBoutsDisplay = (): React.ReactElement => {
    const { start, stop } = this.state;
    const difference = differenceInMilliseconds(stop, start);

    // get all bouts that are within the time window
    const bouts = this.state.bouts.filter(
      (b) => start < b.stop && b.start < stop
    );

    // render the shaded bouts in the bouts display
    const boutElems = bouts.map((b) => {

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
      <div className="bouts-display-container">
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

  render() {
    const { flashMessage, goBack, handleClick, studyDetails } = this.props;
    const { userPermissionId, expTime } = this.props.user;
    const { canEdit, start, stop, loading } = this.state;

    // localize the start and stop times for display purposes
    const adjustedStart = new Date(
      start.getTime() - start.getTimezoneOffset() * 60000
    );

    const adjustedStop = new Date(
      stop.getTime() - stop.getTimezoneOffset() * 60000
    );

    // localize the subject's expiry date
    const expTimeDate = new Date(expTime);
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
                    <span>{userPermissionId}</span>

                    {/* download the subject's data as excel */}
                    <button
                      className="button-primary button-lg"
                      style={{ width: "12rem" }}
                      onClick={this.downloadExcel}
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
                              dittiId={userPermissionId}
                              studyId={studyDetails.id}
                              studyEmail={studyDetails.email}
                              studyPrefix={studyDetails.dittiId}
                              flashMessage={flashMessage}
                              goBack={goBack}
                              handleClick={handleClick}
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
                        onKeyup={this.setStart}
                      />
                    </div>

                    {/* control the end time */}
                    <div className="subject-display-field">
                      <span>Stop:</span>
                      <TextField
                        type="datetime-local"
                        value={adjustedStop.toISOString().substring(0, 16)}
                        onKeyup={this.setStop}
                      />
                    </div>

                    {/* move and zoom the window */}
                    <div className="subject-display-buttons">
                      <button
                        className="button-secondary"
                        onClick={this.decrement}
                      >
                        <Left />
                      </button>
                      <button
                        className="button-secondary"
                        onClick={this.increment}
                      >
                        <Right />
                      </button>
                      <button
                        className="button-secondary"
                        onClick={this.zoomIn}
                        disabled={differenceInMinutes(stop, start) < 180}
                      >
                        <ZoomIn style={{ height: "66%", margin: "auto" }} />
                      </button>
                      <button
                        className="button-secondary"
                        onClick={this.zoomOut}
                      >
                        <ZoomOut style={{ height: "66%", margin: "auto" }} />
                      </button>
                    </div>
                  </div>

                  {/* the taps and bouts displays */}
                  <div className="subject-display">
                    {this.getTapsDisplay()}
                    {this.getBoutsDisplay()}
                  </div>
                </div>
              </React.Fragment>
            )}
          </div>
        </div>
      </div>
    );
  }
}

export default SubjectVisuals;
