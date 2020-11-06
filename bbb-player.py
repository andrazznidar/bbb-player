import argparse
from urllib.parse import urlparse
import os
import urllib.request
import json
from distutils.dir_util import copy_tree
import traceback
import re
from datetime import timedelta


DOWNLOADED_FULLY_FILENAME = "rec_fully_downloaded.txt"
DOWNLOADED_MEETINGS_FOLDER = "downloadedMeetings"
DEFAULT_COMBINED_VIDEO_NAME = "combine-output"
COMBINED_VIDEO_FORMAT = "mkv"


def ffmpegCombine(suffix, fileName=DEFAULT_COMBINED_VIDEO_NAME):
    try:
        import ffmpeg
    except:
        print("ffmpeg-python not imported. Try running:")
        print("pip3 install ffmpeg-python")
        exit(1)

    print("ffmpeg-python imported.")

    video_file = ffmpeg.input('./deskshare/deskshare.' + suffix)
    audio_file = ffmpeg.input('./video/webcams.' + suffix)

    # Based on https://www.reddit.com/r/learnpython/comments/ey41dp/merging_video_and_audio_using_ffmpegpython/fgf1oyq/
    output = ffmpeg.output(video_file, audio_file, f'{fileName}.{COMBINED_VIDEO_FORMAT}',
                           vcodec='copy', acodec='copy', map='-1:v:0', strict='very')

    ffmpeg.run(output)


def downloadFiles(baseURL, basePath):
    filesForDL = ["captions.json", "cursor.xml", "deskshare.xml", "presentation/deskshare.png", "metadata.xml", "panzooms.xml", "presentation_text.json",
                  "shapes.svg", "slides_new.xml", "video/webcams.webm", "video/webcams.mp4", "deskshare/deskshare.webm", "deskshare/deskshare.mp4",
                  "favicon.ico"]

    for file in filesForDL:
        print('Downloading ' + file)
        downloadURL = baseURL + file
        print(downloadURL)
        savePath = os.path.join(basePath, file)
        print(savePath)

        try:
            urllib.request.urlretrieve(
                downloadURL, savePath, reporthook=bar.on_urlretrieve if bar else None)
        except Exception:
            traceback.print_exc()
            print("Did not download " + file)


def downloadSlides(baseURL, basePath):
    # Part of this is based on https://www.programiz.com/python-programming/json
    with open(basePath + '/presentation_text.json') as f:
        data = json.load(f)
        for element in data:
            print(element)
            noSlides = len(data[element])
            print(noSlides)
            createFolder(os.path.join(basePath, 'presentation', element))
            for i in range(1, noSlides+1):
                downloadURL = baseURL + 'presentation/' + \
                    element + '/slide-' + str(i) + '.png'
                savePath = os.path.join(basePath, 'presentation',
                                        element,  'slide-{}.png'.format(i))

                print(downloadURL)
                print(savePath)

                try:
                    urllib.request.urlretrieve(
                        downloadURL, savePath, reporthook=bar.on_urlretrieve if bar else None)
                except:
                    print("Did not download " + element +
                          '/slide-' + str(i) + '.png')


def createFolder(path):
    # Create meeting folders, based on https://stackabuse.com/creating-and-deleting-directories-with-python/
    try:
        os.makedirs(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


# Parse the command line arguments
parser = argparse.ArgumentParser()
# group = parser.add_mutually_exclusive_group()
group = parser
group.add_argument("-d", "--download", type=str, nargs=1,
                   help="download the BBB conference linked here")
group.add_argument("-n", "--name", type=str, nargs=1,
                   help="define name of the conference (e.g. lecture1)")
group.add_argument("-p", "--play", type=str, nargs=1,
                   help="play a BBB conference saved locally. Full id string \
                   (e.g. d01a98b1a40329c5a43429ae487a599f437033b8-16328634322962) or \
                   the name you provided when downloading (e.g. lecture1)")
group.add_argument("-c", "--combine", type=str, nargs=1,
                   help="combine deskshare+audio of a BBB conference saved localy. Full id string \
                   (e.g. d01a98b1a40329c5a43429ae487a599f437033b8-16328634322962) or \
                   the name you provided when downloading (e.g. lecture1)")
args = parser.parse_args()

if(args.download != None and args.play == args.combine == None):
    print("Download")
    inputURL = args.download[0]

    meetingNameWanted = None
    if args.name:
        meetingNameWanted = args.name[0]

    # get meeting id from url https://regex101.com/r/UjqGeo/3
    matchesURL = re.search(r"/?(\d+\.\d+)/.*?([0-9a-f]{40}-\d{13})/?",
                          inputURL,
                          re.IGNORECASE)
    if matchesURL and len(matchesURL.groups()) == 2:
        bbbVersion = matchesURL.group(1)
        meetingId = matchesURL.group(2)
        print("Detected bbb version:\t{}\nDetected meeting id:\t{}".format(bbbVersion, meetingId))
    else:
        raise ValueError("Meeting ID could not be found in the url.")

    baseURL = "{}://{}/presentation/{}/".format(urlparse(inputURL).scheme,
                                                urlparse(inputURL).netloc,
                                                meetingId)
    print("Base url: {}".format(baseURL))

    if meetingNameWanted:
        folderPath = os.path.join(os.getcwd(), DOWNLOADED_MEETINGS_FOLDER, meetingNameWanted)
    else:
        folderPath = os.path.join(os.getcwd(), DOWNLOADED_MEETINGS_FOLDER, meetingId)
    print("Folder path: {}".format(folderPath))

    if os.path.isfile(os.path.join(folderPath, DOWNLOADED_FULLY_FILENAME)):
        print("Meeting is already downloaded.")
    else:
        print("Folder already created but not everything was downloaded. Retrying.")

        foldersToCreate = [os.path.join(folderPath, x) for x in ["", "video", "deskshare", "presentation"]]
        # print(foldersToCreate)
        for i in foldersToCreate:
            createFolder(i)

        try:
            from progressist import ProgressBar
            bar = ProgressBar(throttle=timedelta(seconds=1),
                template="Download |{animation}|{tta}| {done:B}/{total:B} at {speed:B}/s")
        except:
            print("progressist not imported. Progress bar will not be shown. Try running:")
            print("pip3 install progressist")
            bar = None

        downloadFiles(baseURL, folderPath)
        downloadSlides(baseURL, folderPath)
        copy_tree(os.path.join(os.getcwd(), "player"),
                  os.path.join(folderPath, "player"))
        with open(os.path.join(folderPath, DOWNLOADED_FULLY_FILENAME), 'w') as fp: 
            # write a downloaded_fully file to mark a successful download
            # todo: check if files were really dl-ed (make a json of files to download and
            #          check them one by one on success)
            pass

elif(args.play != None and args.name == args.download == args.combine == None):
    print("Play")
    fileId = args.play[0]

    try:
        from flask import Flask, redirect
    except:
        print("Flask not imported. Try running:")
        print("pip3 install Flask")
        exit(1)

    print("Flask imported.")

    print(os.getcwd())

    try:
        os.chdir(os.path.join(os.getcwd(), 'downloadedMeetings', fileId))
    except:
        print("Meeting with ID/name " + fileId +
              " is not downloaded. Download it first using the --download command")
        exit(1)

    print(os.getcwd())

    print('---------')
    print('In your modern web browser open:')
    print('http://localhost:5000/player/playback.html')
    print('Press CTRL+C when done.')
    print('---------')

    # Based on https://stackoverflow.com/a/42791810
    # Flask is needed for HTTP 206 Partial Content support.
    app = Flask(__name__,
                static_url_path='',
                static_folder=os.getcwd(),
                template_folder='')

    @app.route('/')
    def redirect_1(): return redirect(
        "http://localhost:5000/player/playback.html", code=307)

    # Based on https://stackoverflow.com/a/37331139
    # This is needed for playback of multiple meetings in short succession.
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TESTING'] = True

    if __name__ == "__main__":
        app.run()

elif(args.combine != None and args.name == args.download == args.play == None):
    print("Combine")
    fileIdOrName = args.combine[0]

    try:
        os.chdir('./downloadedMeetings/' + fileIdOrName)
    except:
        print(f"Meeting with ID {fileIdOrName} \
                is not downloaded. Download it first using the --download command")
        exit(1)

    matchesName = re.match(r"([0-9a-f]{40}-\d{13})", fileIdOrName, re.IGNORECASE)
    if matchesName:
        # if file id/name looks like bbb 54 char string use a simple predefined name
        meetingId = matchesName.group(0)
        print(f"Extracted meeting id: {meetingId} from provided name")
        print(f"Setting output file name to {DEFAULT_COMBINED_VIDEO_NAME}")
        fileName = DEFAULT_COMBINED_VIDEO_NAME
    else:
        fileName = fileIdOrName
        # todo: add name parsing from -n


    if(os.path.isfile(f'./{fileName}.{COMBINED_VIDEO_FORMAT}')):
        print(f'./{DEFAULT_COMBINED_VIDEO_NAME}.{COMBINED_VIDEO_FORMAT} already found. Aborting.')
        exit(1)
    elif(os.path.isfile('./deskshare/deskshare.webm') and os.path.isfile('./video/webcams.webm')):
        ffmpegCombine('webm', fileName=fileName)
    elif(os.path.isfile('./deskshare/deskshare.mp4') and os.path.isfile('./video/webcams.mp4')):
        ffmpegCombine('mp4', fileName=fileName)
    else:
        print('Video files not found, this meeting might not be supported.')
        exit(1)

    print('Your combined video file is located here:')
    print(f'./downloadedMeetings/{fileIdOrName}/{fileName}.{COMBINED_VIDEO_FORMAT}')

else:
    print("Error parsing aguments. Use '--help' for help.")

