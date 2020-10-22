# bbb-player

Download public BigBlueButton recordings and play them offline.
Playback is to a great extent based on the [BigBlueButton](https://github.com/bigbluebutton) frontend.

## Usage

1. Download and unzip this repo.
2. Change working directory to this repo.
3. Install `requrements.txt` using: `pip3 install -r requirements.txt`
4. Download a recoreded BBB meeting using: `python3 bbb-player.py --download URL` where URL is your viewing url.
   > Example: `python3 bbb-player.py --download https://bbb.example.com/playback/presentation/2.0/playback.html?meetingId=70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148`
5. Wait for download to complete.
6. Play the downloaded metting using: `python3 bbb-player.py --play meetingID` where meetingID is your meetingID from the URL and is equal to a name of a folder inside of `./downloadedMeetings`.
   > Example: `python3 bbb-player.py --play 70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148`
7. Open a modern web browser and play the downloaded meeting on `http://localhost:8000/player/playback.html`.
8. When done press `CTRL+C` to stop the local server.

## Combining

If the downloaded BBB meeting was only using voice/webcam and video deskshare, you can combine webcam audio and deskshare video in one `mkv` video file.

1. Download the BBB meeting as specified in the first four steps of the `Usage` section in `README.md`.
2. Start the combining process using `python3 bbb-player.py --combine meetingID` where meetingID is your meetingID from the URL and is equal to a name of a folder inside of `./downloadedMeetings`.
   > Example: `python3 bbb-player.py --combine 70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148`
3. Wait for the process to complete.
4. Your combined video file is located in the specific meeting folder `./downloadedMeetings/meetingID/combine-output.mkv`. You can use this file as any other normal video file.
   > Example: `./downloadedMeetings/70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148/combine-output.mkv`
