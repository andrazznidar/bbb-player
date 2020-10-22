import argparse
from urllib.parse import urlparse
import os
import urllib.request
import json
from distutils.dir_util import copy_tree
import traceback
from flask import Flask


def ffmpegCombine(suffix):
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
    output = ffmpeg.output(video_file, audio_file, './combine-output.mkv',
                           vcodec='copy', acodec='copy', map='-1:v:0', strict='very')

    ffmpeg.run(output)


def downloadFiles(baseURL, basePath):
    filesForDL = ["captions.json", "cursor.xml", "deskshare.xml", "metadata.xml",
                  "panzooms.xml", "presentation_text.json", "shapes.svg", "slides_new.xml", "video/webcams.webm", "video/webcams.mp4", "deskshare/deskshare.webm", "deskshare/deskshare.mp4"]

    for file in filesForDL:
        print('Downloading ' + file)
        downloadURL = baseURL + file
        print(downloadURL)
        savePath = basePath + file
        print(savePath)

        try:
            urllib.request.urlretrieve(downloadURL, savePath)
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
            createFolder(basePath + '/presentation/' + element)
            for i in range(1, noSlides+1):
                downloadURL = baseURL + 'presentation/' + \
                    element + '/slide-' + str(i) + '.png'
                savePath = basePath + '/presentation/' + \
                    element + '/slide-' + str(i) + '.png'

                print(downloadURL)
                print(savePath)
                try:
                    urllib.request.urlretrieve(downloadURL, savePath)
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
group = parser.add_mutually_exclusive_group()
group.add_argument("--download", type=str, nargs=1,
                   help="download the BBB conference linked here")
group.add_argument("--play", type=str, nargs=1,
                   help="play BBB conference saved locally with ID")
group.add_argument("--combine", type=str, nargs=1,
                   help="combine deskshare+audio of a BBB conference saved localy with ID")
args = parser.parse_args()

if(args.download != None and args.play == args.combine == None):
    print("Download")
    inputURL = args.download[0]
    meetingId = urlparse(inputURL).query[10:]
    print(meetingId)
    baseURL = urlparse(inputURL).scheme + '://' + \
        urlparse(inputURL).netloc + '/presentation/' + meetingId + '/'
    print(baseURL)

    folderPath = "./downloadedMeetings/" + meetingId

    if(os.path.isdir(folderPath) == False):

        createFolder(folderPath)
        createFolder(folderPath + '/video')
        createFolder(folderPath + '/deskshare')
        createFolder(folderPath + '/presentation')

        downloadFiles(baseURL, folderPath + '/')
        downloadSlides(baseURL, folderPath)
        copy_tree("./player", "downloadedMeetings/" + meetingId + "/player")

    else:
        print("Folder for this meeting already exists.")

elif(args.play != None and args.download == args.combine == None):
    print("Play")
    fileId = args.play[0]

    os.chdir('./downloadedMeetings/' + fileId)

    print('---------')
    print('In your modern web browser open:')
    print('http://localhost:5000/player/playback.html')
    print('Press CTRL+C when done.')
    print('---------')

    # Based on https://stackoverflow.com/a/42791810
    # Flask is needed for HTTP 206 Partial Content support.

    app = Flask(__name__,
                static_url_path='',
                static_folder='./',
                template_folder='')

    if __name__ == "__main__":
        app.run()

elif(args.combine != None and args.download == args.play == None):
    print("Combine")
    fileId = args.combine[0]

    try:
        os.chdir('./downloadedMeetings/' + fileId)
    except:
        print("Meeting with ID " + fileId +
              " is not downloaded. Download it first using the --download command")
        exit(1)

    if(os.path.isfile('./combine-output.mkv')):
        print('./combine-output.mkv already found. Aborting.')
        exit(1)
    elif(os.path.isfile('./deskshare/deskshare.webm') and os.path.isfile('./video/webcams.webm')):
        ffmpegCombine('webm')
    elif(os.path.isfile('./deskshare/deskshare.mp4') and os.path.isfile('./video/webcams.mp4')):
        ffmpegCombine('mp4')
    else:
        print('Video files not found, this meeting might not be supported.')

    print('Your combined video file is located here:')
    print('./downloadedMeetings/' + fileId + '/combine-output.mkv')
else:
    print("Error parsing aguments. Use '--help' for help.")
