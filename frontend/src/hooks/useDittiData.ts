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

import { useEffect, useMemo, useState } from "react";
import { AudioFile, AudioTap, AudioTapDetails, Tap, TapDetails } from "../interfaces";
import { APP_ENV } from "../environment";
import { makeRequest } from "../utils";
import { DataFactory } from "../dataFactory";
import { differenceInMilliseconds } from "date-fns";


// TODO: extend to customize default values when needed in future vizualizations
export const useDittiData = () => {
  const [dataLoading, setDataLoading] = useState(true);
  const [taps, setTaps] = useState<TapDetails[]>([]);
  const [audioTaps, setAudioTaps] = useState<AudioTapDetails[]>([]);
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

  return {
    dataLoading,
    taps,
    audioTaps,
    audioFiles,
    refreshAudioFiles,
  };
};
