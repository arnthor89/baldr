import argparse
import os
from multiprocessing import Pool
from pathlib import Path
from random import choices, shuffle

import tqdm
from PIL import Image, ImageDraw

OPTIONS = None


class Options:
    def __init__(
        self,
        image_path: str,
        pallet_image: Image,
        width: int,
        height: int,
        square_size: int,
        num_colors: int,
        num_pictures: int,
        test: bool,
    ) -> None:
        self.image_path = image_path
        self.pallet_image = pallet_image
        # Size for the new picture
        self.num_squares_x = width
        self.num_squares_y = height
        self.num_squares_total = self.num_squares_x * self.num_squares_y
        self.width = self.num_squares_x * square_size
        self.height = self.num_squares_y * square_size
        self.square_size = square_size
        self.num_colors = num_colors
        self.num_pictures = num_pictures
        self.output_path = self.get_output_path()
        self.test = test

    def get_output_path(self):
        """Sets the global output path"""
        # Create a dictionary for the output
        current_path = Path().resolve()
        dir_path = self.get_unique_filename(Path(self.image_path).stem)
        return os.path.join(current_path, dir_path)

    def get_unique_filename(self, path):
        """Adds a suffix to filename if it already exists"""
        filename, extension = os.path.splitext(path)
        suffix = 1
        while os.path.exists(path):
            path = f"{filename}({str(suffix)}){extension}"
            suffix += 1
        return path


def chunk(seq, size, groupByList=True):
    """Returns list of lists/tuples broken up by size input"""
    func = tuple
    if groupByList:
        func = list
    return [func(seq[i : i + size]) for i in range(0, len(seq), size)]


def get_palette_in_rgb(img):
    """
    Returns list of RGB tuples found in the image palette
    :type img: Image.Image
    :rtype: list[tuple]
    """
    assert img.mode == "P", "image should be palette mode"
    pal = img.getpalette()
    colors = chunk(pal, 3, False)
    return colors


def fill_in_missing_colors(num_colors, colors):
    """Returns a list of colors with length equal to num_squares_total"""
    k = num_colors - len(colors)
    if k < 0:
        return colors
    # Missing k colors, fill in by randomly sampling from the list
    missing = choices(colors, k=k)
    return colors + missing


def get_random_colors(image, num_squares_total, num_colors):
    """
    Returns a list of colors from the image
    with length equal to num_squares_total
    """
    # Get the pallet from the image
    colors = get_palette_in_rgb(image)

    # Get all the distinct colors
    distinct_colors = list(set(colors))

    # In case we have too few colors
    distinct_colors = fill_in_missing_colors(num_colors, distinct_colors)

    # Get the first n random colors
    shuffle(distinct_colors)
    return fill_in_missing_colors(num_squares_total, distinct_colors[:num_colors])


def draw_squares(width, height, square_size, colors):
    """Draws a sequence of squares on an image using a list of colors"""
    x1 = 0
    y1 = 0
    x2 = square_size
    y2 = square_size
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)

    for color in colors:
        draw.rectangle([(x1, y1), (x2, y2)], fill=color)
        if x2 == width:
            x1 = 0
            x2 = square_size
            y1 += square_size
            y2 += square_size
        else:
            x1 += square_size
            x2 += square_size
    return image


def get_unique_filename(path):
    """Adds a suffix to filename if it already exists"""
    filename, extension = os.path.splitext(path)
    suffix = 1
    while os.path.exists(path):
        path = f"{filename}({str(suffix)}){extension}"
        suffix += 1
    return path


def generate_image(index):
    global OPTIONS
    # Get random colors as a list of tuples
    colors = get_random_colors(OPTIONS.pallet_image, OPTIONS.num_squares_total, OPTIONS.num_colors)
    # Draw the new image using the pallet
    image = draw_squares(OPTIONS.width, OPTIONS.height, OPTIONS.square_size, colors)
    file_path = os.path.join(OPTIONS.output_path, f"pic{index}.png")
    if OPTIONS.test:
        image.show()
    else:
        image.save(file_path, format="PNG")
    return True


def run(
    image_path: str,
    width: int,
    height: int,
    square_size: int,
    num_colors: int,
    num_pictures: int,
    test: bool,
) -> None:

    # import time
    # start = time.time()

    # Get the original image
    try:
        original_image = Image.open(image_path)
    except Exception as e:
        print(e)
        exit()

    # Convert the image to pallet mode
    pallet_image = original_image.convert(mode="P")

    global OPTIONS
    OPTIONS = Options(
        image_path,
        pallet_image,
        width,
        height,
        square_size,
        num_colors,
        num_pictures,
        test,
    )

    if test:
        print("Generating a single picture")
        generate_image(0)
        return

    # Create a new directory for the output
    os.mkdir(OPTIONS.output_path)

    print("\nBeep boop bop 🤖")
    print("Generated pictures\n")

    pool = Pool()
    tasks = range(num_pictures)
    for _ in tqdm.tqdm(pool.imap_unordered(generate_image, tasks), total=len(tasks)):
        pass
    pool.close()
    pool.join()

    print(f"\nGenerated {num_pictures} pictures in {OPTIONS.output_path} 🍺")

    # end = time.time()
    # print(f"Elapsed: {end - start}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-i",
        "--image-path",
        help="Image to get color pallet",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--width",
        help="Image width",
        choices=range(1, 51),
        metavar="[1-50]",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--height",
        help="Image height",
        choices=range(1, 51),
        metavar="[1-50]",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--square-size",
        help="Pixels in each square",
        choices=range(1, 513),
        metavar="[1-512]",
        default=128,
        type=int,
    )
    parser.add_argument(
        "--num-colors",
        help="Number of colors to use",
        choices=range(1, 101),
        metavar="[1-100]",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--num-pictures",
        help="Number of pictures to generate",
        choices=range(1, 101),
        metavar="[1-100]",
        default=5,
        type=int,
    )
    parser.add_argument("-t", "--test", help="Will generate and open a single picture", action="store_true")
    args = parser.parse_args()

    run(
        image_path=args.image_path,
        width=args.width,
        height=args.height,
        square_size=args.square_size,
        num_colors=args.num_colors,
        num_pictures=args.num_pictures,
        test=args.test,
    )
