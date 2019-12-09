#!/usr/bin/env python3

import numpy as np
from PIL import Image


def read_image(data, width, height):
    pixel_list = list(map(lambda r: int(r), data_raw))
    dim = len(pixel_list)
    layers = int(dim / (width * height))
    img = np.asarray(pixel_list, dtype=np.int)
    return img.reshape(layers, height, width)


def decode_image(img):
    _, height, width = img.shape
    decoded = np.zeros(shape=(height, width), dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            # Find the first non transparent pixel
            res = 0
            for n in img[:, y, x]:
                if n != 2:
                    res = n
                    break
            decoded[y, x] = 255 if res == 1 else 0
    return decoded


width, height = 25, 6
with open("input") as hand:
    for line in hand:
        data_raw = line.strip()

img = read_image(data_raw, width=width, height=height)
min_zeros = None
for n_layer in range(len(img)):
    layer = img[n_layer]
    unique, counts = np.unique(layer, return_counts=True)
    values_map = dict(zip(unique, counts))
    # Count the number of zeros
    n_zeros = values_map[0] if 0 in values_map else 0
    if min_zeros is None or n_zeros < min_zeros:
        min_zeros = n_zeros
        n_ones = values_map[1] if 1 in values_map else 0
        n_two = values_map[2] if 2 in values_map else 0
        result = n_ones * n_two

print("Min zeros", min_zeros)
print("Result", result)

decoded = decode_image(img)
dec_image = Image.fromarray(decoded)
dec_image.save("res.png")
