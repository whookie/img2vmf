# img2vmf
This script allows you to generate a Source Engine Valve Map File (VMF) from a 2D Image.

**Dependencies**

- **vmflib** `pip install vmflib` or on github: https://github.com/BHSPitMonkey/vmflib
- **python3** (Tested only with Anaconda Python 3.7)
- It should run on linux, but it is only tested for **windows**.

**Usage**

[*Arguments*]

```
-i | --image      | Set the input image (If it ends in .json, it will use a set of images, see below for more information)
-o | --out        | The name as which to save the VMF file
-s | --pixelsize  | The amount of Hammer Units (1 unit = 1 inch I think) that fit the length of a pixel
-t | --thickness  | The thickness of the brushes that make up the ground
-m | --material   | The material to use on the blocks upon creation (Default 'tools/toolsnodraw')
```

[*Example*]
Using a single image:
`python img2vmt.py --image layout.jpg --out mynewmap.vmf -s 2 -t 16`
- Translates the image `layout.jpg` to a VMF file, where 2 units equal 1 pixel, and a brush height of 16 units.

`python img2vmt.py --image house.json --out mynewmap.vmf -s 2 -t 16`
- Works like the example above, but it translates multiple images on different heights.

[*How the JSON works*]

It's very simple:
```
{
  "groundfloor.jpg": 0,
  "firstfloor.jpg": 128,
  "basement.jpg": -128
}
```
You can add an infinite amount of images (just note that it will take longer with every image) as long as you don't reach the height limit (if there is one? I'm not sure)

The Format is generally `"imagename.jpg": height` where height is the offset from the 0-plane

**Note**

- As I could not find an algorithm to slice an image into boxes I thought of a custom one.
If you know of a good algorithm to slice an image into a series of boxes, please tell me!

- The one I came up with is most likely very slow and inefficient, so try to avoid using images larger than HD.

- Do not use this on existing maps, as it will overwrite your map, and not add into it!
