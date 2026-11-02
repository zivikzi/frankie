"""Every number the living world uses, in one place, plainly named.

Labels: the world, the body's costs and the rendering are infrastructure, so
they may be conventional. Where a number comes from the bench it says so.
Nothing here is tuned to make any creature look good; the values were picked
once, by hand, before any batch was run.
"""

# ------------------------------------------------------------------ energy (bench numbers where they fit)

ENERGY_START = 60.0          # every creature starts at 60 (bench, section 5)
ENERGY_MAX = 100.0           # a full stomach: energy above this is wasted (world rule, conventional)
NOURISH_GAIN = 15.0          # eating a nourishing object: +15 (bench)
POISON_LOSS = -20.0          # eating a poisonous object: -20 (bench)
NOTHING_GAIN = 0.0           # eating a "nothing" object: 0 (bench)

TICK_COST = 0.04             # being alive costs this much every tick, resting included
STEP_COST = 0.04             # a step costs this much on top of the tick
CLIMB_COST_PER_M = 0.08      # walking uphill costs this much per metre climbed (downhill is free)
TURN_COST = 0.005            # turning on the spot
LOOK_COST = 0.25             # one sharp look (the bench charges for looks too)
BUMP_COST = 0.02             # walking into a fence, wall or river bank hurts a little

# ------------------------------------------------------------------ the land

WORLD_SIZE = 128.0           # metres across, square; x and z run from 0 to WORLD_SIZE
GRID = 129                   # height-map samples per side (1 m apart)
HEIGHT_MAX = 14.0            # tallest hills, in metres
NOISE_OCTAVES = 5            # smooth value-noise height map (conventional)
NOISE_BASE_CELLS = 4         # lattice cells across the map at the coarsest octave
NOISE_PERSISTENCE = 0.5      # each octave has half the amplitude of the one before

# Regions: low ground is marsh, high ground is rocky, and the middle is split
# between meadow and forest by a second noise field (conventional).
REGIONS = ("meadow", "forest", "marsh", "rocky")
MARSH_BELOW = 0.22           # share of the land, lowest first, that is marsh
ROCKY_ABOVE = 0.80           # land above this share (by height) is rocky
SCENE_MIN_GAP = 0.18         # region scene values are drawn at least this far apart (0 to 1 scale)
CONTEXT_JITTER = 0.02        # each object's scene and host wobble by up to this much

# ------------------------------------------------------------------ objects and kinds

N_PATCHES = 34               # patches of objects scattered over the land
PATCH_SIZE_LO = 3            # objects per patch, from ...
PATCH_SIZE_HI = 6            # ... to this
PATCH_RADIUS = 3.0           # objects sit within this many metres of the patch centre
REGROW_TICKS_LO = 250        # an eaten object regrows at the same spot after this many ticks ...
REGROW_TICKS_HI = 450        # ... up to this many
PRIMARY_WEIGHT = 0.70        # a kind's patches fall in its favourite region this often ...
SECONDARY_WEIGHT = 0.25      # ... in its second region this often, and anywhere else the rest of the time

# ------------------------------------------------------------------ obstacles (the problem-solving test)

OBSTACLE_WORLD_SHARE = 0.67  # this share of worlds has obstacles; the rest have none, for comparison
FENCE_RADIUS = 7.0           # a fence is a ring (polygon) of this radius around a rich food patch
FENCE_SIDES = 12             # fence segments per ring
FENCE_GAP_SIDES = 1          # one segment is left open: the gap
RICH_PATCH_SIZE = 7          # food objects inside a fenced patch or across the river
WALL_LENGTH_LO = 14.0        # solid walls are this long ...
WALL_LENGTH_HI = 26.0        # ... to this
RIVER_HALF_WIDTH = 2.2       # a river is a band this wide on each side of its centre line
FORD_HALF_WIDTH = 2.0        # the one crossing (ford or log) is this wide on each side of its centre
CREATURE_RADIUS = 0.35       # how close a creature's centre may come to a fence or wall

# ------------------------------------------------------------------ the body

STEP_LENGTH = 1.0            # metres per step
TURN_MAX_DEG = 45.0          # the most a creature can turn in one tick
EYE_HEIGHT = 0.9             # metres above the ground
VIEW_RANGE = 22.0            # the wide blurry view reaches this far ...
VIEW_HALF_ANGLE_DEG = 60.0   # ... within this angle either side of the heading
BLUR_NOISE_NW = 2.0          # blurry-view noise, in noise widths, right in front of the eyes ...
BLUR_NOISE_PER_M_NW = 0.25   # ... growing by this much per metre of distance
SHARP_RANGE = 4.0            # a sharp look reaches only objects this close
SHARP_NOISE_NW = 1.0         # a sharp look is as clear as the bench's readings (1 noise width)
TASTE_NOISE_NW = 1.0         # taste is read as the bench reads it
EAT_RANGE = 1.3              # a creature can eat an object this close to its centre
NOISE_WIDTH = 0.01           # one noise width (bench, PLACEHOLDER-45)
SIGHT_SAMPLE_M = 1.0         # hills are checked along the line of sight every metre

# ------------------------------------------------------------------ runs

MAX_TICKS = 3000             # a batch run stops here if the creature is still alive
WINDOW_TICKS = 50            # learning curves use windows of this many ticks
TRAIL_LENGTH = 400           # positions kept for the trail on screen

# ------------------------------------------------------------------ creature character (drawn at birth)

RESERVE_LO = 20.0            # reserve R drawn from 20 ... (bench M33)
RESERVE_HI = 60.0            # ... to 60
BOLDNESS_LO = 0.1            # boldness b drawn from 0.1 ... (bench M33)
BOLDNESS_HI = 0.6            # ... to 0.6
