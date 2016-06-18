## Optimizing Bell Plates

This code provides utilities for optimizing the shape of a plate bell based on its desired overtones using the CalcuLiX FEM library. It's far from polished, but I'm leaving it as is unless anybody takes a particular interest in it.

###Requirements
Besides the standard Python scientific libraries, this package requires the CalculiX FEM library and pyaudio if you want to preview the sounds of the bells. I've tested it on `cgx` 2.9, but it should work with 2.10 as well.

### Modules
#### `xy_interpolation`
Contains tools for drawing the outlines of the bells and writing them to `.dxf` format when ready to send to a waterjet cutter.
#### `optimize`
Uses `scipy.fmin` to find an optimal bell shape (`basinopping` is broken at the moment). The body of the code is one example of how to generate shapes - tweak it for your particular purpose.
####`stats`
When run, if `stats` sees a pickled file called `vals.p` in the working directory it'll show the development of the shape over time
####`sounds`
Allows `stats` to play the sound of the bell at each iteration.

### Usage
Right now the code is set up to simulate 1/4" 6061 aluminum plates, so if you want to use some other material you'll have to change the `inptext` file in `xy_interpolation`. Choose a list of target overtones (in Hz) and a thickness of plate (in mm), then use `optimize.findOptimumCurve(target)` to generate a bell which makes that shape. If you want better accuracy, it's a good idea to use the `optpts` from that result as a starting condition `c0` with grade set to `'fine'`, which will just continue the simulation with a higher mesh density. Finally, use `pts_to_dxf(optpts)` to generate a `.dxf` file that outputs the curve to vector format so that a waterjet place can cut it out for you.



