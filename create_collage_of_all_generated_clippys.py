import argparse
from subprocess import DEVNULL

parser = argparse.ArgumentParser(description='Create Graffiti')
parser.add_argument(
    '--outputpath',
    type=str,
    default='/data/GANfitti/generated_clip/',
    help='Path to output directory'
)

parser.add_argument(
    '--input_dir',
    type=str,
    default='samples_directory',
    help='Path to input directory'
)

parser.add_argument(
    '--num_images',
    type=int,
    default=1000,
    help='num images to use'
)

parser.add_argument(
    '--space_between_images',
    type=int,
    default=10,
    help='select each nth image'
)   

parser.add_argument(
    "--seed",
    type=int,
    default=-1,
    help="seed for shuffle -1 for un-shuffled"    
)

parser.add_argument(
    "--buckets",
    type=int,
    default=3,
    help="number buckets"    
)

args = parser.parse_args()

import PIL.Image, os

buckets = args.buckets
image_size = 512

dir_index = 0
for (dirpath, dirnames, filenames) in os.walk(args.input_dir):
    for dirPath in dirnames:
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(args.input_dir, dirPath)):

            print(f"processing {os.path.join(args.input_dir, dirPath)}")

            f = []
            f.extend(filenames)

            segments = []
            for image in f:
                    segments.append(PIL.Image.open(os.path.join(dirpath, image)))

            segments = segments[:100]

            print(f"num segements {len(segments)}")

            #drop nth image until num_images are met
            images_collected = []
            last_idx = 0

            while len(images_collected) < args.num_images and last_idx < len(segments):
                images_collected.append(segments[last_idx])
                last_idx += args.space_between_images
            
            import subprocess
            import shutil

            if os.path.isdir(f"/tmp/fooo"):
                shutil.rmtree(f"/tmp/fooo")
            os.mkdir(f"/tmp/fooo")

            #paste images into directory

            idx = 0
            for i in images_collected:
                name = f"{idx}-f.png"
                path = os.path.join("/tmp/fooo", name)
                i.save(path)
                idx += 1

            #call create_timeline_of_fakes
            timeline_of_fakes = subprocess.Popen(['python3', 'create_timeline_of_fakes.py', '-o', "/tmp/fooo/timeline.png", "-i", "/tmp/fooo", "-s", str(image_size), "-x", "0", "-y", "0", "-n", "9999"], stdin=DEVNULL, stdout=DEVNULL)
            timeline_of_fakes.wait()
            #call create_even_buckets
            outName = f"b{buckets}-{dir_index}-n{args.num_images}-s{args.seed}-collage.png"
            even_buckets = subprocess.Popen(['python3', 'create_even_buckets.py', "-o", os.path.join(args.outputpath, outName), '-i', '/tmp/fooo/timeline.png', "-s", str(image_size), "-b", str(buckets), "-r", str(args.seed), "-c", "s"], stdin=DEVNULL, stdout=DEVNULL)
            even_buckets.wait()

            dir_index += 1
            shutil.rmtree(f"/tmp/fooo")