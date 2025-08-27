# IAYY (I Asked You Yesterday)
*YIAY question and answers segment downloader*

## How to use
1. Download and install [Python](https://www.python.org/), [FFmpeg](https://ffmpeg.org/) and [yt-dlp](https://github.com/yt-dlp/yt-dlp)
    1. Make sure they're both on the PATH so the videos can be downloaded. For yt-dlp, [a third party manager is recommended](https://github.com/yt-dlp/yt-dlp/wiki/Installation#third-party-package-managers).
2. Clone this repository (or download the .zip file of the code via the green button above)
3. Install pip requirements (`pip install -r requirements.txt`)
4. Run `python3 download_videos.py`
    1. A new folder called `segment_downloads` will be created
5. Use any video randomizer to playback the videos in `segment_downloads`

# Contribution
You can help contribute to this repo by forking it. Please make sure to create a new branch before committing your changes.

Adding support for more YIAY snippets means creating a new YAML file to support a new video. `template.yaml` on the root of this repo will help you with this.

YouTube has a feature to show the seconds and milliseconds the video is on. Right click the video frame and turn on "Stats for nerds". Look for the "Mystery Text" row; there should be a variable called `t`. Use that number as well as the `<` and `>` keys to find the best frame to start and end the snippet on.

> [!TIP]
>  To avoid seeing jarring frame cuts when the segment is downloaded, get the second to last frame you want. The `t` variable might display the wrong number, so be sure to check if the frame you're on is the right time you need.

Once you have finished marking all of the clips in the video, test if the YAML works on your end by running the download script. If these new clips look normal, great! Otherwise, keep tweaking the numbers until they look nice.

Sometimes a blank frame may appear instead of a normal frame; I have no idea how to fix it, but if you have a solution to this please let me know!

Once ready, send a PR to this repo.

*This project has been licensed with the MIT License.*
