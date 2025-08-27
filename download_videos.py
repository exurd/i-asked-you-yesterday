import os
import subprocess
from pathlib import Path

# https://pyyaml.org/wiki/PyYAMLDocumentation
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


# create video id archive
vid_archive = []
os.makedirs("./segment_downloads", exist_ok=True)
vid_archive_path = "./segment_downloads/vid_archive.txt"
if not os.path.exists(vid_archive_path):
    with open(vid_archive_path, "w") as f:
        pass

with open(vid_archive_path, "r") as file:
    vid_archive = [line.strip() for line in file]


def add_to_vid_archive(video_id):
    """
    Adds a downloaded video to the archive so it won't be checked again on later
    runs of this script.
    """
    global vid_archive
    try:
        vid_archive.append(video_id)
        with open(vid_archive_path, "a") as f:
            f.write(video_id)
            f.write("\n")
            f.close()
        return True
    except:
        print(f"Error saving video id archive to disk! {e}")
    return False


# getting the specific segment timestamps (seconds and milliseconds) can be
# easily found by looking for the mystery text `t` value in the "stats for
# nerds" feature YT has.
# this would've been painful without that so thank GOD that's there
# also thank the heavens for --download-sections!!!


def run_com(command):
    """
    Run command with checks.
    
    Return True if command runs with no errors, otherwise return False.
    """
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"An error has occurred! {e}")
    return False


def download_yt_segment(video_id, section_timestamps, name, type):
    command = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--force-keyframes-at-cuts",  # https://github.com/yt-dlp/yt-dlp/issues/2220#issuecomment-2579162159
        "-t", "mp4", "-o", f"./segment_downloads/{type}s/{name}_{type}_%(autonumber)03d.%(ext)s"
    ]
    # add section timestamps
    for section in section_timestamps:
        command.append("--download-sections")
        command.append(section)
    return run_com(command)


def process(v_data, filename):
    """
    Process data in the YAML to download the video segments.

    Each YAML file should contain:
    - Unix timestamp of when it was last updated
    - YouTube Video ID (REQUIRED!)
    - A question segment in seconds and miliseconds
    - Multiple answer segments in seconds and miliseconds
    """

    video_id = v_data["video_id"]

    # check if in video id archive
    if video_id in vid_archive:
        print("Video has already been downloaded; skipping!")
        return None

    # download questions
    if "questions" in v_data:
        section_timestamps = []
        for question in v_data["questions"]:
            t_start = question["start"]
            t_end = question["end"]
            section_timestamps.append(f"*{t_start}-{t_end}")
        
        download_yt_segment(
            video_id=video_id,
            section_timestamps=section_timestamps,
            name=filename.removesuffix(".yaml"),
            type="question")
    
    # download answers
    if "answers" in v_data:
        section_timestamps = []
        for answer in v_data["answers"]:
            t_start = answer["start"]
            t_end = answer["end"]
            section_timestamps.append(f"*{t_start}-{t_end}")
        
        download_yt_segment(
            video_id=video_id,
            section_timestamps=section_timestamps,
            name=filename.removesuffix(".yaml"),
            type="answer")
    
    # add to video id archive
    add_to_vid_archive(video_id)

    return True


snips_folder = Path("snips")
yaml_files = snips_folder.rglob("*.yaml")
for yaml_file in yaml_files:
    print(f"Next up: {yaml_file}")
    with open(yaml_file, "r", encoding="utf-8") as f:
        try:
            data = yaml.load(f, Loader=Loader)
            process(data, yaml_file.name)
        except yaml.YAMLError as e:
            print(f"Error parsing {yaml_file}: {e}")

