import PIL.Image
import os, sys
import getopt

def main(argv):
    print(argv)

    lhsImagePath = ""
    rhsImagePath = ""
    outImagePath = ""

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"hl:r:o:",["help","lhs=","rhs=","out="])
    except getopt.GetoptError:
        print(f"concat_timelines.py -lhs <lhs> -rhs <rhs> -out <out>")
        sys.exit(2)

    for opt, arg in opts:
        print(f"parsing opt: {opt} arg: {arg}")
        if opt == '-h':
            print(f"concat_timelines.py -l <lhs> -r <rhs> -o <out>")
            sys.exit(1)
        elif opt in ("-l", "--lhs"):
            lhsImagePath = arg
        elif opt in ("-r", "--rhs"):
            rhsImagePath = arg
        elif opt in ("-o", "--out"):
            outImagePath = arg
    
    if not os.path.exists(lhsImagePath):
        print(f"{lhsImagePath} does not exist")
        sys.exit(3)

    if not os.path.exists(rhsImagePath):
        print(f"{rhsImagePath} does not exist")
        sys.exit(4)
    
    if os.path.exists(outImagePath):
        print(f"{outImagePath} already exists")
        sys.exit(5)
    
    lhsImage = PIL.Image.open(lhsImagePath)
    rhsImage = PIL.Image.open(rhsImagePath)

    outImage = PIL.Image.new('RGB', (lhsImage.width + rhsImage.width, lhsImage.height))
    outImage.paste(lhsImage, (0, 0))
    outImage.paste(rhsImage, (lhsImage.width, 0))
    outImage.save(outImagePath)

if __name__ == '__main__':
    main(sys.argv[1:])
