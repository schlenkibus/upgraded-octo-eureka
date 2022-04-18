from PIL import Image
import colorthief, colorsys
import sys, os, io
import getopt


numFilt = 0
style = "H"
totalSegments = 0

def dominant(im):
    global numFilt
    global style
    global totalSegments

    with io.BytesIO() as file_object:
        #print progressbar
        numFilt += 1
        print(f"\rprocessing images... {numFilt}/{totalSegments}", end="")
        im.save(file_object, "PNG")
        color_thief = colorthief.ColorThief(file_object)
        rgb = color_thief.get_color(quality=1)
        hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
        if style == 'H':
            return hsv[0]
        if style == 'S':
            return hsv[1]
        if style == 'V':
            return hsv[2]

def main(argv):
    infile = ""
    outfile = ""
    segmentsize = 0
    local_style = ""
    force = False

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"hi:o:t:s:f",["help","inimage=","outimage=","type=","segment_size=", "force"])
    except getopt.GetoptError:
        print(f"create_sorted_image.py -o <outimage> -i <inimage> -t <type> [H/S/V] -s <segment_size> -f")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print(f"create_sorted_image.py -o <outimage> -i <inimage> -t <type> [H/S/V] -s <segment_size> -f")
            sys.exit(1)
        elif opt in ("-o", "--output"):
            outfile = arg
        elif opt in ("-i", "--input"):
            infile = arg
        elif opt in ("-s", "--segment_size"):
            segmentsize = int(arg)
        elif opt in ("-t", "--type"):
            local_style = arg
        elif opt in ("-f", "--force"):
            force = True

    global style
    style = local_style

    if not os.path.exists(infile):
        print(f"{infile} does not exists")
        sys.exit(3)

    if not os.path.exists(outfile) or force:
        with Image.open(infile) as im:
            crops = []
            width, height = im.size
            singleSize = segmentsize
            wSegments = int(width / singleSize)
            hSegments = int(height / singleSize)

            global totalSegments
            totalSegments = wSegments * hSegments
            
            for xIndex in range(wSegments):
                for yIndex in range(hSegments):
                    x = int(xIndex * singleSize)
                    y = int(yIndex * singleSize)
                    crops.append(im.crop((x, y, x + singleSize, y + singleSize)))

            #sortedCrops = sorted(crops, key=dominant)
            sortedCrops = crops

            newImage = Image.new(('RGB'), im.size)
            numImagesProcessed = 0

            xDelta = 0
            yDelta = 0
            
            lastYStart = 0

            #traverse all possible postions from the top left corner moving up and to the right
            for crop in sortedCrops:
                print(f"pasting at {xDelta}, {yDelta}")
                newImage.paste(crop, (xDelta, yDelta))
                xDelta += singleSize
                yDelta -= singleSize

                #when whe hit the upper bound of the desired image we need to jump to the front and below already pasted lines
                if yDelta < 0:
                    lastYStart += 1
                    lastYStart = min(lastYStart, hSegments)
                    yDelta = lastYStart
                    xDelta = 0

                if xDelta + singleSize > width:
                    xDelta = 0
                    yDelta += singleSize
                    if yDelta + singleSize > height:
                        yDelta = 0
                if yDelta < 0:

                numImagesProcessed += 1


            #end algorithm


            #while numImagesProcessed < totalSegments:



             #   print(f"stiching image... x: {xDelta} y: {yDelta}, numImagesProcessed: {numImagesProcessed}")
              #  newImage.paste(sortedCrops[numImagesProcessed], (xDelta * singleSize, yDelta * singleSize))
               # numImagesProcessed += 1

                #if yDelta == 0:
                 #   xDelta = 0
                  #  yDelta = min(lastYStart + 1, hSegments)
                   # lastYStart = yDelta
                   # lastYStart = yDelta                    
                #else:
                 #   yDelta -= 1
                  #  xDelta += 1
                   # xDelta = min(xDelta, wSegments)
            
            newImage.save(outfile)
    else:
        print(f"{outfile} already exists (specify -f to force overwrite)")
        sys.exit(5)

###############################################################################
###############################################################################
if __name__ == "__main__":
    main(sys.argv[1:])