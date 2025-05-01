import { APP_ENV } from "../environment";
import { makeRequest } from "../utils";
import { DataFactory } from "../dataFactory";
import { differenceInMilliseconds } from "date-fns";
import {
  createContext,
  PropsWithChildren,
  useState,
  useMemo,
  useEffect,
  useCallback,
} from "react";
import { DittiDataContextValue } from "./dittiDataContext.types";
import { AudioFile, AudioTap, Tap } from "../types/api";
import { TapModel, AudioTapModel } from "../types/models";

export const DittiDataContext = createContext<
  DittiDataContextValue | undefined
>(undefined);

export const DittiDataProvider = ({ children }: PropsWithChildren) => {
  const [dataLoading, setDataLoading] = useState(true);
  const [taps, setTaps] = useState<TapModel[]>([]);
  const [audioTaps, setAudioTaps] = useState<AudioTapModel[]>([]);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  const getTapsAsync = useCallback(async (): Promise<TapModel[]> => {
    let taps: TapModel[] = [];

    if (APP_ENV === "production") {
      taps = await makeRequest("/aws/get-taps?app=2")
        .then((res) => {
          const tapsData = res as unknown as Tap[];
          return tapsData.map((tap) => {
            return {
              dittiId: tap.dittiId,
              time: new Date(tap.time),
              timezone: tap.timezone,
            };
          });
        })
        .catch(() => {
          console.error(
            "Unable to fetch taps data. Check account permissions."
          );
          return [];
        });
    } else if (dataFactory) {
      taps = dataFactory.taps;
    }

    // Sort taps by timestamp
    taps = taps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );

    return taps;
  }, [dataFactory]);

  const getAudioTapsAsync = useCallback(async (): Promise<AudioTapModel[]> => {
    let audioTaps: AudioTapModel[] = [];

    if (APP_ENV == "production") {
      audioTaps = await makeRequest("/aws/get-audio-taps?app=2")
        .then((res) => {
          const audioTapsData = res as unknown as AudioTap[];
          return audioTapsData.map((at) => {
            return {
              dittiId: at.dittiId,
              audioFileTitle: at.audioFileTitle,
              time: new Date(at.time),
              timezone: at.timezone,
              action: at.action,
            };
          });
        })
        .catch(() => {
          console.error(
            "Unable to fetch audio taps data. Check account permissions."
          );
          return [];
        });
    } else if (dataFactory) {
      audioTaps = dataFactory.audioTaps;
    }

    // sort taps by timestamp
    audioTaps = audioTaps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );

    return audioTaps;
  }, [dataFactory]);

  const getAudioFilesAsync = useCallback(async (): Promise<AudioFile[]> => {
    let audioFiles: AudioFile[] = [];

    if (APP_ENV === "production") {
      audioFiles = (await makeRequest("/aws/get-audio-files?app=2").catch(
        () => {
          console.error(
            "Unable to fetch audio files. Check account permissions."
          );
          return [];
        }
      )) as unknown as AudioFile[];
    } else if (dataFactory) {
      audioFiles = dataFactory.audioFiles;
    }

    return audioFiles;
  }, [dataFactory]);

  useEffect(() => {
    const promises: Promise<void>[] = [];

    if (APP_ENV === "production") {
      promises.push(getTapsAsync().then(setTaps));
      promises.push(getAudioTapsAsync().then(setAudioTaps));
      promises.push(getAudioFilesAsync().then(setAudioFiles));
    } else if (
      (APP_ENV === "development" || APP_ENV === "demo") &&
      dataFactory
    ) {
      promises.push(
        dataFactory.init().then(() => {
          setTaps(dataFactory.taps);
          setAudioTaps(dataFactory.audioTaps);
          setAudioFiles(dataFactory.audioFiles);
        })
      );
    }

    Promise.all(promises)
      .then(() => {
        setDataLoading(false);
      })
      .catch((error: unknown) => {
        console.error("Error during initial data fetch:", error);
        setDataLoading(false);
      });
  }, [dataFactory, getAudioFilesAsync, getAudioTapsAsync, getTapsAsync]);

  const refreshAudioFiles = async () => {
    setAudioFiles(await getAudioFilesAsync());
  };

  return (
    <DittiDataContext.Provider
      value={{
        dataLoading,
        taps,
        audioTaps,
        audioFiles,
        refreshAudioFiles,
      }}
    >
      {children}
    </DittiDataContext.Provider>
  );
};
