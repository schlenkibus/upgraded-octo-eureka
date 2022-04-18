import getopt
import sys
import os
from PIL import Image, ImageFilter
import bordercrop
import random

#parse arguments
startPosX = 0
endPosX = 0
imagePath = ""
outPath = ""
segmentSize = 0

def main(argv):
    global startPosX
    global endPosX
    global imagePath
    global outPath
    global segmentSize

    try:
        opts, args = getopt.getopt(argv, "s:e:i:o:n:", ["startPosX=", "endPosX=", "imagePath=", "outPath=", "segmentSize="])
    except getopt.GetoptError:
        print("grab_segements_in_x_direction.py -s <startPosX> -e <endPosX> -i <imagePath> -o <outPath> -n <segmentSize>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-s", "--startPosX"):
            startPosX = int(arg)
        elif opt in ("-e", "--endPosX"):
            endPosX = int(arg)
        elif opt in ("-i", "--imagePath"):
            imagePath = arg
        elif opt in ("-o", "--outPath"):
            outPath = arg
        elif opt in ("-n", "--segmentSize"):
            segmentSize = int(arg)
    print("startPosX:", startPosX)
    print("endPosX:", endPosX)
    print("imagePath:", imagePath)
    print("outPath:", outPath)
    print("segmentSize:", segmentSize)
    #check if all arguments are valid
    if startPosX < 0 or endPosX < 0 or startPosX > endPosX or segmentSize < 0:
        print("Invalid arguments")
        sys.exit(2)
    if imagePath == "" or outPath == "":
        print("Invalid arguments")
        sys.exit(2)
    #check if image exists
    if not os.path.isfile(imagePath):
        print("Image does not exist")
        sys.exit(2)

    if not os.path.exists(outPath):
        print("Output image already exists")

    #load image into memory
    image = Image.open(imagePath)
    #get crop
    crop = image.crop((startPosX * segmentSize, 0, endPosX * segmentSize, image.height))

    #save crop
    crop.save(outPath)

if __name__ == "__main__":
    main(sys.argv[1:])
