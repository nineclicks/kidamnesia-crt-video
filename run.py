import cv2
import numpy as np
from random import choice

FRAME_WIDTH = 3840
FRAME_HEIGHT = 2160
N_X = 9
N_Y = 8
CELL_WIDTH = FRAME_WIDTH // N_X
CELL_HEIGHT = FRAME_HEIGHT // N_Y

print(CELL_WIDTH, CELL_HEIGHT)

with open('items.txt') as fp:
    files = [x.strip() for x in fp.readlines()]

video=cv2.VideoWriter('video.mp4',-1,30,(FRAME_WIDTH,FRAME_HEIGHT))

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

    res = cv2.resize(frame, dsize=(temp_new_width, temp_new_height), interpolation=cv2.INTER_CUBIC)

    res = res[(temp_new_height - new_height)//2:(temp_new_height - new_height)//2 + new_height,(temp_new_width - new_width)//2:(temp_new_width - new_width)//2 + new_width]
    return res

def load_file(files, random_pos=False):
    cap = cv2.VideoCapture(choice(files))

    if random_pos:
        total_frames = int(cap.get(7))
        frame_no = choice(range(total_frames))
        cap.set(cv2.CAP_PROP_POS_FRAMES,frame_no)

    return cap

sources = []

for _ in range(N_X * N_Y):
    sources.append(load_file(files, random_pos=True))

for i in range(60):
    print(i)
    new_frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH,3), np.uint8)
    for i, s in enumerate(sources):
        x = (i % N_X) * CELL_WIDTH
        y = (i // N_X) * CELL_HEIGHT
        frame: np
        ret, frame = s.read()
        if ret:
            new_cell = resize(frame, CELL_WIDTH, CELL_HEIGHT)
            new_frame[y:y+CELL_HEIGHT, x:x+CELL_WIDTH] = new_cell
        else:
            sources[i] = load_file(files)

    video.write(new_frame)

video.release()