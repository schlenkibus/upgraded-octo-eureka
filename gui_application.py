from curses.textpad import Textbox
import random
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import glob
import os
import sys
import bordercrop

global root
global state
root = None
state = None

class State:
	def __init__(self):
		self.xSel = 0
		self.ySel = 0
		self.tileSize = None
		self.previewImage = None
		self.previewImageTK = None
		self.previewImagePIL = None
		self.referenceImage = None
		self.tileSizeSV = None
		self.allImages = []
		self.allSegmentsRaw = []
		self.currentFrame = None

state = State()

def pressed(event):
    print(f"pressed at: {event.x}/{event.y}")

def released(event):
    print(f"released at: {event.x}/{event.y}")

def drag(event):
    print(f"drag at: {event.x}/{event.y}")

def key(event):
    print(f"pressed key: {event.char}")

def queryDirectory():
    directory = filedialog.askdirectory(initialdir = "/",
                                          title = "Select a Directory")
    return directory

def queryFile():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File")
    return filename

def querySaveAs():
	saveAs = filedialog.asksaveasfilename(initialdir = "/",
										  title = "Select a File")
	return saveAs

def up():
	global state
	state.ySel -= 1
	state.ySel = max(state.ySel, 0)
	updateSelection()
	print(f"up: {state.ySel}")

def down():
	global state
	state.ySel += 1
	state.ySel = min(state.ySel, state.referenceImage.height // state.tileSize)
	updateSelection()
	print(f"down: {state.ySel}")

def left():
	global state
	state.xSel -= 1
	state.xSel = max(state.xSel, 0)
	updateSelection()
	print(f"left: {state.xSel}")

def right():
	global state
	state.xSel += 1
	state.xSel = min(state.xSel, state.referenceImage.width // state.tileSize)
	updateSelection()
	print(f"right: {state.xSel}")

def updateSelection():
	global state
	global root
	print(f"updateSelection: {state.xSel}/{state.ySel}")

	if state.tileSize != None:
		if state.previewImage != None:
			state.previewImage.destroy()

		state.previewImagePIL = state.referenceImage.crop((state.xSel * state.tileSize, state.ySel * state.tileSize, (state.xSel + 1) * state.tileSize, (state.ySel + 1) * state.tileSize))
		state.previewImageTK = ImageTk.PhotoImage(state.previewImagePIL)
		state.previewImage = Label(state.currentFrame, image=state.previewImageTK)
		state.previewImage.image = state.previewImageTK
		state.previewImage.pack()

def returnPressed(event):
	global state
	print(f"tile size changed: {int(state.tileSizeSV.get())}")
	state.tileSize = int(state.tileSizeSV.get())
	updateSelection()
	return True

def updateResultImage():
	newImage = stichEvenRows(state.allSegmentsRaw, state.tileSize, state.numBuckets)	
	newImage = newImage.resize((state.referenceImage.width, state.referenceImage.height))
	#save image with prompt
	newImage.save(querySaveAs())


def loadImageTileFromAllInDirectory():
	global state

	for imagePath in state.allImages:
		image = Image.open(imagePath)
		crop = image.crop((state.xSel * state.tileSize, state.ySel * state.tileSize, (state.xSel + 1) * state.tileSize, (state.ySel + 1) * state.tileSize))
		state.allSegmentsRaw.append(crop)

	state.numBuckets = 5
	updateResultImage()
	
def getTotalHeightOfBucket(bucket):
    totalHeight = 0
    for segment in bucket:
        totalHeight += segment.size[1]
    return totalHeight

def getMaxTotalHeight(buckets):
    maxHeight = 0
    for bucket in buckets:
        maxHeight = max(maxHeight, getTotalHeightOfBucket(bucket))
    return maxHeight

def stichEvenRows(segments, singleSize, numbuckets, shuffle=False, seed=187):

    sortedSegments = segments

    if shuffle:
        random.seed(seed)
        random.shuffle(sortedSegments)
    else:
        sortedSegments = sorted(segments, key=lambda x: x.size[1], reverse=True)

    buckets = []

    #create buckets
    for i in range(numbuckets):
        buckets.append([])
    
    for segment in sortedSegments:
        maxHeight = getMaxTotalHeight(buckets)

        #find the bucket that has the most difference to the current max height
        maxDiff = 0
        maxDiffIndex = 0
        for index, bucket in enumerate(buckets):
            height = getTotalHeightOfBucket(bucket)
            diff = abs(height - maxHeight)
            if diff > maxDiff:
                maxDiff = diff
                maxDiffIndex = index

        buckets[maxDiffIndex].append(segment)

    maxHeight = 0
    for bucket in buckets:
        totalHeight = 0
        for segment in bucket:
            totalHeight += segment.size[1]
        maxHeight = max(maxHeight, totalHeight)

    newImg = Image.new(('RGB'), (singleSize * numbuckets, maxHeight))
    
    for index, bucket in enumerate(buckets):
        y = 0
        for segment in bucket:
            newImg.paste(segment, (index * singleSize, y))
            y += segment.size[1]
    return newImg

def cropBlackbarsFromImage(segment, precrop, blackThreshold=1, rowThreshold=0.99, minRowsForBorder=3):
    preprocessed = segment.crop((0, precrop, segment.size[0], segment.size[1] - precrop))
    borders = bordercrop.borders(preprocessed, blackThreshold, segment.size[0] * rowThreshold, minRowsForBorder)
    print(borders)
    return preprocessed.crop(borders)

#Phase 2 - Segmentation
def selectTimelineToCreateSingleImageFrom():
	global root
	global state

	directory = queryDirectory()
	if directory:
		print(directory)
	else:
		print("No directory selected")
		return

	foundImages = []
	for file in glob.glob(directory + "/*.png"):
		foundImages.append(file)
	
	if state.currentFrame:
		state.currentFrame.destroy()
	
	state.currentFrame = Frame(root)
	
	state.allImages = foundImages

	previewImageOG = Image.open(foundImages[0])
	previewImage = previewImageOG.resize((1200, 800), Image.NONE)
	state.referenceImage = previewImageOG
	imagetk = ImageTk.PhotoImage(previewImage)
	previewLabel = Label(state.currentFrame, image=imagetk)
	previewLabel.image = imagetk
	previewLabel.pack()

	#tile size
	label = Label(state.currentFrame, text="Tile Size")
	label.pack()
	state.tileSizeSV = StringVar()
	input = Entry(state.currentFrame, textvariable=state.tileSizeSV)
	input.bind("<Return>", returnPressed)
	input.pack()

	buttonUp = Button(state.currentFrame, text="Up", command=up)
	buttonUp.pack()
	buttonDown = Button(state.currentFrame, text="Down", command=down)
	buttonDown.pack()
	buttonLeft = Button(state.currentFrame, text="Left", command=left)
	buttonLeft.pack()
	buttonRight = Button(state.currentFrame, text="Right", command=right)
	buttonRight.pack()

	buttonNext = Button(state.currentFrame, text="Next", command=loadImageTileFromAllInDirectory)
	buttonNext.pack()
	state.currentFrame.pack()

	updateSelection()

if __name__ == "__main__":
	root = Tk()
	root.geometry('1500x1000')    
	root.bind("<Button-1>", pressed)
	root.bind("<ButtonRelease-1>", released)
	root.bind("<B1-Motion>", drag)
	root.bind("<Key>", key)
	#Phase 1 Select Working Dir
	state.currentFrame = Frame(root)
	
	button_select_directory = Button(state.currentFrame, text="Select Directory Of Multiple Training Images", command=selectTimelineToCreateSingleImageFrom)
	button_select_directory.pack()
	state.currentFrame.pack()

	root.mainloop()