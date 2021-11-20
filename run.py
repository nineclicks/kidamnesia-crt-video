import cv2
import numpy as np
from random import choice
from pathlib import Path

OUTPUT_FILENAME='CRT_Room.mov'
FILE_LIST_FILENAME='items.txt'

# File extentions that will be grabbed from a folder in the items list file
VIDEO_TYPES = ['mp4', 'mov', 'avi', 'm4v', 'wmv', 'mpg']

# Range of frames for a video cell before a new video starts in the cell
CELL_LENGTH_FRAMES_RANGE = (30 * 10, 30 * 25) # 30fps * 10-25 seconds

# Length in frames of the entire crt room video
VIDEO_LENGTH_FRAMES = 30 * 60 * 2 # 30fps * 60 seconds * 2 minutes

# CRT room might not come out right if you change anything below
FRAME_WIDTH = 3840 # crt room video width
FRAME_HEIGHT = 2160 # crt room video height
N_X = 9 # number of tiled video cells wide
N_Y = 8 # number of tiled video cells tall
CELL_WIDTH = FRAME_WIDTH // N_X
CELL_HEIGHT = FRAME_HEIGHT // N_Y

def get_file_list(list_filename):
    with open(list_filename) as fp:
        files = []
        for path in fp.readlines():
            path = Path(path.strip())

            if path.is_file() and path.exists():
                files.append(str(path))

            elif path.is_dir():
                for f in path.iterdir():
                    if f.is_file() and f.suffix.lower().lstrip('.') in VIDEO_TYPES and f.exists():
                        files.append(str(f))

    return files

def resize(frame: np, new_width, new_height):
    height, width, channels = frame.shape
    new_ratio = new_width/new_height
    old_ratio = width/height

    if new_ratio < old_ratio:
        # resize by height
        scale = new_height / height
        temp_new_width = int(width * scale)
        temp_new_height = new_height
    else:
        # resize by width
        scale = new_width / width
        temp_new_width = new_width
        temp_new_height = int(height * scale)

    # resize
    res = cv2.resize(frame, dsize=(temp_new_width, temp_new_height), interpolation=cv2.INTER_CUBIC)

    # crop
    res = res[(temp_new_height - new_height)//2:(temp_new_height - new_height)//2 + new_height,(temp_new_width - new_width)//2:(temp_new_width - new_width)//2 + new_width]
    return res

def load_file(files, random_pos=False):
    for _ in range(10):
        try:
            fn = choice(files)
            cap = cv2.VideoCapture(fn)

            if random_pos:
                total_frames = int(cap.get(7))
                frame_no = choice(range(total_frames))
                cap.set(cv2.CAP_PROP_POS_FRAMES,frame_no)

            return cap

        except Exception:
            files.remove(fn)

def make_video(output_filename, file_list):
    video=cv2.VideoWriter(output_filename,-1,30,(FRAME_WIDTH,FRAME_HEIGHT))
    sources = []

    for _ in range(N_X * N_Y):
        sources.append([load_file(file_list, random_pos=True), choice(range(*CELL_LENGTH_FRAMES_RANGE))])

    for i in range(VIDEO_LENGTH_FRAMES):

        if int(i/VIDEO_LENGTH_FRAMES*100) != int((i-1)/VIDEO_LENGTH_FRAMES*100):
            print(str(int(i/VIDEO_LENGTH_FRAMES*100))+ '%')

        new_frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH,3), np.uint8)
        for i, x in enumerate(sources):
            s, f = x
            x = (i % N_X) * CELL_WIDTH
            y = (i // N_X) * CELL_HEIGHT
            ret, frame = s.read()

            while not ret or f <= 0:
                s = load_file(file_list, random_pos=True)
                f = choice(range(*CELL_LENGTH_FRAMES_RANGE))
                sources[i] = [s, f]
                ret, frame = s.read()

            new_cell = resize(frame, CELL_WIDTH, CELL_HEIGHT)
            new_frame[y:y+CELL_HEIGHT, x:x+CELL_WIDTH] = new_cell
            sources[i][1] -= 1

        video.write(new_frame)

    video.release()

if __name__ == '__main__':
    files = get_file_list(FILE_LIST_FILENAME)
    make_video(OUTPUT_FILENAME, files)