import argparse
from urllib.parse import urlparse
import os
import urllib.request
import json
from distutils.dir_util import copy_tree
import traceback
import re
from datetime import timedelta
import logging


LOGGING_LEVEL = logging.INFO
# LOGGING_LEVEL = logging.DEBUG
DOWNLOADED_FULLY_FILENAME = "rec_fully_downloaded.txt"
DOWNLOADED_MEETINGS_FOLDER = "downloadedMeetings"
DEFAULT_COMBINED_VIDEO_NAME = "combine-output"
COMBINED_VIDEO_FORMAT = "mkv"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(format="[%(asctime)s -%(levelname)8s]: %(message)s",
                    datefmt="%H:%M:%S",
                    level=LOGGING_LEVEL)
logger = logging.getLogger('bbb-player')

try:
    from pySmartDL import SmartDL
    smartDlEnabled = True
except ImportError:
    logger.warning("pySmartDL not imported, using urllib instead")
    smartDlEnabled = False


def ffmpegCombine(suffix, fileName=DEFAULT_COMBINED_VIDEO_NAME):
    try:
        import ffmpeg
    except:
        logger.critical(
            "ffmpeg-python not imported. Try running:\npip3 install ffmpeg-python")
        exit(1)

    logger.debug("ffmpeg-python imported")

    video_file = ffmpeg.input('./deskshare/deskshare.' + suffix)
    audio_file = ffmpeg.input('./video/webcams.' + suffix)

    # Based on https://www.reddit.com/r/learnpython/comments/ey41dp/merging_video_and_audio_using_ffmpegpython/fgf1oyq/
    output = ffmpeg.output(video_file, audio_file, f'{fileName}.{COMBINED_VIDEO_FORMAT}',
                           vcodec='copy', acodec='copy', map='-1:v:0', strict='very')

    ffmpeg.run(output)


def downloadFiles(baseURL, basePath):
    filesForDL = ["captions.json", "cursor.xml", "deskshare.xml", "presentation/deskshare.png", "metadata.xml", "panzooms.xml", "presentation_text.json",
                  "shapes.svg", "slides_new.xml", "video/webcams.webm", "video/webcams.mp4", "deskshare/deskshare.webm", "deskshare/deskshare.mp4"]

    for i, file in enumerate(filesForDL):
        logger.info(f'[{i+1}/{len(filesForDL)}] Downloading {file}')
        downloadURL = baseURL + file
        logger.debug(downloadURL)
        savePath = os.path.join(basePath, file)
        logger.debug(savePath)

        try:
            if smartDlEnabled:
                smartDl = SmartDL(downloadURL, savePath)
                smartDl.start()
            else:
                urllib.request.urlretrieve(
                    downloadURL, savePath, reporthook=bar.on_urlretrieve if bar else None)
        except urllib.error.HTTPError as e:
            # traceback.print_exc()
            if e.code == 404:
                logger.warning(f"Did not download {file} because of 404 error")
        except Exception:
            logger.exception("")


def downloadSlides(baseURL, basePath):
    # Part of this is based on https://www.programiz.com/python-programming/json
    with open(basePath + '/presentation_text.json', encoding="utf8") as f:
        data = json.load(f)
        logger.info(f"Downloading {len(data)} presentations")
        for element in data:
            logger.debug(element)
            noSlides = len(data[element])
            logger.debug(noSlides)
            createFolder(os.path.join(basePath, 'presentation', element))
            logger.info(f"Downloading {noSlides} slides for the presentation")
            for i in range(1, noSlides+1):
                logger.debug(f"Downloading slide {i}/{noSlides}")
                downloadURL = baseURL + 'presentation/' + \
                    element + '/slide-' + str(i) + '.png'
                savePath = os.path.join(basePath, 'presentation',
                                        element,  'slide-{}.png'.format(i))

                logger.debug(downloadURL)
                logger.debug(savePath)

                try:
                    if smartDlEnabled:
                        smartDl = SmartDL(
                            downloadURL, savePath, progress_bar=False)
                        smartDl.start()
                    else:
                        urllib.request.urlretrieve(
                            downloadURL, savePath, reporthook=bar.on_urlretrieve if bar else None)
                except urllib.error.HTTPError as e:
                    # traceback.print_exc()
                    if e.code == 404:
                        logger.warning(
                            f"Did not download {element}/slide-{str(i)}.png")
                except Exception:
                    logger.exception("")

            createFolder(os.path.join(
                basePath, 'presentation', element, 'thumbnails'))

            logger.info(
                f"Downloading {noSlides} thumbnails for the presentation")
            for i in range(1, noSlides+1):
                downloadURL = baseURL + 'presentation/' + \
                    element + '/thumbnails/thumb-' + str(i) + '.png'
                savePath = os.path.join(basePath, 'presentation',
                                        element, 'thumbnails', 'thumb-{}.png'.format(i))

                logger.debug(f"Download url:\t{downloadURL}")
                logger.debug(f"Download path:\t{savePath}")

                try:
                    if smartDlEnabled:
                        smartDl = SmartDL(
                            downloadURL, savePath, progress_bar=False)
                        smartDl.start()
                    else:
                        urllib.request.urlretrieve(
                            downloadURL, savePath, reporthook=bar.on_urlretrieve if bar else None)
                except urllib.error.HTTPError as e:
                    # traceback.print_exc()
                    if e.code == 404:
                        logger.warning(
                            f"Did not download {element}/slide-{str(i)}.png")
                except Exception:
                    logger.exception("")


def createFolder(path):
    # Create meeting folders, based on https://stackabuse.com/creating-and-deleting-directories-with-python/
    try:
        os.makedirs(path)
    except OSError:
        logger.debug("Creation of the directory %s failed" % path)
    else:
        logger.debug("Successfully created the directory %s " % path)


def create_app():
    logger.info("Server")

    try:
        from flask import Flask, render_template, request, redirect, url_for
    except:
        logger.error("Flask not imported. Try running:\npip3 install Flask")
        exit(1)

    logger.debug("Flask imported.")

    downloadedMeetingsFolderPath = os.path.join(
        SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER)
    if not os.path.isdir(downloadedMeetingsFolderPath):
        logger.error(f"Meetings folder is not present.\
Download at least one meeting first using the --download argument")
        exit(1)

    logger.debug(f"Current path: {os.getcwd()}")

    # check if an older bbb version recording exists and copy 2.3 player to it:
    meetingFolders = sorted([folder for folder in os.listdir(
        downloadedMeetingsFolderPath) if os.path.isdir(os.path.join(downloadedMeetingsFolderPath, folder))])
    for m in meetingFolders:
        # get links to correct html files in folders of downloaded meetings
        if (os.path.isfile(os.path.join(downloadedMeetingsFolderPath, m, 'index.html'))
                and os.path.isfile(os.path.join(downloadedMeetingsFolderPath, m, 'asset-manifest.json'))):
            # bbb 2.3 has index.html
            pass
        else:
            # bbb 2.0 - copy bbb 2.3 player over it
            logger.info(
                f"An older 2.0 bbb player detected in meeting {m}. Copying 2.3 player over it")
            player23Folder = os.path.join(SCRIPT_DIR, "player23")
            meetingFolder = os.path.join(downloadedMeetingsFolderPath, m)
            copy_tree(player23Folder, meetingFolder)

    # Based on https://stackoverflow.com/a/42791810
    # Flask is needed for HTTP 206 Partial Content support.
    app = Flask(__name__,
                static_url_path='',
                static_folder=SCRIPT_DIR,
                template_folder='')

    @app.route('/', methods=["POST"])
    def api_dl_meeting():
        form = request.form
        if form["meeting-name"] and form["meeting-url"]:
            name = form["meeting-name"].strip().replace(" ", "_")
            url = form["meeting-url"].strip()

            downloadScript(url, name)

            message = f"Download of {name} with URL {url} completed or failed. ¯\_(ツ)_/¯, check the list meetings and try to play it."

            # TODO: download meeting and dinamically show progress
            # https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page/40964086

        else:
            message = f"Error occured when trying to add a meeting to download queue."

        #message += " (NOT IMPLEMENTED)"
        return hello(message=message)

    @app.route("/", methods=["GET"])
    def hello(message='You should download new meetings from the command line. Run "python3 bbb-player.py --help" for help. You can try this form if you are feeling adventurous.'):
        # list all folders in DOWNLOADED_MEETINGS_FOLDER
        meetingFolders = sorted([folder for folder in os.listdir(
            downloadedMeetingsFolderPath) if os.path.isdir(os.path.join(downloadedMeetingsFolderPath, folder))])
        if len(meetingFolders) == 0:
            logger.warning(
                f"Meeting folder /{DOWNLOADED_MEETINGS_FOLDER} is empty. Download at least one meeting first using the --download argument")
        meetingLinks = []
        for m in meetingFolders:
            # get links to correct html files in folders of downloaded meetings
            if (os.path.isfile(os.path.join(downloadedMeetingsFolderPath, m, 'index.html')) and os.path.isfile(os.path.join(downloadedMeetingsFolderPath, m, 'asset-manifest.json'))):
                # bbb 2.3 has index.html
                meetingLinks.append(
                    [f"/{DOWNLOADED_MEETINGS_FOLDER}/{m}/index.html", m])
            else:
                # bbb 2.0 has player/playback.html
                meetingLinks.append(
                    [f"/{DOWNLOADED_MEETINGS_FOLDER}/{m}/player/playback.html", m])
        # render available meeting links on page
        return render_template("index.html",
                               meetingLinks=meetingLinks, message=message)

    # Based on https://stackoverflow.com/a/37331139
    # This is needed for playback of multiple meetings in short succession.
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TESTING'] = True

    return app


def downloadScript(inputURL, meetingNameWanted):
    # get meeting id from url https://regex101.com/r/UjqGeo/3
    matchesURL = re.search(r"/?(\d+\.\d+)/.*?([0-9a-f]{40}-\d{13})/?",
                           inputURL,
                           re.IGNORECASE)
    if matchesURL and len(matchesURL.groups()) == 2:
        bbbVersion = matchesURL.group(1)
        meetingId = matchesURL.group(2)
        logger.info(f"Detected bbb version:\t{bbbVersion}")
        logger.info(f"Detected meeting id:\t{meetingId}")
    else:
        logger.error("Meeting ID could not be found in the url.")
        exit(1)

    baseURL = "{}://{}/presentation/{}/".format(urlparse(inputURL).scheme,
                                                urlparse(inputURL).netloc,
                                                meetingId)
    logger.debug("Base url: {}".format(baseURL))

    if meetingNameWanted:
        folderPath = os.path.join(
            SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, meetingNameWanted)
    else:
        folderPath = os.path.join(
            SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, meetingId)
    logger.debug("Folder path: {}".format(folderPath))

    if os.path.isfile(os.path.join(folderPath, DOWNLOADED_FULLY_FILENAME)):
        logger.info("Meeting is already downloaded.")
    else:
        logger.info(
            "Folder already created but not everything was downloaded. Retrying.")
        # todo: maybe delete contents of the folder

        foldersToCreate = [os.path.join(folderPath, x) for x in [
            "", "video", "deskshare", "presentation"]]
        # logger.info(foldersToCreate)
        for i in foldersToCreate:
            createFolder(i)

        try:
            from progressist import ProgressBar
            bar = ProgressBar(throttle=timedelta(seconds=1),
                              template="Download |{animation}|{tta}| {done:B}/{total:B} at {speed:B}/s")
        except:
            logger.warning("progressist not imported. Progress bar will not be shown. Try running: \
                                pip3 install progressist")
            bar = None

        downloadFiles(baseURL, folderPath)
        downloadSlides(baseURL, folderPath)

        # Copy the 2.3 player
        copy_tree(os.path.join(SCRIPT_DIR, "player23"), folderPath)

        with open(os.path.join(folderPath, DOWNLOADED_FULLY_FILENAME), 'w') as fp:
            # write a downloaded_fully file to mark a successful download
            # todo: check if files were really dl-ed (make a json of files to download and
            #          check them one by one on success)
            pass


if __name__ == "__main__":

    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    # group = parser.add_mutually_exclusive_group()
    group = parser
    group.add_argument("-d", "--download", type=str, nargs=1,
                       help="download the BBB conference linked here")
    group.add_argument("-n", "--name", type=str, nargs=1,
                       help="define name of the conference (e.g. meeting1)")
    group.add_argument("-s", "--server", action="store_true",
                       help="launch a server with all available downloaded meetings listed on one page")
    group.add_argument("-c", "--combine", type=str, nargs=1,
                       help="combine deskshare+audio of a BBB conference saved localy. Full id string \
                    (e.g. 70i9tyx7zbajoptzbav3ky1tuqxj3hgerup42jda-2177698461148) or \
                    the name you provided when downloading (e.g. meeting1)")
    group.add_argument("-v", "--verbose", action="store_true",
                       help="verbose logging")

    args = parser.parse_args()

    if args.verbose:
        LOGGING_LEVEL = logging.DEBUG
        logger.setLevel(LOGGING_LEVEL)

    if(args.download != None and args.server == False and args.combine == None):
        logger.info("Download")
        inputURL = args.download[0]

        meetingNameWanted = None
        if args.name:
            meetingNameWanted = args.name[0].strip().replace(" ", "_")
            logger.info(f"Naming the meeting as: {meetingNameWanted}")

        downloadScript(inputURL, meetingNameWanted)

    elif(args.server == True and args.name == args.download == args.combine == None):
        app = create_app()

        logger.info('---------')
        logger.info('In your modern web browser open:')
        logger.info('http://localhost:5000')
        logger.info('Press CTRL+C when done.')
        logger.info('---------')

        app.run(host='0.0.0.0', port=5000)

    elif(args.combine != None and args.name == args.download == None and args.server == False):
        logger.info("Combine")
        fileIdOrName = args.combine[0]

        try:
            os.chdir(os.path.join(
                SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, fileIdOrName))
        except:
            logger.error(f"Meeting with ID {fileIdOrName} is not downloaded. \
                        Download it first using the --download command")
            exit(1)

        matchesName = re.match(
            r"([0-9a-f]{40}-\d{13})", fileIdOrName, re.IGNORECASE)
        if matchesName:
            # if file id/name looks like bbb 54 char string use a simple predefined name
            meetingId = matchesName.group(0)
            logger.info(
                f"Extracted meeting id: {meetingId} from provided name")
            logger.info(
                f"Setting output file name to {DEFAULT_COMBINED_VIDEO_NAME}")
            fileName = DEFAULT_COMBINED_VIDEO_NAME
        else:
            fileName = fileIdOrName
            # todo: add name parsing from -n

        if(os.path.isfile(f'./{fileName}.{COMBINED_VIDEO_FORMAT}')):
            logger.warning(
                f'./{DEFAULT_COMBINED_VIDEO_NAME}.{COMBINED_VIDEO_FORMAT} already found. Aborting.')
            exit(1)
        elif(os.path.isfile('./deskshare/deskshare.webm') and os.path.isfile('./video/webcams.webm')):
            ffmpegCombine('webm', fileName=fileName)
        elif(os.path.isfile('./deskshare/deskshare.mp4') and os.path.isfile('./video/webcams.mp4')):
            ffmpegCombine('mp4', fileName=fileName)
        else:
            logger.error(
                'Video files not found, this meeting might not be supported.')
            exit(1)

        logger.info('Your combined video file is located here:')
        logger.info(
            f'./{DOWNLOADED_MEETINGS_FOLDER}/{fileIdOrName}/{fileName}.{COMBINED_VIDEO_FORMAT}')

    else:
        logger.error("Error parsing arguments. Use '--help' for help.")
