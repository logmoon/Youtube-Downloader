from pytubefix import YouTube
from pytubefix import Playlist
import moviepy.editor as mpe
from sys import argv
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
    print(f"Successfully Downloaded in '{file_path}'")


# Youtube changed a few things making adaptive resolution videos come without audio
# So we have to first download the video, then the audio, and combine them.

# Code adapted from: https://stackoverflow.com/a/61063349
def combine_video_audio(video_path, audio_path, output_path, fps):
    my_clip = mpe.VideoFileClip(video_path)
    audio_background = mpe.AudioFileClip(audio_path)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(output_path, threads=4, audio_fps=44100, codec='libx264', audio=True, fps=fps)

def download_video(yt, video_itag, audio_itag, output_path):
    # First, download the video
    video = yt.streams.get_by_itag(video_itag)
    title = video.title
    fps = video.fps
    print("==Downloading Video...==")
    video.download(output_path=output_path, filename="video.mp4")
    # Then, download the audio
    audio = yt.streams.get_by_itag(audio_itag)
    print("==Downloading Audio...==")
    audio.download(output_path=output_path, filename="audio.mp3")
    # Now we combine
    print("==Combining...==")
    combine_video_audio(output_path+"/video.mp4", output_path+"/audio.mp3", output_path+ "/" +title+".mp4", fps)
    # Clean up
    print("==Cleaning up...==")
    os.remove(output_path+"/video.mp4")
    os.remove(output_path+"/audio.mp3")
    print("==Done!==")

def handle_video_and_audio(yt, out_path):
    # Register callbacks
    yt.register_on_progress_callback(progress_func)
    yt.register_on_complete_callback(complete_func)

    print(f"==Video Information:==\nTitle:{yt.title}\nAuthor:{yt.author}\nViews:{yt.views}")
    while (True):
        choice = input("==Enter:==\n0 To Download Video\n1 To Download Audio\n2 To Cancel\n> ")
        if (int(choice) == 0 or int(choice) == 1 or int(choice) == 2):
            break

    if int(choice) == 0: # Video
        print("==Fetching the video streams...==")
        for entry in yt.streams.filter(mime_type="video/mp4", adaptive=True, only_video=True):
            print(entry)
        video_itag = input("==Enter The itag of the chosen stream:==\n> ")

        print("==Fetching the audio streams...==")
        for entry in yt.streams.filter(mime_type="audio/mp4", only_audio=True):
            print(entry)
        audio_itag = input("==Enter The itag of the chosen stream:==\n> ")

        print("==Starting Download...==")
        download_video(yt, video_itag, audio_itag, out_path)
    elif int(choice) == 1: # Audio
        print("==Fetching the streams...==")
        for entry in yt.streams.filter(mime_type="audio/mp4", only_audio=True):
            print(entry)
        itag = input("==Enter The itag of the chosen stream:==\n> ")
        print("==Starting Download...==")
        audio = yt.streams.get_by_itag(itag)
        audio.download(output_path=out_path, filename=output_path+audio.title+".mp3")
    else:
        return


def process_video_and_audio(link, out_path):
    yt = YouTube(
            link,
            use_oauth=False,
            allow_oauth_cache=True)
    handle_video_and_audio(yt, out_path)


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
            handle_video_and_audio(video, output_path)


def process():
    if 'playlist' in yt_link: # This is a link to the playlist main page, so we directly download it.
        process_playlist(yt_link)
    elif 'list' in yt_link: # Here, this is a video link, but the video is inside of a playlist, so we ask if you want only the video or the entire playlist.
        while (True):
            choice = input("==Enter:==\n0 To Download The Video\n1 To Download The Entire Playlist\n> ")
            if (int(choice) == 0 or int(choice) == 1):
                break
        if int(choice) == 0:
            process_video_and_audio(yt_link, output_path)
        else:
            process_playlist(yt_link)
    else:
        process_video_and_audio(yt_link, output_path)


if __name__ == '__main__':
    process()
