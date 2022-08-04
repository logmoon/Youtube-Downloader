from pytube import YouTube
from pytube import Playlist
from sys import argv
from sys import platform
import sys
import os

yt_link = argv[1]
output_path = argv[2]

# This progress bar function was taken from https://stackoverflow.com/questions/56197879/how-to-use-progress-bar-in-pytube
def progress_func(chunk, file_handle, bytes_remaining):
    filesize=chunk.filesize
    current = ((filesize - bytes_remaining)/filesize)
    percent = ('{0:.1f}').format(current*100)
    progress = int(50*current)
    status = '█' * progress + '-' * (50 - progress)
    sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
    sys.stdout.flush()

def complete_func(stream, file_path):
    print(f"File Successfully Downloaded in '{file_path}'")

def download_video(yt, out_path):
    yt.register_on_progress_callback(progress_func)
    yt.register_on_complete_callback(complete_func)

    print(f"==Video Information:==\nTitle:{yt.title}\nAuthor:{yt.author}\nViews:{yt.views}")

    while (True):
        choice = input("==Enter:==\n0 To Download Video\n1 To Download Audio\n> ")
        if (int(choice) == 0 or int(choice) == 1):
            break

    print("==Fetching the streams...==")

    if int(choice) == 0:
        for entry in yt.streams.filter(progressive=True):
            print(entry)
        itag = input("==Enter The itag of the chosen stream:==\n> ")
        print("==Starting Download...==")
        yt.streams.get_by_itag(itag).download(output_path=out_path)
    else:
        for entry in yt.streams.filter(only_audio=True):
            print(entry)
        itag = input("==Enter The itag of the chosen stream:==\n> ")
        print("==Starting Download...==")
        yt.streams.get_by_itag(itag).download(output_path=out_path)


def process_video(link, out_path):
    yt = YouTube(
            link,
            use_oauth=False,
            allow_oauth_cache=True)
    download_video(yt, out_path)


def process_playlist(link):
    p = Playlist(link)

    if (len(p.video_urls) == 0):
        print("==Couldn't find playlist, it could be private, check the provided URL==")
        return

    print(f"==Playlist Information:==\nTitle:{p.title}\nOwner:{p.owner}\nDescription:{p.description}")

    while (True):
        choice = input("==Enter:==\n0 To Download All in video format in highest resolution\n1 To Download All in audio format in highest resolution\n2 To Choose for each video\n> ")
        if (int(choice) == 0 or int(choice) == 1 or int(choice) == 2):
            break

    if int(choice) == 0:
        for video in p.videos:
            video.register_on_progress_callback(progress_func)
            video.register_on_complete_callback(complete_func)
            print(f"==Video Information:==\nTitle:{video.title}\nAuthor:{video.author}\nViews:{video.views}")
            print("==Starting Download...==")
            video.streams.get_highest_resolution().download(output_path=output_path)
    elif int(choice) == 1:
        for video in p.videos:
            video.register_on_progress_callback(progress_func)
            video.register_on_complete_callback(complete_func)
            print(f"==Video Information:==\nTitle:{video.title}\nAuthor:{video.author}\nViews:{video.views}")
            print("==Starting Download...==")
            video.streams.get_audio_only().download(output_path=output_path)
    else:
        for video in p.videos:
            download_video(video, output_path)


def process():
    if 'playlist' in yt_link:
        process_playlist(yt_link)
    elif 'list' in yt_link:
        while (True):
            choice = input("==Enter:==\n0 To Download The Video\n1 To Download The Entire Playlist\n> ")
            if (int(choice) == 0 or int(choice) == 1):
                break
        if int(choice) == 0:
            process_video(yt_link, output_path)
        else:
            process_playlist(yt_link)
    else:
        process_video(yt_link, output_path)


if __name__ == '__main__':
    process()
