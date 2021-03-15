# bbb-player

Download public BigBlueButton recordings and play them offline.
Playback is to a great extent based on the BigBlueButton frontend called [bbb-playback](https://github.com/bigbluebutton/bbb-playback).

### Quickstart:

Must have **Python3.6** or later (with **pip**)

```bash
# download and create a virtual environment
git clone git@github.com:andrazznidar/bbb-player.git && cd bbb-player
python3 -m venv env && source ./env/bin/activate
pip install -r requirements.txt

# to download the meetings:
source ./env/bin/activate
python bbb-player.py -d bbb_recoding_https_url -n name_of_the_meeting

# to serve a webpage where all the meetings are available
source ./env/bin/activate
python bbb-player.py -s

# to deactivate the virtual env:
deactivate
```

## Detailed usage

1. Download and unzip this repo.
1. Change working directory of your system console to this repo.
1. Optionally create a virtual environment: `python3 -m venv env` and activate it: `source ./env/bin/activate`
1. Install `requrements.txt` using: `pip install -r requirements.txt`
1. Download a recoreded BBB meeting using: `python bbb-player.py --download BBB_HTTPS_URL -n name_of_the_meeting` where **_BBB_HTTPS_URL_** is your meeting url and **_name_of_the_meeting_** is your name for the meeting.
   > Example: `python bbb-player.py --download https://bbb.example.com/playback/presentation/2.0/playback.html?meetingId=70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148 -n name_of_the_meeting`
1. Wait for download to complete.
1. Serve a single web page with all the meetings with `python bbb-player.py -s`
1. Open a modern web browser and play the downloaded meeting on `http://localhost:5000/`.
   ![image](https://user-images.githubusercontent.com/25982642/99105478-e59c6280-25e2-11eb-8537-ee06ad9aff0c.png)
1. When done press `CTRL+C` in the system console to stop the local server. And `deactivate` to exit the virtual env

## Combining

If the downloaded BBB meeting was only using voice/webcam and video deskshare, you can combine webcam audio and deskshare video in one `mkv` video file.

1. Download the BBB meeting as specified in the first four steps of the `Usage` section in `README.md`.
2. Start the combining process using `python3 bbb-player.py --combine meetingID` where meetingID is your meetingID from the URL and is equal to a name of a folder inside of `./downloadedMeetings`.
   > Example: `python3 bbb-player.py --combine 70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148`
3. Wait for the process to complete.
4. Your combined video file is located in the specific meeting folder `./downloadedMeetings/meetingID/meetingID.mkv`. You can use this file as any other normal video file.
   > Example: `./downloadedMeetings/70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148/70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148.mkv`
