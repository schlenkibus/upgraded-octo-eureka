import argparse
import random
import os
import PIL
import PIL.Image

#call create_timelines_of_fakes.py for each x and y position on the directory
#and keep track of created files

inputdirectory = ""
outputdirectory = ""
segment_size = 0
number_of_segments = 0
seed = -1

#parse arguments

parser = argparse.ArgumentParser(description='Create timelines of fake videos from a directory of images.')
parser.add_argument('--input', help='The directory of images to use.')
parser.add_argument('--output', help='The directory to save the fake collages to.')
parser.add_argument('--segment_size', help='The size of the segments to use.')
parser.add_argument('--number_of_segments', help='The number of segments to use.')
parser.add_argument('--seed', help='The seed to use for the random number generator.')

args = parser.parse_args()
inputdirectory = args.input
outputdirectory = args.output
segment_size = int(args.segment_size)
number_of_segments = int(args.number_of_segments)
seed = int(args.seed)
random.seed(seed)

print(f"Input directory: {inputdirectory}")
print(f"Output directory: {outputdirectory}")
print(f"Segment size: {segment_size}")
print(f"Number of segments: {number_of_segments}")
print(f"Seed: {seed}")

#get all files in the input directory
files = os.listdir(inputdirectory)
png_files = list(filter(lambda x: x.endswith(".png"), files))
blacklist = ["reals.png", "fakes_init.png"]
png_files = list(filter(lambda x: x not in blacklist, png_files))

print(f"found {len(png_files)} png files")
print(png_files)

image = PIL.Image.open(inputdirectory + "/" + png_files[0])

x_segments = int(image.width / segment_size)
y_segments = int(image.height / segment_size)

del image

#collect N random x y coordinates 
N = number_of_segments
coords = []
coords = []
for i in range(N):
    while True:
        x = random.randint(0, x_segments - 1)
        y = random.randint(0, y_segments - 1)
        if (x, y) not in coords:
            coords.append((x, y))
            break

print(coords)

segment_buckets = dict()

#sort png_files by number
print(png_files)
png_files = sorted(png_files)
print(png_files)    

for it, image_path in enumerate(png_files):
    path = inputdirectory + image_path
    print(f"{it}/{len(png_files)} {path}")
    with PIL.Image.open(path) as image:
        for coord in coords:
            if coord not in segment_buckets:
                segment_buckets[coord] = []

            x = coord[0] * segment_size
            y = coord[1] * segment_size
            segment = image.crop((x, y, x + segment_size, y + segment_size))
            print(f"adding segment {segment} to bucket {coord}")
            segment_buckets[coord].append(segment)
        image.close()

#create a collage of the segments
collage = PIL.Image.new('RGB', (len(segment_buckets[coords[0]]) * segment_size,len(coords)  * segment_size))
for y, coord in enumerate(coords):
    for x, segment in enumerate(segment_buckets[coord]):
        collage.paste(segment, (x * segment_size, y * segment_size))

#save collage
seed_and_num_segments_encoded = "seed_" + str(seed) + "_numSegments_" + str(number_of_segments)
collage.save(outputdirectory + f"{seed_and_num_segments_encoded}_collage.png")

#yield until terminal input was given
while True:
    input("Press enter to continue...")
    break