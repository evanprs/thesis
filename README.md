## Optimizing Bell Plates

This code provides utilities for optimizing the shape of a plate bell based on its desired overtones using the CalcuLiX FEM library. It's far from polished, but I'm leaving it as is unless anybody takes a particular interest in it.

### Requirements
Besides the standard Python scientific libraries, this package requires the CalculiX FEM library, the packages in requirements.txt, and pyaudio if you want to preview the sounds of the bells.


### Modules
#### `xy_interpolation`
Contains tools for drawing the outlines of the bells and writing them to `.dxf` format when ready to send to a waterjet cutter.
#### `optimize`
Uses `scipy.fmin` to find an optimal bell shape (`basinopping` is broken at the moment). The body of the code is one example of how to generate shapes - tweak it for your particular purpose.
#### `stats`
When run, if `stats` sees a pickled file called `vals.p` in the working directory it'll show the development of the shape over time
#### `sounds`
Allows `stats` to play the sound of the bell at each iteration.

### Usage
Use the contents of optimize.py as a jumping off point for your own projects. Default material properties are defined for 6061 aluminum, redefine them to suit your needs.

### Docker 
If desired, a Dockerfile is attached to make installing dependencies more straightforward. With Docker installed on your computer, build the image:  

    docker build -t bells .  

Once that's done, run the image. To run graphics, you'll need have a running X server on your host PC.
On Windows I use [vcxsrv](https://sourceforge.net/projects/vcxsrv) with access control disabled,
and set my DISPLAY variable to my IP address: 

    set DISPLAY=192.168.0.11:0.0

When you launch the container, be sure to export your DISPLAY variable

    docker run -it -e DISPLAY bells



### TODOs
Get multi-layer parts to actually work (combine solids in cgx)
testing
