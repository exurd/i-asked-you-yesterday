import os
import random
import subprocess

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

# merge files together with audio normalization
cmd = [
    "ffmpeg",
    "-fflags", "+genpts",
    "-i", q_path,
    "-i", a_path,
    "-filter_complex",
    "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
    "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
    "[0:a][1:a]concat=n=2:v=0:a=1[aout];"
    "[v0][v1]concat=n=2:v=1:a=0[vout];"
    "[aout]loudnorm=I=-16:TP=-1.5:LRA=11[audio]",
    "-map", "[vout]",
    "-map", "[audio]",
    "-c:v", "libx264", "-crf", "23", "-preset", "fast",
    "-c:a", "aac", "-b:a", "128k",
    "random_qa.mp4"
]
subprocess.run(cmd)
