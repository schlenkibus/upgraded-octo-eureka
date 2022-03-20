from PIL import Image
import colorthief, colorsys
import sys, os, io
import getopt

numFilt = 0
style = "H"

def dominant(im):
    global numFilt
    global style
    with io.BytesIO() as file_object:
        print(f"processing filter[{numFilt}]")
        numFilt += 1
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
    print(argv)
    infile = ""
    outfile = ""
    segmentsize = 0
    local_style = ""

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"hi:o:t:s:",["help","inimage=","outimage=","type=","segment_size="])
    except getopt.GetoptError:
        print(f"create_sorted_image.py -o <outimage> -i <inimage> -t <type> [H/S/V] -s <segment_size>")
        sys.exit(2)

    print(args)
    print(opts)

    for opt, arg in opts:
        print(f"parsing opt: {opt} arg: {arg}")
        if opt == '-h':
            print(f"create_sorted_image.py -o <outimage> -i <inimage> -t <type> [H/S/V] -s <segment_size>")
            sys.exit(1)
        elif opt in ("-o", "--output"):
            outfile = arg
        elif opt in ("-i", "--input"):
            infile = arg
        elif opt in ("-s", "--segment_size"):
            segmentsize = int(arg)
        elif opt in ("-t", "--type"):
            local_style = arg

    global style
    style = local_style

    if not os.path.exists(infile):
        print(f"{infile} does not exists")
        sys.exit(3)

    if not os.path.exists(outfile):
        with Image.open(infile) as im:
            crops = []
            width, height = im.size
            singleSize = segmentsize
            wSegments = int(width / singleSize)
            hSegments = int(height / singleSize)
            totalSegments = wSegments * hSegments
            
            print(totalSegments)

            for xIndex in range(wSegments):
                for yIndex in range(hSegments):
                    x = int(xIndex * singleSize)
                    y = int(yIndex * singleSize)
                    crops.append(im.crop((x, y, x + singleSize, y + singleSize)))

            sortedCrops = sorted(crops, key=dominant)

            newImg = Image.new(('RGB'), im.size)
            numImagesProcessed = 0

            for xIndex in range(wSegments):
                for yIndex in range(hSegments):
                    index = numImagesProcessed
                    print(f"processing crop[{index}]")
                    x = int(xIndex * singleSize)
                    y = int(yIndex * singleSize)
                    newImg.paste(sortedCrops[index], (x, y))
                    numImagesProcessed += 1
            
            newImg.save(outfile)

###############################################################################
###############################################################################
if __name__ == "__main__":
    main(sys.argv[1:])