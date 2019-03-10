
from PIL import Image
import numpy as np
from json import load
from os import path

import argparse

from copy import deepcopy

from vmflib import vmf

from vmflib.types import Vertex
from vmflib.tools import Block

# Add command line args
parser = argparse.ArgumentParser(description="Generate a Source Engine Map layout in VMF format from a 2D layout image")
parser.add_argument("-i", "--image", help="Set the input layout image (Can also be a JSON file with multiple levels)", required=True)
parser.add_argument("-o", "--out", help="Name of the VMF File", required=True)
parser.add_argument("-s", "--pixelsize", help="Length of one pixel in hammer units", required=True, type=int)
parser.add_argument("-t", "--thickness", help="Thickness of the ground in hammer units", required=True, type=int)
parser.add_argument("-m", "--material", help="Material to use on the brush (e.g. 'tools/toolsnodraw')")

# Parse command line args
args = parser.parse_args()._get_kwargs()

# Convert to dict
argv = {}
for argkv in args:
    argv[argkv[0]] = argkv[1]

MULTILEVEL = False
INFILE = argv["image"]
if INFILE.split(".")[-1] == "json":
    MULTILEVEL = True

OUTFILE = argv["out"]
PXSIZE = argv["pixelsize"]
BRUSHWIDTH = argv["thickness"]

TEXTURE = "tools/toolsnodraw"
try:
    TEXTURE = argv["material"]
except KeyError:
    pass

def Units(px):
    return PXSIZE * px

def IsBackgroundColor(c):
    for i in c:
        if i < 128:
            return False
    return True

def GetBoxes(image, height, width):
    # Detect boxes
    layers = []

    currentLayer = []
    currentLine = []
    for y in range(height):
        for x in range(width):

            try:
                if y > currentLayer[0][0][1]:
                    layers.append(currentLayer)
                    currentLayer = []
            except IndexError: pass

            if len(currentLine) == 0 and not IsBackgroundColor(image[y][x]):
                currentLine.append([x, y])
            elif len(currentLine) == 1 and IsBackgroundColor(image[y][x]):
                currentLine.append([x, y])
                currentLayer.append(currentLine)
                currentLine = []

    print("Successfully sliced the image.")
    del currentLayer
    del currentLine

    inprogress = [line for line in layers[0]]
    finalized = []

    ## Match
    for i in range(1, len(layers)):
        BlocksMatched = []
        LinesMatched = []

        # Match every line with every active block
        for m in range(len(inprogress)):
            for n in range(len(layers[i])):
                block = inprogress[m]
                line = layers[i][n]

                if block[0][0] == line[0][0] and block[1][0] == line[1][0]:
                    block[1][1] += 1

                    BlocksMatched.append(m)
                    LinesMatched.append(n)
        
        # Which blocks / lines have been matched?
        # Move matched blocks to finalized[] and move unmatched lines to inprogress[]
        for m in range(len(inprogress)):
            if m not in BlocksMatched:
                # Move block no. m to finalized[]
                finalized.append(deepcopy(inprogress[m]))
                inprogress[m] = None
        
        m = 0
        me = len(inprogress)
        while m < me:
            if inprogress[m] == None:
                del inprogress[m]
                me -= 1
                m -= 1
            m += 1
        
        for n in range(len(layers[i])):
            if n not in LinesMatched:
                inprogress.append(deepcopy(layers[i][n]))
                layers[i][n] = None
        
        n = 0
        ne = len(layers[i])
        while n < ne:
            if layers[i][n] == None:
                del layers[i][n]
                ne -= 1
                n -= 1
            n += 1

    for element in inprogress:
        finalized.append(deepcopy(element))
    del inprogress

    return finalized

def GenerateBlocks(boxes, baseheight):
    blocks = [] # blocks = [..., ((x, y, z), (length, width, height)), ...] ! X Y Z is the origin !
    for block in boxes:
        # block format: [[x1, y1], [x2, y2]] => Length = y2 - y1; height = x2 - x1
        height = (BRUSHWIDTH)
        length = (block[1][0] - block[0][0])
        width = (block[1][1] - block[0][1] + 1)

        x = float((block[0][0] + block[1][0]) / 2)
        y = float((block[0][1] + block[1][1]) / 2) + 0.5
        z = baseheight + float(BRUSHWIDTH / 2)

        blocks.append(((x, y, z), (length, width, height)))
    return blocks

cfg = {}
if MULTILEVEL:
    with open(INFILE) as f:
        cfg = load(f) # Format: { "file": height, "file2": height2, ... }
else:
    cfg[INFILE] = 0

gBlocks = []
for key in cfg:
    imgfile = key
    layerheight = cfg[key]

    # Open image
    img = Image.open(imgfile)
    Layout_Width, Layout_Height = img.size
    Layout = np.array(img)

    print("Processing Image: %s (%d x %d)" % (imgfile, Layout_Width, Layout_Height))
    boxes = GetBoxes(Layout, Layout_Height, Layout_Width)
    print("Generating meshes for Image %s on height %d" % (imgfile, layerheight))
    gBlocks += GenerateBlocks(boxes, layerheight)

# Generate the map from blocks

m = vmf.ValveMap() # Create the map

m.world.skyname = "sky_day01_01" # Set the skybox

# Add blocks

for block in gBlocks:
    b = Block(Vertex(*block[0]), block[1], TEXTURE)
    m.world.children.append(b)

print("All meshes generated and added to the VMF file.")

m.write_vmf(OUTFILE)
