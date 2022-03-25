import getopt
import sys
import os
from PIL import Image, ImageFilter
import bordercrop
import random

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

def storeImage(segment, outputPath, suffix):
    name = outputPath.split(".")[0]
    pwd = os.getcwd()
    segment.save(pwd + name + suffix + ".png")

def stichEvenRows(segments, outputImagePath, singleSize, numbuckets, shuffle=False, seed=187):

    sortedSegments = segments

    if shuffle:
        random.seed(seed)
        random.shuffle(sortedSegments)
    else:
        sortedSegments = sorted(segments, key=lambda x: x.size[1])

    buckets = []

    #create buckets
    for i in range(numbuckets):
        buckets.append([])
    
    for segment in sortedSegments:
        #determine current max height of the buckets
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

        #add segment to bucket
        buckets[maxDiffIndex].append(segment)

    maxHeight = 0
    for bucket in buckets:
        totalHeight = 0
        for segment in bucket:
            totalHeight += segment.size[1]
        maxHeight = max(maxHeight, totalHeight)

    #create image to hold all contents of the buckets
    newImg = Image.new(('RGB'), (singleSize * numbuckets, maxHeight))
    
    #paste bucket into new image
    for index, bucket in enumerate(buckets):
        y = 0
        for segment in bucket:
            newImg.paste(segment, (index * singleSize, y))
            y += segment.size[1]

    #save image
    storeImage(newImg, outputImagePath, "_evenRows")

def stichAndSave(sortedSegments, suffix, outputImagePath, wSegments, hSegments, singleSize):
    newImg = Image.new(('RGB'), (wSegments * singleSize, hSegments * singleSize))

    #set the background color to white
    newImg.paste((255, 255, 255), (0, 0, newImg.size[0], newImg.size[1]))

    for index, segment in enumerate(sortedSegments):
        x = int(index % wSegments) * singleSize
        y = int(index / wSegments) * singleSize
        newImg.paste(segment, (x, y))

    storeImage(newImg, outputImagePath, suffix)

def cropBlackbarsFromImage(segment, precrop, blackThreshold=1, rowThreshold=0.95, minRowsForBorder=3):
    preprocessed = segment.crop((0, precrop, segment.size[0], segment.size[1] - precrop))
    borders = bordercrop.borders(preprocessed, blackThreshold, segment.size[0] * rowThreshold, minRowsForBorder)
    return preprocessed.crop(borders)

def main(argv):
    imageSectionSize = 0
    inputImagePath = ""
    outputImagePath = ""

    try:
        opts, args = getopt.getopt(argv,"hi:o:s:",["help","inimage=","outimage=","segment_size="])
    except getopt.GetoptError:
        print(f"group_similar.py -o <outimage> -i <inimage> -s <segment_size>")
        sys.exit(2)

    for opt, arg in opts:
        print(f"parsing opt: {opt} arg: {arg}")
        if opt == '-h':
            print(f"group_similar.py -o <outimage> -i <inimage> -s <segment_size>")
            sys.exit(1)
        elif opt in ("-o", "--output"):
            outputImagePath = arg
        elif opt in ("-i", "--input"):
            inputImagePath = arg
        elif opt in ("-s", "--segment_size"):
            imageSectionSize = int(arg)

    #load image into memory
    if not os.path.exists(inputImagePath):
        print(f"{inputImagePath} does not exists")
        sys.exit(3)

    image = Image.open(inputImagePath)

    #split image into segments
    width, height = image.size
    singleSize = imageSectionSize
    wSegments = int(width / singleSize)
    hSegments = int(height / singleSize)

    #create a list of all the segments
    segments = []
    for xIndex in range(wSegments):
        for yIndex in range(hSegments):
            x = int(xIndex * singleSize)
            y = int(yIndex * singleSize)
            segment = image.crop((x, y, x+singleSize, y+singleSize))
            segments.append(segment)

    croppedSegments = []
    for segment in segments:
        cropped = cropBlackbarsFromImage(segment, precrop=5, blackThreshold=5, rowThreshold=0.95, minRowsForBorder=3)      
        if cropped.size[1] > 10:  
            croppedSegments.append(cropped)

    stichEvenRows(croppedSegments, outputImagePath, singleSize, numbuckets=10, shuffle=True)

    #sort segments by their height
    sortedSegments = sorted(segments, key=lambda x: x.size[1])
    #paste images into one horizontal image and paste segements
    stichAndSave(sortedSegments, "_horizontal", outputImagePath, len(sortedSegments), 1, singleSize)

    #sort segments based on the color temperature
    sortedSegments = sorted(sortedSegments, key=lambda x: x.getpixel((0,0)))
    #stich image together
    stichAndSave(sortedSegments, "_temperature", outputImagePath, wSegments, hSegments, singleSize)

    #sort all segments again based on their amount of black pixels
    sortedSegments = sorted(sortedSegments, key=lambda x: x.getbbox()[3])
    stichAndSave(sortedSegments, "_black-pixels", outputImagePath, wSegments, hSegments, singleSize)


#program entry 
if __name__ == "__main__":
    main(sys.argv[1:])