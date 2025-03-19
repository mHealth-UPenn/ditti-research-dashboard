import { APP_ENV } from "./environment";
import { AudioFile, AudioTapDetails, ISleepLevel, ISleepLevelClassic, ISleepLevelStages, ISleepLog, Study, TapDetails, UserDetails } from "./interfaces";
import { makeRequest } from "./utils";

const aboutSleepTemplate = `<div>
  <h1>About Sleep</h1>
  <p>This is an about sleep template</p>
</div>`;


const generateAudioFiles = (): AudioFile[] => {
  const categories = ["Nature", "Voice", "Noise", "Music"];
  const audioFiles = [];

  for (let i = 0; i < 20; i++) {
    const audioFile = {
      id: `audio_${i + 1}`,
      _version: 1,
      fileName: `file_${i + 1}.mp3`,
      title: `Audio File ${i + 1}`,
      category: categories[Math.floor(Math.random() * categories.length)],
      availability: "",
      studies: [],
      length: 300
    };

    audioFiles.push(audioFile);
  }

  return audioFiles;
}


const generateUsers = (studyIds: string[]): UserDetails[] => {
  const users: UserDetails[] = [];

  studyIds.forEach(studyId => {
    for (let i = 1; i <= 10; i++) {
      const user = {
        tapPermission: true,
        information: aboutSleepTemplate,
        userPermissionId: `${studyId}${String(i).padStart(3, "0")}`,
        expTime: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
        teamEmail: `${studyId}@email.com`,
        createdAt: new Date().toISOString()
      };

      users.push(user);
    }
  });

  return users;
}


const generateTaps = (
  dittiIds: string[],
  audioFileNames: string[]
): [TapDetails[], AudioTapDetails[]] => {
  const taps: TapDetails[] = [];
  const audioTaps: AudioTapDetails[] = [];
  const timezones = [
    "",
    "GMT Universal Coordinated Time",
    "GMT-05:00 Eastern Standard Time",
    "GMT-04:00 Eastern Daylight Time",
  ]

  dittiIds.forEach(dittiId => {
    const now = new Date();

    // Loop through the last seven days
    for (let daysAgo = 1; daysAgo <= 7; daysAgo++) {
      const timezone = timezones[Math.floor(Math.random() * timezones.length)];
      const day = new Date(now);
      day.setDate(now.getDate() - daysAgo);

      // Generate one or two tapping bouts
      const tappingBoutsCount = Math.random() < 0.5 ? 1 : 2;
      let lastBoutEndTime = null;

      for (let bout = 0; bout < tappingBoutsCount; bout++) {
        const isAudioTappingBout = Math.random() < 0.5;

        // Start the tapping bout at a random time between 10pm and 12am
        const boutStartHour = 22 + Math.floor(Math.random() * 2);
        const boutStartMinute = Math.floor(Math.random() * 60);
        const boutStart = new Date(day);
        boutStart.setHours(boutStartHour, boutStartMinute, 0, 0);

        if (lastBoutEndTime) {
          boutStart.setTime(
            lastBoutEndTime.getTime() + (30 + Math.random() * 30) * 60000
          );
        }

        if (isAudioTappingBout) {
          // Generate an audio tapping bout
          const index = Math.floor(Math.random() * audioFileNames.length)
          const audioFileName = audioFileNames[index];
          const audioTapsInBout = 2 + Math.floor(Math.random() * 9);
          let tapTime = new Date(boutStart);

          for (let i = 0; i < audioTapsInBout; i++) {
            audioTaps.push({
              dittiId,
              time: new Date(tapTime),
              timezone,
              audioFileTitle: audioFileName,
              action: i === 0 ? "play" : "resume"
            });

            const delta = (310 + Math.floor(Math.random() * 31)) * 1000;
            tapTime = new Date(tapTime.getTime() + delta);
          }

          lastBoutEndTime = new Date(tapTime);
        } else {
          // Generate a regular tapping bout
          const tapsInBout = 20 + Math.floor(Math.random() * 81);
          let tapTime = new Date(boutStart);

          for (let i = 0; i < tapsInBout; i++) {
            taps.push({ dittiId, time: new Date(tapTime), timezone });

            const delta = (10 + Math.floor(Math.random() * 11)) * 1000;
            tapTime = new Date(tapTime.getTime() + delta);
          }

          lastBoutEndTime = new Date(tapTime);
        }
      }
    }
  });

  return [taps, audioTaps];
}


const generateRandomTimeBetween = (startHour: number, endHour: number) => {
  const today = new Date();
  const start = new Date(today.setHours(startHour, 0, 0, 0)).getTime();
  const end = new Date(today.setHours(endHour, 0, 0, 0)).getTime();
  const randomTime = new Date(start + Math.random() * (end - start));
  return randomTime;
}


const getRandomLevelStages = (prev: ISleepLevelStages): ISleepLevelStages => {
  const levels: ISleepLevelStages[] = ["deep", "light", "rem", "wake"];
  const levelsFiltered = levels.filter(l => l !== prev);
  const randomIndex = Math.floor(Math.random() * levelsFiltered.length);
  return levelsFiltered[randomIndex];
}


const getRandomLevelClassic = (prev: ISleepLevelClassic): ISleepLevelClassic => {
  const levels: ISleepLevelClassic[] = ["asleep", "awake", "restless"];
  const levelsFiltered = levels.filter(l => l !== prev);
  const randomIndex = Math.floor(Math.random() * levelsFiltered.length);
  return levelsFiltered[randomIndex];
}


const generateSleepLogs = (): ISleepLog[] => {
  const sleepLogs: ISleepLog[] = [];
  const levelsStages: ISleepLevelStages[] = ["deep", "light", "rem", "wake"];
  const levelsClassic: ISleepLevelClassic[] = ["asleep", "awake", "restless"];
  const classicDay = Math.ceil(Math.random() * 7);

  for (let i = 7; i >= 1; i--) {
    const dateOfSleep = new Date();
    const dateOffset = dateOfSleep.getDate() - i
    dateOfSleep.setDate(dateOffset);

    const startTime = generateRandomTimeBetween(22, 24); // Random time between 10pm and 12am
    startTime.setDate(dateOffset)

    const sleepLog: ISleepLog = {
      dateOfSleep: dateOfSleep.toISOString(),
      logType: "auto_detected",
      type: i === classicDay ? "classic" : "stages",
      levels: [],
    };

    let previousLevel: ISleepLevel | null = null;
    let totalDurationMinutes = 0;
    // Simulate between six to eight hours
    const maxDurationMinutes = 360 + Math.random() * 120;

    while (totalDurationMinutes < maxDurationMinutes) {
      // Random between 5 and 30 minutes
      const seconds = Math.floor(Math.random() * (30 * 60 - 5 * 60)) + 5 * 60;
      const dateTime = previousLevel
        ? new Date(new Date(previousLevel.dateTime).getTime() + previousLevel.seconds * 1000)
        : startTime;

      const level: ISleepLevel = {
        dateTime: dateTime.toISOString(),
        seconds,
        isShort: null,
        level: i === classicDay
          // Use classic
          ? previousLevel
          ? getRandomLevelClassic(previousLevel.level as ISleepLevelClassic)
          : levelsClassic[Math.floor(Math.random() * levelsClassic.length)]
          // Use stages
          : previousLevel
          ? getRandomLevelStages(previousLevel.level as ISleepLevelStages)
          : levelsStages[Math.floor(Math.random() * levelsStages.length)]
      };

      sleepLog.levels.push(level);
      previousLevel = level;
      totalDurationMinutes += seconds / 60;
    }

    sleepLogs.push(sleepLog);
  }

  return sleepLogs;
}


class DataFactory {
  private initialized: boolean;
  public studies: Study[];
  public taps: TapDetails[];
  public audioTaps: AudioTapDetails[];
  public audioFiles: AudioFile[];
  public users: UserDetails[];
  public sleepLogs: ISleepLog[];

  constructor() {
    this.initialized = false;
    this.studies = [];
    this.taps = [];
    this.audioTaps = [];
    this.audioFiles = [];
    this.users = [];
    this.sleepLogs = [];
  }

  async init() {
    if (!this.initialized) {
      this.studies = [
        {
          id: 1,
          name: "Sleep and Lifestyle Enhancement through Evidence-based Practices for Insomnia Treatment",
          acronym: "SLEEP-IT",
          dittiId: "sit",
          email: "sleep.it@research.edu",
          defaultExpiryDelta: 30,
          isQi: false,
          consentInformation: "Consent Information",
        },
        {
          id: 2,
          name: "Cognitive and Affective Lifestyle Modifications for Sleep Enhancement through Mindfulness Practices",
          acronym: "CALM-SLEEP",
          dittiId: "cs",
          email: "calm.sleep@research.edu",
          defaultExpiryDelta: 45,
          isQi: true,
          consentInformation: "Consent Information",
        }
      ];

      if (APP_ENV !== "demo") {
        try {
          this.studies = await makeRequest("/db/get-studies");
        } catch (error) {
          console.error(error);
        }
      }

      const studyIds = this.studies.map(s => s.dittiId);
      this.users = generateUsers(studyIds);
      this.audioFiles = generateAudioFiles();
      const userIds = this.users.map(u => u.userPermissionId);
      const audioFileNames = this.audioFiles.map(af => af.fileName)
        .filter((s): s is string => s !== undefined);
      [this.taps, this.audioTaps] = generateTaps(userIds, audioFileNames);
      this.sleepLogs = generateSleepLogs();
      this.initialized = true;
    }
  }
}

export default DataFactory;
