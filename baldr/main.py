import os
from PIL import Image, ImageDraw
from random import choices, shuffle
import argparse
from pathlib import Path


def chunk(seq, size, groupByList=True):
    """Returns list of lists/tuples broken up by size input"""
    func = tuple
    if groupByList:
        func = list
    return [func(seq[i: i + size]) for i in range(0, len(seq), size)]


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


def fill_in_missing_colors(num_squares_total, colors):
    """Returns a list of colors with length equal to num_squares_total"""
    k = num_squares_total - len(colors)
    if k < 0:
        return colors
    # Missing k colors, fill in by randomly sampling from the list
    missing = choices(colors, k=k)
    return colors + missing


def get_colors_from_img(image, num_colors):
    """
    Returns a list of colors from the image
    with length equal to num_squares_total
    """
    # Get the pallet from the image
    colors = get_palette_in_rgb(image)

    # Get all the distinct colors
    distinct_colors = list(set(colors))

    distinct_colors = fill_in_missing_colors(
        num_colors, distinct_colors
    )

    # Get the first n random colors
    shuffle(distinct_colors)
    return distinct_colors[:num_colors]


def draw_squares(width, height, square_size, colors):
    """Draws a sequence of squares on an image using a list of colors"""
    x1, y1 = 0
    x2, y2 = square_size
    im = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(im)

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
    return im


def get_unique_filename(path):
    """Adds a suffix to filename if it already exists"""
    filename, extension = os.path.splitext(path)
    suffix = 1
    while os.path.exists(path):
        path = f"{filename}({str(suffix)}){extension}"
        suffix += 1
    return path


def run(
    image_path: str,
    width: int,
    height: int,
    square_size: int,
    save: bool,
    open: bool,
) -> None:
    # Size for the new picture
    num_squares_x = width
    num_squares_y = height
    num_squares_total = num_squares_x * num_squares_y
    width = num_squares_x * square_size
    height = num_squares_y * square_size

    # Get the original image
    try:
        original_image = Image.open(image_path)
    except Exception as e:
        print(e)
        exit()

    # Convert the image to pallet mode
    pallet_image = original_image.convert(mode="P")

    # Get the colors as a list of tuples
    colors = get_colors_from_img(pallet_image, num_colors=num_squares_total)

    # Draw the new image using the pallet
    square_image = draw_squares(width, height, square_size, colors)

    if open:
        square_image.show()
    if save:
        original_filaname = Path(image_path).stem
        filename = get_unique_filename(f"{original_filaname}-colors.png")
        square_image.save(filename, format="PNG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
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
        help="Size of each square",
        choices=range(1, 257),
        metavar="[1-256]",
        default=128,
        type=int,
    )
    parser.add_argument(
        "-s",
        "--save",
        help="Save the image to the current path as a png file",
    )
    parser.add_argument(
        "-o", "--open", help="Open the image", action="store_true"
    )
    args = parser.parse_args()

    run(
        image_path=args.image_path,
        width=args.width,
        height=args.height,
        square_size=args.square_size,
        save=args.save,
        open=args.open,
    )
