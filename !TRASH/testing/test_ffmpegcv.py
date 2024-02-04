import os


def create_video(input_folder, output_file):
    os.system(f"ffmpeg -framerate 20 -pattern_type glob -i '{input_folder}/*.jpg' -c:v libx264 -pix_fmt yuv420p {output_file} -y")
    print(f"Video created: {output_file}")


if __name__ == "__main__":
    input_folder = "fight_frame/"
    output_file = "output_video.mp4"

    create_video("fight_frame/", "output.mp4")
