import { AudioFile, AudioTapDetails, Study, TapDetails, User, UserDetails } from "./interfaces";
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


class DataFactory {
  taps: TapDetails[];
  audioTaps: AudioTapDetails[];
  audioFiles: AudioFile[];
  users: UserDetails[];

  constructor() {
    this.taps = []
    this.audioTaps = []
    this.audioFiles = []
    this.users = []
  }

  async init() {
    const studies: Study[] = await makeRequest("/db/get-studies?app=2");
    const studyIds = studies.map(s => s.dittiId);
    this.audioFiles = generateAudioFiles();
    this.users = generateUsers(studyIds);

    const userIds = this.users.map(u => u.userPermissionId);
    const audioFileNames = this.audioFiles.map(af => af.fileName)
      .filter((s): s is string => s !== undefined);
    [this.taps, this.audioTaps] = generateTaps(userIds, audioFileNames);
  }
}

export default DataFactory;
