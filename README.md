# bbb-player

Download public BigBlueButton recordings and play them offline.
Playback is to a great extent based on the BigBlueButton frontend called [bbb-playback](https://github.com/bigbluebutton/bbb-playback).

## Easy No-Install Playback in a Firefox browser with network connection:
If someone sent you a folder downloaded with bbb-player you can easily play the recording without installing anything.

0. Unzip the folder if it is zipped.
1. Open [servefolder.dev](https://servefolder.dev) in a desktop Firefox (ex. on Windows or macOS).
2. Click `Browse...`.
3. Select the folder of the meeting (make sure the selected folder contains folders like `static` and `styles`).
4. Click `Upload` and confirm. Please note that the files will not be actually uploaded. [Here is how it works.](https://github.com/AshleyScirra/servefolder.dev)
5. Click the generated link and enjoy the recording.


## Quickstart (recommended):
0. You must have [Docker](https://www.docker.com/products/docker-desktop).

1. Use the folowing command where `/path/to/your/folder/myBBBmeetings` is an absolute path to a folder where you wish to download recordings.
>`docker run -d --rm --name bbb-player -p 5000:5000 -v /path/to/your/folder/myBBBmeetings:/app/downloadedMeetings andrazznidar/bbb-player`

2. Open a modern web browser and download or play meetings on `http://localhost:5000/`.

3. When you are done you can use `docker stop bbb-player` to stop the container.


## Detailed usage

Must have **Python3.6** or later with **pip**. But not **Python3.12** or newer.

1. Download and unzip this repo (or use `git clone https://github.com/andrazznidar/bbb-player.git`).
1. Change working directory of your system console to this repo.
1. Optionally create a virtual environment: `python3 -m venv env` and activate it: `source ./env/bin/activate`
1. Install `requrements.txt` using: `pip install -r requirements.txt`
1. Download a recoreded BBB meeting using: `python bbb-player.py --download BBB_HTTPS_URL -n name_of_the_meeting` where **_BBB_HTTPS_URL_** is your meeting url and **_name_of_the_meeting_** is your name for the meeting.
   > Example: `python bbb-player.py --download https://bbb.example.com/playback/presentation/2.0/playback.html?meetingId=70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148 -n Favourite_meeting`
1. Wait for download to complete.
1. Serve a single web page with all the meetings with `python bbb-player.py -s`
1. Open a modern web browser and play the downloaded meeting on `http://localhost:5000/`.
   ![Favourite-meeting](https://user-images.githubusercontent.com/8482843/111150619-9a915c80-858e-11eb-9bd9-e256e8272acf.png)
1. When done press `CTRL+C` in the system console to stop the local server. And `deactivate` to exit the virtual env if you enabled it.

## Combining

If the downloaded BBB meeting was only using voice/webcam and video deskshare, you can combine webcam audio and deskshare video in one `mkv` video file.

1. Download the BBB meeting as specified in the first four steps of the `Usage` section in `README.md`.
2. Start the combining process using `python3 bbb-player.py --combine meetingID` where meetingID is your meetingID from the URL and is equal to a name of a folder inside of `./downloadedMeetings`.
   > Example: `python3 bbb-player.py --combine 70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148`
3. Wait for the process to complete.
4. Your combined video file is located in the specific meeting folder `./downloadedMeetings/meetingID/meetingID.mkv`. You can use this file as any other normal video file.
   > Example: `./downloadedMeetings/70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148/70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148.mkv`

## Docker

This project can be run in Docker.
>`docker run -p 5000:5000 -v /path/to/your/folder/myBBBmeetings:/app/downloadedMeetings andrazznidar/bbb-player`
