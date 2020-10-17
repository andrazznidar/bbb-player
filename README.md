# bbb-player

Download public BigBlueButton recordings and play them offline.

## Usage:

1. Download and unzip this repo.
2. Change working directory to this repo.
3. Download a recoreded BBB meeting using: `python3 bbb-player.py --download URL` where URL is your viewing url. `For example: python3 bbb-player.py --download https://bbb.example.com/playback/presentation/2.0/playback.html?meetingId=70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148`
4. Wait for download to complete.
5. Play the downloaded metting using: `python3 bbb-player.py --play meetingID` where meetingID is your meetingID from URL and is equal to a name of a folder inside `./downloadedMeetings`. `For example: python3 bbb-player.py --play 70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148``
6. Open a modern web browser and play the downloaded metting on `localhost:8000/player/playback.html`
7. When done press `CTRL+C` to stop the local server.
