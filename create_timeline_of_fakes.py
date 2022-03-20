from PIL import Image
import sys, os, io
import getopt

numFilt = 0

def main(argv):
    print(argv)
    indir = ""
    outfile = ""
    segmentsize = 0
    index_of_interest_x = 0
    index_of_interest_y = 0

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:x:y:",["help","indir=","outfile=","segment_size=","x=","y="])
    except getopt.GetoptError:
        print(f"create_timeline_of_fakes.py -o <outfile> -i <indir> -s <segment_size> -x <x> -y <y>")
        sys.exit(2)

    print(args)
    print(opts)

    for opt, arg in opts:
        print(f"parsing opt: {opt} arg: {arg}")
        if opt == '-h':
            print(f"create_timeline_of_fakes.py -o <outfile> -i <indir> -s <segment_size> -x <x> -y <y>")
            sys.exit(1)
        elif opt in ("-o", "--output"):
            outfile = arg
        elif opt in ("-i", "--input"):
            indir = arg
        elif opt in ("-x", "--x"):
            index_of_interest_x = int(arg)
        elif opt in ("-y", "--y"):
            index_of_interest_y = int(arg)
        elif opt in ("-s", "--segment_size"):
            segmentsize = int(arg)


    if not os.path.isdir(indir):
        print(f"{indir} is not an directory")
        sys.exit(3)

    if os.path.exists(outfile):
        print(f"{outfile} already exists")
        sys.exit(4)

    f = []
    for (dirpath, dirnames, filenames) in os.walk(indir):
        f.extend(filenames)
        break

    #filter out files to only include fakes
    f = [file for file in f if 'fakes' in file]
    f = [file for file in f if '.png' in file]
    f = [file for file in f if not 'init' in file]
    f = [file for file in f if not 'fakes000000.png' in file]
    print(f"filtered {f}")
    #sort files based on number
    list.sort(f)
    print(f"sorted {f}")

    segments = []

    for image in f:
        with Image.open(os.path.join(indir, image)) as im:
            singleSize = segmentsize
            x = int(index_of_interest_x * singleSize)
            y = int(index_of_interest_y * singleSize)
            segments.append(im.crop((x, y, x + singleSize, y + singleSize)))
            print(len(segments))

    newImg = Image.new(('RGB'), [len(segments) * singleSize, singleSize])
    xIndex = 0
    for segment in segments:
        x = int(xIndex * singleSize)
        newImg.paste(segment, (x, 0))
        xIndex += 1
            
    newImg.save(outfile)

###############################################################################
###############################################################################
if __name__ == "__main__":
    main(sys.argv[1:])