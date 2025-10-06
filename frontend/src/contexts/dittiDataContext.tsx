/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { httpClient } from "../lib/http";
import { differenceInMilliseconds } from "date-fns";
import {
  createContext,
  PropsWithChildren,
  useState,
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

  const getTapsAsync = useCallback(async (): Promise<TapModel[]> => {
    const taps = await httpClient
      .request<Tap[]>("/aws/get-taps?app=2")
      .then((res: Tap[]) => {
        return res.map((tap) => {
          return {
            dittiId: tap.dittiId,
            time: new Date(tap.time),
            timezone: tap.timezone,
          };
        });
      })
      .catch(() => {
        console.error("Unable to fetch taps data. Check account permissions.");
        return [];
      });

    // Sort taps by timestamp
    return taps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );
  }, []);

  const getAudioTapsAsync = useCallback(async (): Promise<AudioTapModel[]> => {
    const audioTaps = await httpClient
      .request<AudioTap[]>("/aws/get-audio-taps?app=2")
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
      })
      .catch(() => {
        console.error(
          "Unable to fetch audio taps data. Check account permissions."
        );
        return [];
      });

    // sort taps by timestamp
    return audioTaps.sort((a, b) =>
      differenceInMilliseconds(new Date(a.time), new Date(b.time))
    );
  }, []);

  const getAudioFilesAsync = useCallback(async (): Promise<AudioFile[]> => {
    return await httpClient
      .request<AudioFile[]>("/aws/get-audio-files?app=2")
      .catch(() => {
        console.error(
          "Unable to fetch audio files. Check account permissions."
        );
        return [] as AudioFile[];
      });
  }, []);

  useEffect(() => {
    const promises: Promise<void>[] = [];

    promises.push(getTapsAsync().then(setTaps));
    promises.push(getAudioTapsAsync().then(setAudioTaps));
    promises.push(getAudioFilesAsync().then(setAudioFiles));

    Promise.all(promises)
      .then(() => {
        setDataLoading(false);
      })
      .catch((error: unknown) => {
        console.error("Error during initial data fetch:", error);
        setDataLoading(false);
      });
  }, [getAudioFilesAsync, getAudioTapsAsync, getTapsAsync]);

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
