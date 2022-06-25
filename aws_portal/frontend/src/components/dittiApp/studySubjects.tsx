import * as React from "react";
import { Component } from "react";
import { TapDetails, User } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import { add, differenceInDays, isWithinInterval, sub } from "date-fns";
import "./studySubjects.css";

interface StudySubject {
  id: string;
  dittiId: string;
  expiresOn: string;
}

interface StudySubjectsProps {
  studyPrefix: string;
  getTaps: () => TapDetails[];
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface StudySubjectsState {
  studySubjects: StudySubject[];
  loading: boolean;
}

class StudySubjects extends React.Component<
  StudySubjectsProps,
  StudySubjectsState
> {
  state = { studySubjects: [], loading: true };

  componentDidMount() {
    makeRequest(
      `/aws/scan?app=2&key=User&query=user_permission_idBEGINS"${this.props.studyPrefix}"`
    ).then((users: User[]) => {
      const studySubjects: StudySubject[] = users.map((u) => {
        return {
          id: u.id,
          dittiId: u.user_permission_id,
          expiresOn: u.exp_time
        };
      });
      this.setState({ studySubjects, loading: false });
    });
  }

  getSubjectSummary = (s: StudySubject): React.ReactElement => {
    const summaryTaps = [6, 5, 4, 3, 2, 1, 0].map((i) => {
      const today = new Date(new Date().setHours(9, 0, 0, 0));
      const start = sub(today, { days: i });
      const end = add(start, { days: 1 });
      const taps = this.props
        .getTaps()
        .filter((t) =>
          isWithinInterval(new Date(t.time), { start, end })
        ).length;

      const weekday = i
        ? start.toLocaleString("en-US", { weekday: "narrow" })
        : "Today";

      return (
        <div key={i} className="subject-summary-taps-day border-light-l">
          <span>{weekday}</span>
          <span>{taps}</span>
        </div>
      );
    });

    const today = new Date(new Date().setHours(9, 0, 0, 0));
    const start = sub(today, { days: 7 });
    const totalTaps = this.props
      .getTaps()
      .filter((t) =>
        isWithinInterval(new Date(t.time), { start, end: new Date() })
      ).length;

    summaryTaps.push(
      <div className="subject-summary-taps-day border-light-l">
        <span>
          <b>Total</b>
        </span>
        <span>
          <b>{totalTaps}</b>
        </span>
      </div>
    );

    const expiresOn = differenceInDays(new Date(s.expiresOn), new Date());

    return (
      <div key={s.id} className="subject-summary">
        <div className="subject-summary-name">
          <span>{s.dittiId}</span>
          <span>
            <i>Expires in: {expiresOn ? expiresOn + " days" : "Today"}</i>
          </span>
        </div>
        <div className="subject-summary-taps">{summaryTaps}</div>
      </div>
    );
  };

  render() {
    const { loading, studySubjects } = this.state;
    return loading ? (
      <SmallLoader />
    ) : (
      <React.Fragment>
        {studySubjects.map(this.getSubjectSummary)}
      </React.Fragment>
    );
  }
}

export default StudySubjects;
