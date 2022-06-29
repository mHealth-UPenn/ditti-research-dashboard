import * as React from "react";
import { Component } from "react";
import Accounts from "./adminDashboard/accounts";
import StudiesView from "./dittiApp/studies";
import Header from "./header";
import Home from "./home";
import Navbar from "./navbar";
import StudiesMenu from "./studiesMenu";
import "./dashboard.css";
import { TapDetails, UserDetails } from "../interfaces";
import { dummyData } from "./dummyData";
import { differenceInMilliseconds } from "date-fns";

interface DashboardState {
  apps: {
    breadcrumbs: string[];
    name: string;
    id: number;
    view: React.ReactElement;
  }[];
  breadcrumbs: { name: string; view: React.ReactElement }[];
  flashMessages: { id: number; element: React.ReactElement }[];
  history: { name: string; view: React.ReactElement }[][];
  taps: TapDetails[];
  users: UserDetails[];
  view: React.ReactElement;
}

class Dashboard extends React.Component<any, DashboardState> {
  constructor(props: any) {
    super(props);

    const apps = this.getApps();
    const view = <Home apps={apps} handleClick={this.setView} />;

    this.state = {
      apps: apps,
      breadcrumbs: [{ name: "Home", view: view }],
      flashMessages: [],
      history: [],
      taps: [],
      users: [],
      view: view
    };
  }

  getApps = () => {
    return [
      {
        breadcrumbs: ["Ditti App"],
        name: "Ditti App",
        id: 1,
        view: (
          <StudiesView
            getTapsAsync={this.getTapsAsync}
            getTaps={this.getTaps}
            handleClick={this.setView}
            goBack={this.goBack}
            flashMessage={this.flashMessage}
          />
        )
      },
      {
        breadcrumbs: ["Admin Dashboard", "Accounts"],
        name: "Admin Dashboard",
        id: 2,
        view: (
          <Accounts
            handleClick={this.setView}
            goBack={this.goBack}
            flashMessage={this.flashMessage}
          />
        )
      }
    ];
  };

  getTapsAsync = async (): Promise<TapDetails[]> => {
    // let { taps } = this.state;

    // if (!taps.length) {
    //   taps = await makeRequest("/aws/get-taps?app=2").then((res: Tap[]) => {
    //     return res.map((tap) => {
    //       return { dittiId: tap.dittiId, time: new Date(tap.time) };
    //     });
    //   });

    //   taps = taps.sort((a, b) =>
    //     differenceInMilliseconds(new Date(a.time), new Date(b.time))
    //   );

    //   this.setState({ taps });
    // }
    const taps = dummyData.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );
    this.setState({ taps });

    return taps;
  };

  getTaps = (): TapDetails[] => {
    return this.state.taps;
  };

  setView = (name: string[], view: React.ReactElement, replace?: boolean) => {
    let { breadcrumbs } = this.state;
    const { history } = this.state;

    history.push(breadcrumbs.slice(0));
    if (replace) breadcrumbs.pop();

    let i = 0;
    for (const b of breadcrumbs) {
      if (b.name === name[0]) {
        breadcrumbs = breadcrumbs.slice(0, i + 1);
        break;
      } else if (i === breadcrumbs.length - 1) {
        for (const i in name) {
          breadcrumbs.push({
            name: name[i],
            view: parseInt(i) === name.length - 1 ? view : <React.Fragment />
          });
        }

        break;
      }

      i++;
    }

    this.setState({ breadcrumbs, history, view });
  };

  setStudy = (name: string, view: React.ReactElement): void => {
    const { history } = this.state;
    let { breadcrumbs } = this.state;
    history.push(breadcrumbs.slice(0));

    breadcrumbs = breadcrumbs.slice(0, 2);

    if (breadcrumbs.length == 1) {
      const appView = (
        <StudiesView
          getTapsAsync={this.getTapsAsync}
          getTaps={this.getTaps}
          handleClick={this.setView}
          goBack={this.goBack}
          flashMessage={this.flashMessage}
        />
      );

      breadcrumbs.push({ name: "Ditti App", view: appView });
    }

    breadcrumbs.push({ name: name, view: view });
    this.setState({ breadcrumbs, history, view: <React.Fragment /> }, () =>
      this.setState({ view })
    );
  };

  goBack = () => {
    const { history } = this.state;
    const breadcrumbs = history.pop();

    if (breadcrumbs) {
      const view = breadcrumbs[breadcrumbs.length - 1].view;

      if (breadcrumbs.length == this.state.breadcrumbs.length)
        this.setState({ breadcrumbs, history, view: <React.Fragment /> }, () =>
          this.setState({ view })
        );
      else this.setState({ breadcrumbs, history, view });
    }
  };

  flashMessage = (msg: React.ReactElement, type: string): void => {
    const { flashMessages } = this.state;
    const id = flashMessages.length
      ? flashMessages[flashMessages.length - 1].id + 1
      : 0;

    const element = (
      <div key={id} className={"shadow flash-message flash-message-" + type}>
        <div className="flash-message-content">
          <span>{msg}</span>
        </div>
        <div
          className="flash-message-close"
          onClick={() => this.popMessage(id)}
        >
          <span>x</span>
        </div>
      </div>
    );

    flashMessages.push({ id, element });
    this.setState({ flashMessages });
  };

  popMessage = (id: number): void => {
    let { flashMessages } = this.state;
    flashMessages = flashMessages.filter((fm) => fm.id != id);
    this.setState({ flashMessages });
  };

  render() {
    const { breadcrumbs, flashMessages, history, view } = this.state;

    return (
      <main className="bg-light dashboard-container">
        <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
        <div
          style={{
            display: "flex",
            flexGrow: 1,
            maxHeight: "calc(100vh - 4rem)"
          }}
        >
          <StudiesMenu
            setView={this.setStudy}
            flashMessage={this.flashMessage}
            handleClick={this.setView}
            getTaps={this.getTaps}
            goBack={this.goBack}
          />
          <div className="dashboard-content">
            <Navbar
              breadcrumbs={breadcrumbs}
              handleBack={this.goBack}
              handleClick={this.setView}
              hasHistory={history.length > 0}
            />
            <div className="flash-message-container">
              {flashMessages.map((fm) => fm.element)}
            </div>
            {view}
          </div>
        </div>
      </main>
    );
  }
}

export default Dashboard;
