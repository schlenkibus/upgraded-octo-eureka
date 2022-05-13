from curses.textpad import Textbox
import random
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import glob
import os
import sys
import bordercrop

class State:
    def __init__(self):
        self.ogImage = None
        self.image = None
        self.TKimage = None
        self.imageLabel = None

class Cfg:
    def __init__(self):
        self.precrop = 0
        self.THRESHOLD: int = 5
        self.MINIMUM_THRESHOLD_HITTING: int = 100
        self.MINIMUM_ROWS: int = 100

def selectFileToLoad():
    global state
    filename = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Select a File")
    state.ogImage = Image.open(filename)
    updatePreview(state.ogImage, state)

def updatePreview(image, state):
    state.image = image
    state.image = state.image.resize((1200, 800), Image.NONE)
    state.TKimage = ImageTk.PhotoImage(state.image)

    if state.imageLabel is not None:
        state.imageLabel.destroy()

    state.imageLabel = Label(state.root, image=state.TKimage)
    state.imageLabel.pack()

def cropBlackbarsFromImage(segment, precrop, blackThreshold=1, rowThreshold=0.99, minRowsForBorder=3):
    preprocessed = segment.crop((0, precrop, segment.size[0], segment.size[1] - precrop))
    borders = bordercrop.borders(preprocessed, blackThreshold, segment.size[0] * rowThreshold, minRowsForBorder)
    print(borders)
    return preprocessed.crop(borders)

def onThresholdChange(event):
    print(f"Threshold: {event}")
    global cfg
    cfg.THRESHOLD = int(event)
    updatePreview(cropBlackbarsFromImage(state.ogImage, cfg.precrop, cfg.THRESHOLD, cfg.MINIMUM_THRESHOLD_HITTING, cfg.MINIMUM_ROWS), state)

def onThresholdMinChange(event):
    print(f"Threshold Min: {event}")
    global cfg
    cfg.MINIMUM_THRESHOLD_HITTING = int(event)
    updatePreview(cropBlackbarsFromImage(state.ogImage, cfg.precrop, cfg.THRESHOLD, cfg.MINIMUM_THRESHOLD_HITTING, cfg.MINIMUM_ROWS), state)

def onMinimumRowsChange(event):
    print(f"Minimum Rows: {event}")
    global cfg
    cfg.MINIMUM_ROWS = int(event)
    updatePreview(cropBlackbarsFromImage(state.ogImage, cfg.precrop, cfg.THRESHOLD, cfg.MINIMUM_THRESHOLD_HITTING, cfg.MINIMUM_ROWS), state)

if __name__ == "__main__":
    global state
    global cfg
    state = State()
    cfg = Cfg()
    state.root = Tk()
    state.root.geometry('1500x1000')
    state.root.title("Border Crop Test")
    selectFileButton = Button(state.root, text="Select File", command=selectFileToLoad)
    resetButton = Button(state.root, text="Reset", command=lambda: updatePreview(state.ogImage, state))
    cropButton = Button(state.root, text="Crop", command=lambda: updatePreview(cropBlackbarsFromImage(state.ogImage, cfg.precrop, cfg.THRESHOLD, cfg.MINIMUM_THRESHOLD_HITTING, cfg.MINIMUM_ROWS), state))
    thresholdLabel = Label(state.root, text="Threshold")
    thresholdSlider = Scale(state.root, from_=1, to=512, orient=HORIZONTAL, command=onThresholdChange)
    mThresholdLabel = Label(state.root, text="Minimum Threshold Hits")
    mThresholdSlider = Scale(state.root, from_=1, to=512, orient=HORIZONTAL, command=onThresholdMinChange)
    mRowsLabel = Label(state.root, text="Minimum Rows")
    minRowsSlider = Scale(state.root, from_=1, to=512, orient=HORIZONTAL, command=onMinimumRowsChange)

    mThresholdSlider.set(cfg.MINIMUM_THRESHOLD_HITTING)
    thresholdSlider.set(cfg.THRESHOLD)
    minRowsSlider.set(cfg.MINIMUM_ROWS)

    thresholdLabel.pack()
    thresholdSlider.pack()
    mThresholdLabel.pack()
    mThresholdSlider.pack()
    mRowsLabel.pack()
    minRowsSlider.pack()

    selectFileButton.pack()
    resetButton.pack()
    cropButton.pack()
    state.root.mainloop()