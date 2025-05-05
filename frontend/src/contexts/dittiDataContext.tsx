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

import { APP_ENV } from "../environment";
import { httpClient } from "../lib/http";
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
      try {
        const tapsData = await httpClient.request<Tap[]>("/aws/get-taps?app=2");
        taps = tapsData.map((tap) => ({
          dittiId: tap.dittiId,
          time: new Date(tap.time),
          timezone: tap.timezone,
        }));
      } catch (error) {
        console.error(
          "Unable to fetch taps data. Check account permissions.",
          error
        );
      }
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
      try {
        const audioTapsData = await httpClient.request<AudioTap[]>(
          "/aws/get-audio-taps?app=2"
        );
        audioTaps = audioTapsData.map((at) => ({
          dittiId: at.dittiId,
          audioFileTitle: at.audioFileTitle,
          time: new Date(at.time),
          timezone: at.timezone,
          action: at.action,
        }));
      } catch (error) {
        console.error(
          "Unable to fetch audio taps data. Check account permissions.",
          error
        );
      }
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
      try {
        audioFiles = await httpClient.request<AudioFile[]>(
          "/aws/get-audio-files?app=2"
        );
      } catch (error) {
        console.error(
          "Unable to fetch audio files. Check account permissions.",
          error
        );
      }
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
