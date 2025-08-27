import os
import random
import subprocess
import tempfile

base_dir = "segment_downloads"
questions_dir = os.path.join(base_dir, "questions")
answers_dir = os.path.join(base_dir, "answers")

# use system random if possible
try:
    system_random = random.SystemRandom()
    question_file = system_random.choice(os.listdir(questions_dir))
    answer_file = system_random.choice(os.listdir(answers_dir))
except NotImplementedError:
    question_file = random.choice(os.listdir(questions_dir))
    answer_file = random.choice(os.listdir(answers_dir))

q_path = os.path.join(questions_dir, question_file)
a_path = os.path.join(answers_dir, answer_file)

# audio normalize clips
tmp_q = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
tmp_a = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

# normalize question clip
subprocess.run([
    "ffmpeg", "-y", "-i", q_path,
    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
           "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
    "-c:v", "libx264", "-crf", "23", "-preset", "fast",
    "-c:a", "aac", "-b:a", "128k",
    tmp_q
])

# normalize answer clip
subprocess.run([
    "ffmpeg", "-y", "-i", a_path,
    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
           "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
    "-c:v", "libx264", "-crf", "23", "-preset", "fast",
    "-c:a", "aac", "-b:a", "128k",
    tmp_a
])

# merge clips together
cmd = [
    "ffmpeg", "-y",
    "-i", tmp_q, "-i", tmp_a,
    "-filter_complex",
    "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]",
    "-map", "[outv]", "-map", "[outa]",
    "-c:v", "libx264", "-crf", "23", "-preset", "fast",
    "-c:a", "aac", "-b:a", "128k",
    "random_qa.mp4"
]
subprocess.run(cmd)

# cleanup
os.remove(tmp_q)
os.remove(tmp_a)
