"""
Tests if the YAML files were made correctly.
"""
import re
from warnings import warn
from pathlib import Path

# https://pyyaml.org/wiki/PyYAMLDocumentation
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


YT_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def test_segment(segment, filename, segment_type):
    print(f"Testing {segment_type}: {segment}")
    t_start = segment["start"]
    t_end = segment["end"]

    # check if timestamps are not added (or None)
    if t_start is None or t_end is None:
        raise Exception(f"{filename}: {segment_type} {segment['id']} has empty timestamps! {segment}")

    # check if duration is negative
    duration = t_end - t_start
    if duration < 0:
        raise Exception(f"{filename}: {segment_type} {segment['id']}'s duration is negative!"
                        f"\n{t_end} - {t_start} = {t_end - t_start}")
    
    # warn if duration is longer than half a minute (30 seconds)
    if duration > 30:
        warn(f"{filename}: {segment_type} {segment['id']} is over {duration} seconds long.")


def test_file(v_data, filename):
    """
    Process data in the YAML to download the video segments.

    Each YAML file should contain:
    - Unix timestamp of when it was last updated
    - YouTube Video ID (REQUIRED!)
    - A question segment in seconds and miliseconds
    - Multiple answer segments in seconds and miliseconds
    """

    # check if `timestamp` is in v_data
    if not "timestamp" in v_data:
        raise Exception(f"{filename}: Modified timestamp was not found in YAML file!")


    # check if the timestamp is unmodifed (0)
    if v_data["timestamp"] == 0:
        raise Exception(f"{filename}: Modified timestamp is 0! Please add the current UNIX timestamp to the YAML file.")


    # check video id is valid
    video_id = str(v_data["video_id"])
    if not YT_VIDEO_ID_PATTERN.match(video_id):
        raise Exception(f"{filename}: YT Video ID is not valid for {video_id}")


    # check if `questions` is in v_data
    if not "questions" in v_data:
        warn(f"{filename}: Questions was not found in YAML file")
    else:
        # check timestamps in questions
        for question in v_data["questions"]:
            test_segment(question, filename, "Question")


    # check if `answers` is in v_data
    if not "answers" in v_data:
        raise Exception(f"{filename}: Answers was not found in YAML file!")


    # check timestamps in answers
    for answer in v_data["answers"]:
        test_segment(answer, filename, "Answer")


    return True


snips_folder = Path("snips")
yaml_files = snips_folder.rglob("*.yaml")
for yaml_file in yaml_files:
    print(f"Testing: {yaml_file}")
    with open(yaml_file, "r", encoding="utf-8") as f:
        # no need to try except for YAML errors;
        # that's part of the validity test
        data = yaml.load(f, Loader=Loader)
        test_file(data, yaml_file.name)
