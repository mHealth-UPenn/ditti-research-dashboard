import * as React from "react";
import { Component } from "react";
import { Study, StudySubject, TapDetails } from "../../interfaces";
import TextField from "../fields/textField";
import SubjectsEdit from "./subjectsEdit";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import { ReactComponent as ZoomIn } from "../../icons/zoomIn.svg";
import { ReactComponent as ZoomOut } from "../../icons/zoomOut.svg";
import {
  add,
  differenceInMinutes,
  format,
  isWithinInterval,
  sub
} from "date-fns";
import "./subjectVisuals.css";
import { dummyData } from "../dummyData";

interface Bout {
  start: Date;
  stop: Date;
  rate: number;
}

interface SubjectVisualsProps {
  getTaps: () => TapDetails[];
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
  studyDetails: Study;
  subject: StudySubject;
}

interface SubjectVisualsState {
  start: Date;
  stop: Date;
  taps: TapDetails[];
  bouts: Bout[];
}

class SubjectVisuals extends React.Component<
  SubjectVisualsProps,
  SubjectVisualsState
> {
  constructor(props: SubjectVisualsProps) {
    super(props);
    const { id } = props.subject;
    // const taps = props.getTaps().filter((t: TapDetails) => t.tapUserId == id);
    const taps = this.getTaps();

    this.state = {
      start: sub(new Date(new Date().setHours(3, 0, 0, 0)), { hours: 6 }),
      stop: new Date(new Date().setHours(3, 0, 0, 0)),
      taps: taps,
      bouts: []
    };
  }

  getTaps = (): TapDetails[] => {
    return dummyData;
  };

  decrement = (): void => {
    let { start, stop } = this.state;
    const difference = differenceInMinutes(stop, start);
    start = sub(start, { minutes: difference / 6 });
    stop = sub(stop, { minutes: difference / 6 });
    this.setState({ start, stop });
  };

  increment = (): void => {
    let { start, stop } = this.state;
    const difference = differenceInMinutes(stop, start);
    start = add(start, { minutes: difference / 6 });
    stop = add(stop, { minutes: difference / 6 });
    this.setState({ start, stop });
  };

  setStart = (text: string) => {
    if (new Date(text) && new Date(text) < sub(this.state.stop, { hours: 1 }))
      this.setState({ start: new Date(text) });
  };

  setStop = (text: string) => {
    if (new Date(text) && new Date(text) > add(this.state.start, { hours: 1 }))
      this.setState({ stop: new Date(text) });
  };

  zoomIn = (): void => {
    let { start, stop } = this.state;
    start = add(start, { minutes: 20 });
    stop = sub(stop, { minutes: 20 });
    if (differenceInMinutes(stop, start) > 60) this.setState({ start, stop });
  };

  zoomOut = (): void => {
    let { start, stop } = this.state;
    start = sub(start, { minutes: 20 });
    stop = add(stop, { minutes: 20 });
    this.setState({ start, stop });
  };

  getTapsDisplay = (): React.ReactElement => {
    const { start, stop, taps } = this.state;
    const difference = differenceInMinutes(stop, start);
    const tapsFiltered = taps.filter((t) =>
      isWithinInterval(new Date(t.time), { start, end: stop })
    );

    let i = start;
    const groups: { start: Date; stop: Date; taps: TapDetails[] }[] = [];
    while (i < stop) {
      const groupStart = i;
      i = add(i, { minutes: difference / 50 });

      const groupTaps = tapsFiltered.filter((t) =>
        isWithinInterval(new Date(t.time), { start: groupStart, end: i })
      );

      const group = { start: groupStart, stop: i, taps: groupTaps };
      groups.push(group);
    }

    const maxTaps = Math.max(...groups.map((g) => g.taps.length));
    const barWidth = 100 / groups.length + "%";

    const bars = groups.map((g, i) => {
      const height = maxTaps ? (g.taps.length / maxTaps) * 100 + "%" : "0%";
      return (
        <div
          key={i}
          style={{ height, width: barWidth }}
          className="bg-dark bar"
        ></div>
      );
    });

    const mody = Math.ceil(maxTaps / 15);
    const yTicks: { count: number; height: string }[] = [];

    Array.from(Array(maxTaps + 1).keys())
      .slice(1)
      .forEach((i) => {
        if (i % mody) return;
        const last = yTicks[yTicks.length - 1];
        const height = maxTaps ? (i / maxTaps) * 100 + "%" : "100%";
        const tick = { count: i, height };
        if (!last || i != last.count) yTicks.push(tick);
      });

    const yTickElems = yTicks.map((yt, i) => {
      return (
        <React.Fragment>
          <div
            key={i}
            className="border-dark-t y-axis-tick"
            style={{
              bottom: `calc(${yt.height} - 1px)`
            }}
          ></div>
          <div
            key={i + "label"}
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

    Array.from(Array(11).keys())
      .slice(1)
      .forEach((i) => {
        const ix = Math.ceil((i / 10) * groups.length) - 1;
        const time = groups[ix].start;
        const last = xTicks[xTicks.length - 1];
        const tick = { time, width: (ix / groups.length) * 100 + "%" };
        if (!last || time != last.time) xTicks.push(tick);
      });

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

    Array.from(Array(maxTaps + 1).keys())
      .slice(1)
      .forEach((i) => {
        if (i % 4) return;
        const last = hLines[hLines.length - 1];
        const height = maxTaps ? (i / maxTaps) * 100 + "%" : "100%";
        if (!last || height != last) hLines.push(height);
      });

    const hLineElems = hLines.map((hl, i) => {
      return <div key={i} className="hline" style={{ bottom: hl }}></div>;
    });

    const vLines: string[] = [];

    let j = new Date(add(start, { hours: 1 }).setMinutes(0, 0, 0));
    while (j < stop) {
      const thisDifference = differenceInMinutes(j, start);
      vLines.push((thisDifference / difference) * 100 + "%");
      j = new Date(add(j, { hours: 1 }).setMinutes(0, 0, 0));
    }

    const vlineElems = vLines.map((vl, i) => {
      return (
        <div
          key={i}
          className="border-light-r vline"
          style={{ left: vl }}
        ></div>
      );
    });

    return (
      <div className="taps-display-container">
        <div className="taps-display-top">
          <div className="y-axis">
            <div className="y-axis-label">
              <span>Taps</span>
            </div>
            <div>{yTickElems}</div>
          </div>
          <div
            className="taps-display border-dark"
            style={{ position: "relative" }}
          >
            {bars}
            {hLineElems}
            {vlineElems}
          </div>
        </div>
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

  render() {
    const { dittiId, expiresOn } = this.props.subject;
    const { studyDetails } = this.props;
    const { start, stop } = this.state;
    const adjustedStart = new Date(
      start.getTime() - start.getTimezoneOffset() * 60000
    );
    const adjustedStop = new Date(
      stop.getTime() - stop.getTimezoneOffset() * 60000
    );

    return (
      <div className="card-container">
        <div className="card-row">
          <div className="card-m bg-white shadow">
            <div className="subject-header">
              <div className="card-title">{dittiId}</div>
              <div className="subject-header-info">
                <div>
                  Expires on: <b>{expiresOn}</b>
                </div>
                <button
                  className="button-secondary button-lg"
                  onClick={() =>
                    this.props.handleClick(
                      ["Edit"],
                      <SubjectsEdit
                        dittiId={dittiId}
                        studyId={studyDetails.id}
                        studyEmail={studyDetails.email}
                        studyPrefix={studyDetails.dittiId}
                      />,
                      false
                    )
                  }
                  style={{ width: "12rem" }}
                >
                  Edit Details
                </button>
              </div>
            </div>
            <div className="subject-display-container">
              <div className="subject-display-title">Visual Summary</div>
              <div className="subject-display-controls">
                <div className="subject-display-field">
                  <span>Start:</span>
                  <TextField
                    type="datetime-local"
                    value={adjustedStart.toISOString().substring(0, 16)}
                    onKeyup={this.setStart}
                  />
                </div>
                <div className="subject-display-field">
                  <span>Stop:</span>
                  <TextField
                    type="datetime-local"
                    value={adjustedStop.toISOString().substring(0, 16)}
                    onKeyup={this.setStop}
                  />
                </div>
                <div className="subject-display-buttons">
                  <button className="button-secondary" onClick={this.decrement}>
                    <Left />
                  </button>
                  <button className="button-secondary" onClick={this.increment}>
                    <Right />
                  </button>
                  <button
                    className="button-secondary"
                    onClick={this.zoomIn}
                    disabled={differenceInMinutes(stop, start) < 100}
                  >
                    <ZoomIn style={{ height: "66%", margin: "auto" }} />
                  </button>
                  <button className="button-secondary" onClick={this.zoomOut}>
                    <ZoomOut style={{ height: "66%", margin: "auto" }} />
                  </button>
                </div>
              </div>
              <div className="subject-display">{this.getTapsDisplay()}</div>
            </div>
            <div className="flex-center">
              <button
                className="button-primary button-lg"
                style={{ width: "12rem" }}
              >
                Download CSV
              </button>
            </div>
          </div>
          <div className="card-s bg-white shadow">
            <div className="card-title">7-day summary</div>
          </div>
        </div>
      </div>
    );
  }
}

export default SubjectVisuals;
