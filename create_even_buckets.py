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

def stichEvenRows(segments, outputImagePath, singleSize, numbuckets, shuffle=False, seed=187, backgroundColor=(0,0,0)):

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

    if shuffle:
        storeImage(newImg, outputImagePath, f"_buckets_shuffled_{seed}")
    else:
        storeImage(newImg, outputImagePath, "_buckets")

def cropBlackbarsFromImage(segment, precrop, blackThreshold=1, rowThreshold=0.99, minRowsForBorder=3):
    preprocessed = segment.crop((0, precrop, segment.size[0], segment.size[1] - precrop))
    borders = bordercrop.borders(preprocessed, blackThreshold, segment.size[0] * rowThreshold, minRowsForBorder)
    print(borders)
    return preprocessed.crop(borders)

def getSegments(image, singleSize):
    width, height = image.size
    wSegments = int(width / singleSize)
    hSegments = int(height / singleSize)

    segments = []
    for xIndex in range(wSegments):
        for yIndex in range(hSegments):
            x = int(xIndex * singleSize)
            y = int(yIndex * singleSize)
            segment = image.crop((x, y, x+singleSize, y+singleSize))
            segments.append(segment)
    return segments

def main(argv):
    imageSectionSize = 0
    inputImagePath = ""
    outputImagePath = ""
    numberBuckets = 0
    minYPixelsForSegment = 2
    shuffle = False
    seed = -1

    try:
        opts, args = getopt.getopt(argv,"hi:o:s:b:m:s:r:",["help","inimage=","outimage=","segment_size=","buckets=","min_y_pixels=", "random_seed="])
    except getopt.GetoptError:
        print(f"create_even_buckets.py -o <outimage> -i <inimage> -s <segment_size> -b <buckets> -m <min_y_pixels> -r <random_seed> (or -1 for no random seed)")
        sys.exit(2)

    for opt, arg in opts:
        print(f"parsing opt: {opt} arg: {arg}")
        if opt == '-h':
            print(f"create_even_buckets.py -o <outimage> -i <inimage> -s <segment_size> -b <buckets> -m <min_y_pixels> -r <random_seed> (or -1 for no random seed)")
            sys.exit(1)
        elif opt in ("-o", "--output"):
            outputImagePath = arg
        elif opt in ("-i", "--input"):
            inputImagePath = arg
        elif opt in ("-s", "--segment_size"):
            imageSectionSize = int(arg)
        elif opt in ("-b", "--buckets"):
            numberBuckets = int(arg)
        elif opt in ("-m", "--min_y_pixels"):
            minYPixelsForSegment = int(arg)
        elif opt in ("-r", "--random_seed"):
            if arg == "-1":
                shuffle = False
            else:
                shuffle = True
                seed = int(arg)

    isDirectory = os.path.isdir(inputImagePath)
    
    images = []

    if isDirectory:
        #add all images in inputImagePath directory into images
        for file in os.listdir(inputImagePath):
            if file.endswith(".png"):
                images.append(Image.open(inputImagePath + "/" + file))
    else:
        images.append(Image.open(inputImagePath))

    
    segments = []

    for image in images:
        for segment in getSegments(image, imageSectionSize):
            segments.append(segment)

    croppedSegments = []
    for segment in segments:
        cropped = cropBlackbarsFromImage(segment, precrop=0, blackThreshold=128, rowThreshold=0.99, minRowsForBorder=3)      
        #if cropped.size[1] > minYPixelsForSegment:  
        croppedSegments.append(cropped)

    print(len(croppedSegments))

    stichEvenRows(croppedSegments, outputImagePath, imageSectionSize, numberBuckets, shuffle, seed)
    return

if __name__ == "__main__":
    main(sys.argv[1:])