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
import { APP_ENV } from "../environment";
import { makeRequest } from "../utils";
import { DataFactory } from "../dataFactory";
import { differenceInMilliseconds } from "date-fns";
import { createContext, PropsWithChildren, useState, useMemo, useEffect } from "react";
import { DittiDataContextValue } from "./dittiDataContext.types";
import { AudioFile, AudioTap, Tap } from "../types/api";
import { TapModel, AudioTapModel } from "../types/models";

export const DittiDataContext = createContext<DittiDataContextValue | undefined>(undefined);

export const DittiDataProvider = ({ children }: PropsWithChildren<unknown>) => {
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

  useEffect(() => {
    const promises: Promise<void>[] = [];

    if (APP_ENV === "production") {
      promises.push(getTapsAsync().then(setTaps));
      promises.push(getAudioTapsAsync().then(setAudioTaps));
      promises.push(getAudioFilesAsync().then(setAudioFiles));
    } else if ((APP_ENV === "development" || APP_ENV === "demo") && dataFactory) {
      promises.push(dataFactory.init().then(() => {
        if (dataFactory) {
          setTaps(dataFactory.taps);
          setAudioTaps(dataFactory.audioTaps);
          setAudioFiles(dataFactory.audioFiles);
        }
      }));
    }

    Promise.all(promises).then(() => setDataLoading(false));
  }, []);

  const getTapsAsync = async (): Promise<TapModel[]> => {
    let taps: TapModel[] = [];

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

    return taps;
  };

  const getAudioTapsAsync = async (): Promise<AudioTapModel[]> => {
    let audioTaps: AudioTapModel[] = [];

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

  const refreshAudioFiles = async () => {
    setAudioFiles(await getAudioFilesAsync());
  }

  return (
    <DittiDataContext.Provider value={{ 
      dataLoading,
      taps,
      audioTaps,
      audioFiles,
      refreshAudioFiles,
    }}>
      {children}
    </DittiDataContext.Provider>
  );
}
