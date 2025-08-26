import subprocess
from pathlib import Path

# https://pyyaml.org/wiki/PyYAMLDocumentation
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


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


def download_yt_segment_MULTI(video_id, section_timestamps, name, type):
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



def download_yt_segment_SINGLE(video_id, section_timestamp, name, type):
    command = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--force-keyframes-at-cuts",  # https://github.com/yt-dlp/yt-dlp/issues/2220#issuecomment-2579162159
        "-t", "mp4", "-o", f"./segment_downloads/{type}s/{name}_{type}.%(ext)s",
        "--download-sections", section_timestamp,
    ]
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

    # download question
    if "question" in v_data:
        q = v_data["question"]
        t_start = q["start"]
        t_end = q["end"]
        download_yt_segment_SINGLE(
            video_id=video_id,
            section_timestamp=f"*{t_start}-{t_end}",
            name=filename.removesuffix(".yaml"),
            type="question")
    
    # download answers
    if "answers" in v_data:
        section_timestamps = []
        for answer in v_data["answers"]:
            t_start = answer["start"]
            t_end = answer["end"]
            section_timestamps.append(f"*{t_start}-{t_end}")
        
        download_yt_segment_MULTI(
            video_id=video_id,
            section_timestamps=section_timestamps,
            name=filename.removesuffix(".yaml"),
            type="answer")


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

