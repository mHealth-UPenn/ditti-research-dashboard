import { useEffect, useState } from "react";
import { AudioFile, AudioTap, AudioTapDetails, Tap, TapDetails, UserDetails } from "../interfaces";
import { APP_ENV } from "../environment";
import { makeRequest } from "../utils";
import DataFactory from "../dataFactory";
import { differenceInMilliseconds } from "date-fns";


// TODO: extend to customize default values when needed in future vizualizations
const useDittiData = () => {
  const [dataLoading, setDataLoading] = useState(true);
  const [taps, setTaps] = useState<TapDetails[]>([]);
  const [audioTaps, setAudioTaps] = useState<AudioTapDetails[]>([]);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [users, setUsers] = useState<UserDetails[]>([]);

  let dataFactory: DataFactory | null = null;
  if (APP_ENV === "development") {
    dataFactory = new DataFactory();
  }

  useEffect(() => {
    const promises: Promise<any>[] = [];

    if (APP_ENV === "production") {
      promises.push(getTapsAsync().then(setTaps));
      promises.push(getAudioTapsAsync().then(setAudioTaps));
      promises.push(getAudioFilesAsync().then(setAudioFiles));
      promises.push(getUsersAsync().then(setUsers));
    } else if (APP_ENV === "development" && dataFactory) {
      promises.push(dataFactory.init().then(() => {
        if (dataFactory) {
          setTaps(dataFactory.taps);
          setAudioTaps(dataFactory.audioTaps);
          setAudioFiles(dataFactory.audioFiles);
          setUsers(dataFactory.users);
        }
      }));
    }
    Promise.all(promises).then(() => setDataLoading(false));
  }, []);

  const getTapsAsync = async (): Promise<TapDetails[]> => {
    let taps: TapDetails[] = [];

    if (APP_ENV === "production") {
      taps = await makeRequest("/aws/get-taps?app=2").then((res: Tap[]) => {
        return res.map((tap) => {
          return { dittiId: tap.dittiId, time: new Date(tap.time) };
        });
      });
    } else if (dataFactory) {
      taps = dataFactory.taps;
    }

    // Sort taps by timestamp
    taps = taps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );

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
        });
    } else if (dataFactory) {
      audioTaps = dataFactory.audioTaps;
    }

    // sort taps by timestamp
    audioTaps = audioTaps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );

    return audioTaps;
  };

  const getAudioFilesAsync = async (): Promise<AudioFile[]> => {
    let audioFiles: AudioFile[] = [];

    if (APP_ENV === "production") {
      audioFiles = await makeRequest("/aws/get-audio-files?app=2");
    } else if (dataFactory) {
      audioFiles = dataFactory.audioFiles;
    }

    return audioFiles;
  };

  const getUsersAsync = async () => {
    let users: UserDetails[] = [];

    if (APP_ENV === "production") {
      users = await makeRequest("/aws/get-users?app=2");
    } else if (dataFactory) {
      users = dataFactory.users;
    }

    return users;
  };

  return {
    dataLoading,
    taps,
    audioTaps,
    audioFiles,
    users,
  };
};


export default useDittiData;
