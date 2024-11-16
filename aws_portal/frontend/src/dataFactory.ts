import { AudioFile, AudioTapDetails, ISleepLevel, ISleepLevelLevel, ISleepLog, Study, TapDetails, UserDetails } from "./interfaces";
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

  dittiIds.forEach(dittiId => {
    const now = new Date();

    // Loop through the last seven days
    for (let daysAgo = 1; daysAgo <= 7; daysAgo++) {
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
              timezone: "",
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
            taps.push({ dittiId, time: new Date(tapTime) });

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


const getRandomLevel = (prev: ISleepLevelLevel): ISleepLevelLevel => {
  const levels: ISleepLevelLevel[] = ["deep", "light", "rem", "wake"];
  const randomIndex = Math.floor(Math.random() * levels.length - 1);
  return levels.filter(l => l !== prev)[randomIndex];
}


const generateSleepLogs = (): ISleepLog[] => {
  const sleepLogs: ISleepLog[] = [];
  const levels: ISleepLevelLevel[] = ["deep", "light", "rem", "wake"];

  for (let i = 1; i <= 7; i++) {
    const dateOfSleep = new Date();
    dateOfSleep.setDate(dateOfSleep.getDate() - i);

    const startTime = generateRandomTimeBetween(22, 24); // Random time between 10pm and 12am

    const sleepLog: ISleepLog = {
      dateOfSleep: dateOfSleep,
      startTime: startTime,
      type: "stages",
      levels: [],
    };

    let previousLevel: ISleepLevel | null = null;
    let totalDurationMinutes = 0;
    // Simulate between six to eight hours
    const maxDurationMinutes = 360 + Math.random() * 120;

    while (totalDurationMinutes < maxDurationMinutes) {
      // Random between 5 and 30 minutes
      const seconds = Math.floor(Math.random() * (30 * 60 - 5 * 60)) + 5 * 60;

      const level: ISleepLevel = {
        dateTime: previousLevel
          ? new Date(new Date(previousLevel.dateTime).getTime() + previousLevel.seconds * 1000)
          : startTime,
        seconds,
        isShort: null,
        level: previousLevel
          ? getRandomLevel(previousLevel.level)
          : levels[Math.floor(Math.random() * levels.length)],
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
  public taps: TapDetails[];
  public audioTaps: AudioTapDetails[];
  public audioFiles: AudioFile[];
  public users: UserDetails[];
  public sleepLogs: ISleepLog[];

  constructor() {
    this.initialized = false;
    this.taps = [];
    this.audioTaps = [];
    this.audioFiles = [];
    this.users = [];
    this.sleepLogs = [];
  }

  async init() {
    if (!this.initialized) {
      try {
        const studies: Study[] = await makeRequest("/db/get-studies?app=2");
        const studyIds = studies.map(s => s.dittiId);
        this.users = generateUsers(studyIds);
      } catch (err) {
        console.error(err);
      }

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
