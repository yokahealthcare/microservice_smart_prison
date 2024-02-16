import os

import psutil
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    return "This is testing page. It tell you this is working :)"


@app.route("/cpu")
def hardware_info():
    cpu_info = f"Number of CPU cores: {psutil.cpu_count(logical=False)} (physical)\n"

    return f"\n{cpu_info}\n"


def is_file_playable(file_path):
    command = f"ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 '{file_path}'"
    return os.system(command) == 0


def move_from_incoming_to_temp_folder():
    os.system("mv /app/incoming_frame/*.jpg /app/temp_frame")


def create_video(input_folder="temp_frame", output_file="default.mp4"):
    # execute moving frame from incoming_folder
    move_from_incoming_to_temp_folder()

    os.system(
        f"ffmpeg -framerate 20 -pattern_type glob -i '{input_folder}/*.jpg' -c:v libx264 -pix_fmt yuv420p vod/{output_file} -y")
    print(f"Video created: {output_file}")

    # Check output file playable or not
    """
        It is not likely to happen
        ffmpeg still manage to generate playable video
    """
    if not is_file_playable(f"vod/{output_file}"):
        # Restart the function create video
        create_video(output_file=output_file)

    print("File is OK")
    return True


@app.route("/start")
def start():
    output_file = request.args.get("output_file")

    if create_video(output_file=output_file):
        return "OK"
    else:
        return "FAILED"


if __name__ == '__main__':
    """
        host : 0.0.0.0 
        - this is a must, cannot be changed to 127.0.0.1 
        - or it will cannot be accessed after been forwarded by docker to host IP
    
        port : 80 (up to you)
    """
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True, use_reloader=False)
