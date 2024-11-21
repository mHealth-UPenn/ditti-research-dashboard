import { useEffect, useMemo, useState } from "react";
import { AudioFile, AudioTap, AudioTapDetails, Study, Tap, TapDetails, User, UserDetails } from "../interfaces";
import { APP_ENV } from "../environment";
import { makeRequest } from "../utils";
import DataFactory from "../dataFactory";
import { differenceInMilliseconds } from "date-fns";


// TODO: extend to customize default values when needed in future vizualizations
const useDittiData = () => {
  const [dataLoading, setDataLoading] = useState(true);
  const [studies, setStudies] = useState<Study[]>([]);
  const [taps, setTaps] = useState<TapDetails[]>([]);
  const [audioTaps, setAudioTaps] = useState<AudioTapDetails[]>([]);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [users, setUsers] = useState<UserDetails[]>([]);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
    const promises: Promise<any>[] = [];

    if (APP_ENV === "production") {
      promises.push(getTapsAsync().then(setTaps));
      promises.push(getAudioTapsAsync().then(setAudioTaps));
      promises.push(getAudioFilesAsync().then(setAudioFiles));
      promises.push(getUsersAsync().then(setUsers));
    } else if ((APP_ENV === "development" || APP_ENV === "demo") && dataFactory) {
      promises.push(dataFactory.init().then(() => {
        if (dataFactory) {
          setTaps(dataFactory.taps);
          setAudioTaps(dataFactory.audioTaps);
          setAudioFiles(dataFactory.audioFiles);
          setUsers(dataFactory.users);
        }
      }));
    }

    if (APP_ENV === "production" || APP_ENV === "development") {
      promises.push(getStudiesAsync().then(setStudies));
    } else if (APP_ENV === "demo" && dataFactory) {
      setStudies(dataFactory.studies);
    }

    Promise.all(promises).then(() => setDataLoading(false));
  }, []);

  const getStudiesAsync = async (): Promise<Study[]> => {
    let studies: Study[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      studies = await makeRequest("/db/get-studies?app=2")
        .catch(() => {
          console.error("Unable to fetch studies data. Check account permissions.")
          return [];
        });
    } else if (dataFactory) {
      studies = dataFactory.studies;
    }

    return studies;
  };

  const getTapsAsync = async (): Promise<TapDetails[]> => {
    let taps: TapDetails[] = [];

    if (APP_ENV === "production") {
      taps = await makeRequest("/aws/get-taps?app=2").then((res: Tap[]) => {
        return res.map((tap) => {
          return { dittiId: tap.dittiId, time: new Date(tap.time), timezone: tap.timezone };
        });
      }).catch(() => {
        console.error("Unable to fetch taps data. Check account permissions.")
        return [];
      });
    } else if (dataFactory) {
      taps = dataFactory.taps;
    }

    // Sort taps by timestamp
    taps = taps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );

    console.debug("Taps:", taps);
    return taps;
  };

  const getAudioTapsAsync = async (): Promise<AudioTapDetails[]> => {
    let audioTaps: AudioTapDetails[] = [];

    if (APP_ENV == "production") {
      audioTaps = await makeRequest("/aws/get-audio-taps?app=2")
        .then((res: AudioTap[]) => {
          return res.map((at) => {
            return {
              dittiId: at.dittiId,
              audioFileTitle: at.audioFileTitle,
              time: new Date(at.time),
              timezone: at.timezone,
              action: at.action,
            };
          });
        }).catch(() => {
          console.error("Unable to fetch audio taps data. Check account permissions.")
          return [];
        });
    } else if (dataFactory) {
      audioTaps = dataFactory.audioTaps;
    }

    // sort taps by timestamp
    audioTaps = audioTaps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );

    console.debug("AudioTaps:", audioTaps);
    return audioTaps;
  };

  const getAudioFilesAsync = async (): Promise<AudioFile[]> => {
    let audioFiles: AudioFile[] = [];

    if (APP_ENV === "production") {
      audioFiles = await makeRequest("/aws/get-audio-files?app=2")
        .catch(() => {
          console.error("Unable to fetch audio files. Check account permissions.")
          return [];
        });
    } else if (dataFactory) {
      audioFiles = dataFactory.audioFiles;
    }

    return audioFiles;
  };

  const getUsersAsync = async () => {
    let users: UserDetails[] = [];

    if (APP_ENV === "production") {
      users = await makeRequest("/aws/get-users?app=2")
        .catch(() => {
          console.error("Unable to fetch users. Check account permissions.")
          return [];
        });
    } else if (dataFactory) {
      users = dataFactory.users;
    }

    console.debug("Users:", users);
    return users;
  };

  const refreshAudioFiles = async () => {
    setAudioFiles(await getAudioFilesAsync());
  }

  const getUserByDittiId = async (id: string): Promise<User> => {
    const userFilter = users.filter(u => u.userPermissionId === id);

    if (userFilter.length) {
      const user = userFilter[0];
      return {
        tap_permission: user.tapPermission,
        information: user.information,
        user_permission_id: user.userPermissionId,
        exp_time: user.expTime,
        team_email: user.teamEmail,
        createdAt: user.createdAt,
        __typename: "",
        _lastChangedAt: 0,
        _version: 0,
        updatedAt: "",
        id: "",
      }
    }

    return {
      tap_permission: true,
      information: "",
      user_permission_id: "",
      exp_time: "",
      team_email: "",
      createdAt: "",
      __typename: "",
      _lastChangedAt: 0,
      _version: 0,
      updatedAt: "",
      id: "",
    }
  }

  return {
    dataLoading,
    studies,
    taps,
    audioTaps,
    audioFiles,
    users,
    refreshAudioFiles,
    getUserByDittiId,
  };
};


export default useDittiData;
