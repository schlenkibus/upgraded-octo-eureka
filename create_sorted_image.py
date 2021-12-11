from PIL import Image
import colorthief, colorsys
import sys, os, io

numFilt = 0

def dominant(im):
    global numFilt
    with io.BytesIO() as file_object:
        print(f"processing filter[{numFilt}]")
        numFilt += 1
        im.save(file_object, "PNG")
        color_thief = colorthief.ColorThief(file_object)
        rgb = color_thief.get_color(quality=1)
        hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
        return hsv[1]

if len(sys.argv) == 3:
    infile = sys.argv[1]
    outfile = sys.argv[2]
    if os.path.exists(infile) and not os.path.exists(outfile):
        with Image.open(infile) as im:
            crops = []
            width, height = im.size
            singleSize = 256
            wSegments = int(width / singleSize)
            hSegments = int(height / singleSize)
            totalSegments = wSegments * hSegments
            
            print(totalSegments)

            for xIndex in range(wSegments):
                for yIndex in range(hSegments):
                    x = int(xIndex * 256)
                    y = int(yIndex * 256)
                    crops.append(im.crop((x, y, x + 256, y +256)))

            sortedCrops = sorted(crops, key=dominant)

            newImg = Image.new(('RGB'), im.size)
            numImagesProcessed = 0

            for xIndex in range(wSegments):
                for yIndex in range(hSegments):
                    index = numImagesProcessed
                    print(f"processing crop[{index}]")
                    x = int(xIndex * 256)
                    y = int(yIndex * 256)
                    newImg.paste(sortedCrops[index], (x, y))
                    numImagesProcessed += 1
            
            newImg.save(outfile)