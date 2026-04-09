before running file:
pip install numpy
pip install opencv-python

to run it do:
python main_code.py

notes:
If you want to change the block size, change it BOTH at line 77, and 92, the block sized ive picked that looked the best is "5"
if you want to change the search radius, change at line 92, arguement 6 in match_blocks, currently its "6"
if you want to change the T value, change it at line 99, in check_T, input 2 is min_T and input 3 is max_T

Implementation details:

* block_grid_centers:
+ takes width, height and k as inputs, k is used to calculate size of blocks
+ calculate a grid of blocks by starting at k, incrementing by "block" until width-k or height-k using range function
+ we start and end there because a pixel at "x" creates a block stretching [x-k, x+k], so a valid block must start at k
and end at width-k or height-k to allow enough room for a block
+ after that we get a list of xs and ys, from which we can return a list of all the centers corellated to each block in grid


* extract_block:
+ given a x, y value of a pixel in a frame, calculate and return block at that pixel


* clamp:
+ if val < low, make val = low
+ if val > high, make val = high


* match_blocks:
+ y_min, y_max, x_min, x_max are the search area determined by R around the input pixel cx, cy
+ the search area is clamped so that theres still a "k" pixel gap to any border, to allow existence of a block at the edge of the search area
+ e.g. if R=5, k=3 and we're starting from x=6, the first pixel in the search is x=1, we cant make a block at 1 because 1-3=-2
+ for every pixel in search area, calculate ssd from input cx, cy to that pixel
+ while iterating, keep track of best (lowest) ssd and the x, y coordinate of the pixel with best ssd
+ return x, y of pixel with lowest ssd and the ssd value


* check_T:
+ check squareroot ssd against T values


* putting it all together:
+ run block_grid_centers once to generate block grid and get all the centers
+ firstly, read first frame and save it to variable "prev"
+ from 2nd frame onward, while theres still frames:
- "current" set to current frame
- for every block centers in the block grid, call match block on it, passing in k and search radius R (matching source block with candidate block)
- dx, dy are displacement vectors, used to draw arrow
- calculate squareroot of ssd and save it alongside the block center and displacement vector in "arrows"
- iterate through arrow, for each entry check squareroot ssd against T value, if fails dont draw arrow at that grid block center
