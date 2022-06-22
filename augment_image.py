import argparse

input_dir = ''
output_dir = ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_dir',
        type=str,
        default=input_dir,
        help='Path to input directory'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default=output_dir,
        help='Path to output directory'
    )
    args = parser.parse_args()
    print(args)

    # Create output directory
    import os
    os.makedirs(args.output_dir, exist_ok=True)

    # Loop all images in input directory
    import glob
    for image_path in glob.glob(os.path.join(args.input_dir, '*.jpg')):
        print(image_path)

        #load image
        import cv2, numpy as np
        image = cv2.imread(image_path)

        #blue filter
        lower_range = np.array([0,0,0])  # Set the Lower range value of color in BGR
        upper_range = np.array([100,70,255])   # Set the Upper range value of color in BGR
        mask = cv2.inRange(image,lower_range,upper_range) # Create a mask with range
        result = cv2.bitwise_and(image,image,mask = mask) 

        #save image
        cv2.imshow('image',result)
        outpath = os.path.join(args.output_dir, os.path.basename(image_path), "_blue.jpg")
