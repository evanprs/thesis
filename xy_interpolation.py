import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from itertools import combinations
import os
import subprocess
from dxfwrite import DXFEngine as dxf

# Globals to activate debug code
SHOW_STEPS = False
SHOW_WINS = False
SHOW_FAILS = False
PLOT_SHAPE = False


def smart_mkdir(path):
    """
    Args:
        path: path of desired folder
    Returns:
        the path of the actual folder created
    """
    timestamp = '__{:%Y-%m-%d__%H:%M:%S}'.format(datetime.datetime.now())
    path = path + timestamp
    
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        copynum = 1  # to avoid duplicate names, append a number
        while os.path.exists(path + '-' + str(copynum)):
            copynum += 1
        path = path + '-' + str(copynum)
        os.makedirs(path)
    return path

def smart_syscall(call_text):
    exit_status = subprocess.call(call_text, shell=True, stdout=subprocess.PIPE)
    if exit_status != 0:
        raise IOError("System call '" + call_text + "' failed with exit status " 
                        + str(exit_status) +". Is CalculiX installed?")


def rand_points(n, scale=1):
    xp = np.random.random(n) * scale
    yp = np.random.random(n) * scale
    return xp, yp


def halve(ls):
    """ Splits a list of two sublists in half"""
    ls1 = ls[0][len(ls[0]) // 2:], (ls[1][len(ls[1]) // 2:])
    ls2 = ls[0][:len(ls[0]) // 2], (ls[1][:len(ls[1]) // 2])
    return ls1, ls2


def breakup(ls, order):
    """Breaks up ls into 2^order sublists"""
    if order == 1:  # base case
        return halve(ls)
    else:
        ls1, ls2 = halve(ls)
        return breakup(ls1, order - 1) + breakup(ls2, order - 1)


def range_intersects(rng1, rng2):
    """ rng = (xmin, xmax)"""
    return (rng1[0] <= rng2[0] <= rng1[1] or
            rng2[0] <= rng1[0] <= rng2[1] or
            rng1[0] <= rng2[1] <= rng1[1] or
            rng2[0] <= rng1[1] <= rng2[1])


def box_intersects(box1, box2):
    """ box = (xmin,xmax,ymin,ymax)"""
    return (range_intersects((box1[0], box1[1]), (box2[0], box2[1])) and
            range_intersects((box1[2], box1[3]), (box2[2], box2[3])))


def curve_intersects_rec(c1, c2, thresh):
    if len(c1[0]) <= thresh:  # base case
        return True
    # construct bounding boxes
    box1 = (np.min(c1[0]), np.max(c1[0]), np.min(c1[1]), np.max(c1[1]))
    box2 = (np.min(c2[0]), np.max(c2[0]), np.min(c2[1]), np.max(c2[1]))

    if SHOW_STEPS:
        plt.figure()
        plt.axis((-1, 2, -1, 2))
        plt.plot(c1[0], c1[1], c2[0], c2[1])
        plt.title(str(box_intersects(box1, box2)) + ' size =' + str(len(c1[0])))
        plt.show()

    if box_intersects(box1, box2):  # split the curves in half, recurse
        c1a, c1b = halve(c1)
        c2a, c2b = halve(c2)
        return (curve_intersects_rec(c1a, c2a, thresh) or
                curve_intersects_rec(c1a, c2b, thresh) or
                curve_intersects_rec(c1b, c2a, thresh) or
                curve_intersects_rec(c1b, c2b, thresh))
    else:
        return False


def curve_intersects(c, thresh=100):
    """ Takes as input two curves c1 = [x,y]
    Returns True if c1 and c2 intersect. 
    Works by recursing on bounding boxes.
    Thanks to the lovely Pomax for the method."""
    assert len(c[0]) == len(c[1])
    assert len(c[0]) > thresh*4  # it'll give true by default if you start with a small list

    # Hacky fix - some self-intersections get lost if you don't break it up enough
    cs = breakup(c, 3)
    c_pairs = combinations(cs, r=2)  # try each combination

    if SHOW_FAILS:
        plt.figure()
        plt.axis((-0.5, 1.5, -0.5, 1.5))
        for curve in cs:
            plt.plot(curve[0], curve[1], thresh)
        plt.show()

    for pair in c_pairs:
        if curve_intersects_rec(pair[0], pair[1], thresh):
            return True

    if SHOW_WINS:
        plt.figure()
        for curve in cs:
            plt.plot(curve[0], curve[1])
        plt.show()

    return False


def interp(points, n=2000):
    """Takes as input list points = (x,y)
    returns a list [xnew,ynew] of interpolated points of length n.
    n only matters for curve_intersects, n=2000 seems to work."""
    tck, u = interpolate.splprep(points, s=0, per=True)
    unew = np.linspace(0, 1, n)
    xnew, ynew = interpolate.splev(unew, tck)
    xnew = np.delete(xnew, 0)  # need to remove duplicate points
    ynew = np.delete(ynew, 0)
    return xnew, ynew


def bevel(curve, radius):
    """
    Imposes a minimum radius on a 2D curve.

    Args:
        curve (tuple): (x,y) points
        radius (int): the desired minimum radius

    Returns:
        beveled (tuple): (x,y) points with min radius
        """
    import pyclipper
    scale = 10000
    radius *= scale
    transposed = pyclipper.scale_to_clipper(list(zip(*curve)), scale=scale)

    pco = pyclipper.PyclipperOffset()
    pco.AddPath(transposed, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    inset = pco.Execute(-radius)[0]

    pco2 = pyclipper.PyclipperOffset()
    pco2.AddPath(inset, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    solution = pco2.Execute(radius)[0]
    # solution.pop(0) # TODO: decide if necessary

    beveled = pyclipper.scale_from_clipper(list(zip(*solution)), scale=scale)
    return beveled

def make_circle(r, center=(0,0), n=50):
    """ 
    Args:
        r (float): radius
        center (float,float): (x,y) center point
        n (int): number of points to draw

    Returns:
        the pair of interpolated points (x,y)

    """   
    theta = np.linspace(0, 2*np.pi, n, endpoint=False)
    x = r * np.cos(theta) + center[0]
    y = r * np.sin(theta) + center[1]
    return x,y
    
def make_moon(r, phase, center=(0,0), n=50):
    """ 
    Returns the outline points of a crescent moon
    Args:
        r (float): radius
        phase (float): fractional moon phase (0,1], 1=full
        center (float,float): (x,y) center point
        n (int): number of points to draw

    Returns:
        curve: the pair of interpolated points (x,y)

    """
    assert 0 < phase <= 1    
    n0 = 3000 # start with a bunch, resample later

    theta = np.linspace(np.pi/2, np.pi*3/2, n0//2, endpoint=False)
    xc = r * np.cos(theta) + center[0]
    yc = r * np.sin(theta) + center[1]
    
    theta = np.linspace(np.pi*3/2, np.pi*5/2, n0//2, endpoint=False)
    xe = r * (2 * phase - 1)  * np.cos(theta) + center[0]
    ye = r * np.sin(theta) + center[1]
    
    x = np.concatenate((xc,xe))
    y = np.concatenate((yc,ye))
    curve = (x,y)

    # soften edges
    curve = bevel(curve, 1)
    # TODO - bevel returns [(x,y)..], so no need to retranspose

    # resample
    pts = tuple(map(lambda x: np.append(x, x[0]), curve))
    curve = interp(pts, n=n)

    return curve

    
def make_shape(pts, max_output_len=100):
    """ 
    Args:
        pts: a tuple of points (x,y) to be interpolated
        max_output_len: the max number of points in the interpolated curve

    Returns:
        the pair of interpolated points (xnew,ynew)
    
    Raises:
        ValueError: pts defined a self-intersecting curve
    """
    assert len(pts[0]) == len(pts[1])
    pts = tuple(map(lambda x: np.append(x, x[0]), pts))
    fit_pts = interp(pts)
    if curve_intersects(fit_pts):
        raise ValueError("Curve is self-intersecting")

    if PLOT_SHAPE:
        plt.figure()
        plt.plot(pts[0],pts[1], 'x')
        plt.plot(fit_pts[0],fit_pts[1])
        plt.axes().set_aspect('equal', 'datalim')
        plt.show()
    
    
    sparse_pts = tuple(map(lambda ls: ls[::len(fit_pts[0]) // max_output_len + 1], fit_pts))
    return sparse_pts


def make_random_shape(n_pts, max_output_len=100, scale=500, circ=False):
    """ Interpolate a random shape out of n_pts starting points.
    Starts to take way too long for n_pts > 9
    
    Args:
        n_pts: number of points from which to interpolate the curve
        max_output_len: the max number of points in the interpolated curve
        scale: the range [0,scale] in which to randomly generate points
        circ: if True, shape will be roughly circular
        
    Returns:
        fit_pts: a tuple (x,y) of the interpolated curve points
        pts: a tuple (x,y) of the points used to make the curve
    """
    valid_shape = False
    failcounter = 0
    while not valid_shape:
        try:
            if circ:
                thetas = rand_points(n_pts, scale=2*np.pi)[0]
                thetas.sort()
                rs = rand_points(n_pts, scale=scale/2)[0]+scale/2
                xs = rs * np.cos(thetas)
                ys = rs * np.sin(thetas)
                pts = xs,ys
                fit_pts = make_shape(pts,max_output_len)       
            else:
                pts = rand_points(n_pts, scale)
                fit_pts = make_shape(pts, max_output_len)
            valid_shape = True
            return fit_pts, pts
        except ValueError:
            failcounter += 1


def curves_to_fbd(curves, fbd_filepath):
    """
    Converts a set of (x,y) points to a .fbd file.
    WARNING - will ruin things downstream if you give it a bad curve
    
    Args:
        curves [(curve, thick), ...]: list of curves and thicknesses, bottom to top
            curve: the (x,y) points to be converted. Do not duplicate endpoints
            thick: the thickness of the desired solid
        fbd_filepath: path to output file
    """
    BIAS = '' # null until I figure out why this is here
    with open(fbd_filepath, 'w') as fbdfile:
        N = 0 # keep track of points so far for labeling purposes
        net_thick = 0
        for curve, thick in curves:
            assert len(curve[0]) == len(curve[1])
            n_pts = len(curve[0])

            # build points
            for i in range(n_pts):
                fbdfile.write(f'pnt p{i+N} {curve[0][i]}  {curve[1][i]} {net_thick}\n')

            # build lines
            for i in range(n_pts):
                fbdfile.write(f'line l{i+N} p{i+N} p{(i+1)%n_pts+N} {BIAS}\n')

            # combine all but the first 2 of the lines into one
            fbdfile.write(f'lcmb U{N} + l{N+2}\n')
            for i in range(3+N, n_pts+N):
                fbdfile.write(f'lcmb U{N} ADD - l{i}\n')

            # try and make a surface from it?
            fbdfile.write(f'gsur s{N} + BLEND + U{N} + l{N} + l{N+1}\n')

            # put everything so far into set 'botpts'
            fbdfile.write(f'seta botpts{N} s{N}\n')
            # fbdfile.write(f'comp botpts{N} d\n')

            # translate everything up by the thickness
            fbdfile.write(f'swep botpts{N} toppts{N} tra 0 0 {thick}\n')

            N += n_pts + 1
            net_thick += thick

        fbdfile.write('merge n all\n')

        # do something the developer suggested
        fbdfile.write('div all 2\n')

        # mesh using tetrahedrons, write mesh to file, and quit
        fbdfile.write('elty all te10\n')
        fbdfile.write('mesh all \n')
        fbdfile.write('send all abq \n')
        fbdfile.write('quit \n')


# TODO - check a model against solidworks to make sure this works
# This code provides the input parameters to run the simulation
# Units:  Temp(K), Length(MM), Force(N), Density(10**3*KG/MM**3)

def pts_to_dxf(pts, name='test.dxf'):
    """
    Takes a set of (x,y) points, interpolates the curve, then writes to dxf.
    
    Args:
        curve: the (x,y) points to be converted. Do not duplicate endpoints
        name: filename of output
    """
    curve = make_shape(pts, max_output_len=300)
    assert len(curve[0]) == len(curve[1])
    cpts = list(zip(*curve))
    cpts.append(cpts[0]) # duplicate endpoints
    n_pts = len(cpts)
    drawing = dxf.drawing(name)
    drawing.add_layer('LINES')
    # build points
    i = 0
    while i < n_pts-1:
        drawing.add(dxf.line(cpts[i], cpts[i+1], color=7, layer='LINES'))
        i += 1
    drawing.save()



def make_inp(elastic='69000e6,0.33', density=0.002712, freqs=14, name='test'):
    """ Creates a .inp file for cgx which sets material parameters.
    Defaults chosen for 6061 Al.
    
    Arguments:
        elastic (str): young's modulus in Pa and poisson's ratio, comma separated
        freqs (int): number of eigenfrequencies to calculate
        density (float): density of material in kg/cm^3
        name (str): .inp filename
    """
    
    inptext = '''
    *include, input=all.msh
    *MATERIAL,NAME=Al
    *ELASTIC
    {}
    *DENSITY
    {}
    *SOLID SECTION,ELSET=Eall,MATERIAL=Al
    *STEP, PERTURBATION 
    *FREQUENCY
    {}
    *NODE PRINT,FREQUENCY=0
    *EL PRINT,FREQUENCY=0
    *NODE FILE
    U
    *EL FILE
    S
    *END STEP'''.format(elastic, density, freqs)
    
    with open('./' + name + '.inp', 'w') as inpfile:
        inpfile.write(inptext)


def parse_dat(path):
    '''
    Args:
        path: path to dat file
    
    Returns:
        a list of tuples [(fq,pf,mm),...]
            fq (int): frequency of eigenmode
            pf (tuple): participation factors (x,y,z,x_rot,y_rot,z_rot)
            mm (tuple): effective modal mass (x,y,z,x_rot,y_rot,z_rot)
            '''
    raw_freq = []
    raw_part = []
    raw_modm = []
    with open(path, 'r') as datfile:
        # get frequencies
        for i in range(7):
            datfile.readline()
        for line in datfile:
            if line == '\n': break
            raw_freq.append((line.strip().split('  ')))

        # get participation factors
        for i in range(4):
            datfile.readline()
        for line in datfile:
            if line == '\n': break
            raw_part.append((line.strip().split('  ')))

        # get effective modal masses
        for i in range(4):
            datfile.readline()
        for line in datfile:
            if line == '\n': break
            raw_modm.append((line.strip().split('  ')))

    # convert strings to floats
    fq = list(map(float, [rf[3] for rf in raw_freq]))  # only get Hz
    pf = list(map(float, [num for num in pftxt[1:]]) for pftxt in raw_part)
    mm = list(map(float, [num for num in pftxt[1:]]) for pftxt in raw_part)

    return (fq, pf, mm)


def find_eigenmodes(curves, elastic, density, showshape=False, name='test', savedata=False):
    '''
    Use the cgx/ccx FEM solver to find the eigenmodes of a plate
    Units of curve and thickness are in mm
    
    Args:
        curves [(curve, thick), ...]: list of curves and thicknesses, bottom to top
            curve: the (x,y) points to be converted. Do not duplicate endpoints
            thick: the thickness of the desired solid
        showshape (bool): if True, cgx will show the deformed result
        name (string): name of the folder to be created
    Returns:
        fq (list): eigenfrequencies
        pf (list): participation factors (x,y,z,x_rot,y_rot,z_rot)
        mm (list): effective modal mass (x,y,z,x_rot,y_rot,z_rot)
    '''
    # we want to test if ccx/cgx will work before beginning, so call them now to test
    smart_syscall('cgx')
    
    totalSuccess = False
    home = os.getcwd()
    while not totalSuccess:
        os.chdir('/tmp')
        folder_path = smart_mkdir(name)
        os.chdir(folder_path)
        make_inp(elastic, density, freqs=106)
        with open(name + '.curve','w') as curvefile:
            curvefile.write(str(curves))
        curves_to_fbd(curves, name + '.fbd')
        os.system('cgx -b -bg ' + name + '.fbd >> test.log 2> error.log')
        if showshape:
            os.system('ccx ' + name + ' >> test.log  2> error.log; cgx ' + name + '.frd ' + name + '.inp >> test.log  2> error.log')
        else:
            os.system('ccx ' + name + ' >> test.log')

        try: # TODO - tweak the intersection criteria so that this happens less
            data = parse_dat(name + '.dat')
            totalSuccess = True
        except StopIteration:
            os.chdir('..')
            if not savedata:
                os.system('rm -r '+folder_path) #BE VERY CAREFUL
            print(folder_path)
            raise ValueError('Curve did not create a valid object')
        try:
            os.remove(name+'.frd') # this takes up too much space and can be reproduced later if necessary
        except FileNotFoundError:
            print(f"didn't find {name}.frd in {folder_path}")
        if not savedata:
            os.chdir('/tmp')
            os.system('rm -r '+folder_path) 
        
    os.chdir(home) 
    fq, pf, mm = [d[6:] for d in data]  # ignore the trivial
    return fq, pf, mm


# TODO - improve this criteria to include prominence of harmonics
def fitness(fq_ideal, fq_actual):
    """
    General fitness criteria. Defined here since different applications handle
    the data differently
    """
    try:
        assert len(fq_ideal) == len(fq_actual)  # just in case
    except TypeError:
        print(fq_actual)
        print(fq_ideal)
        print(type(fq_actual))
        print(type(fq_ideal))
    fq_id = np.array(fq_ideal)
    fq_ac = np.array(fq_actual)
    return np.mean((fq_id - fq_ac)**2 / fq_id)  # chi square 


def find_frequencies(fq_curr, fq_trgt):
    """
    Takes full range of frequncies found, identifies the subset of frequencies
    that correspond to the range of target frequencies. This set is bounded by
    the number of target frequencies. When smaller it will force a larger set,
    and when larger it will generate a subset of the subset.

    Args:
        fq_curr: full list of simulated frequency content
        fq_trgt: set of target frequencies
    
    Returns:
        fq: list of frequencies most likely to compare to target frequencies
    """

    fq_min = fq_trgt[0]
    fq_max = fq_trgt[-1]
    fq_num = len(fq_trgt)
    fq_tol = 10  # Tolerance in Hz
    fq_tot = 0  # Internally track length of our array

    # Isoldate all potential frequencies in our window
    fq_out = []  # We know the max lenght, so it'd probably be best to fully allocate space to it right now
    for fq in fq_curr:
        # Case A: Frequencies within our range
        if ( ( fq > (fq_min - fq_tol)) and (fq < (fq_max + fq_tol)) ):
            fq_out.append(fq)
            fq_tot += 1
        # Case B: Frequencies beyond our range, but when we haven't collected enough
        elif ( (fq_tot < fq_num ) and ( fq > (fq_max + fq_tol) ) ):
            fq_out.append(fq)
        # Case C: Frequencies beyond our range, and when we're done
        elif ( fq > (fq_max + fq_tol) ):
            break
    
    # Isolate to "most likely" freuqncies
    fq_i = np.ceil(np.linspace(0, len(fq_out), fq_num, endpoint=False))  # Indicies
    fq_out = np.asarray(fq_out)
    
    return fq_out[fq_i.astype(int).tolist()].tolist()  # Using numpy for easy indexing


if __name__ == "__main__":
    moon = make_moon(100,.9)
    moon2 = make_moon(100,.15)
    # fq, pf, mm = find_eigenmodes([(moon, 3)], elastic='69000e6,0.33', density=0.002712, showshape=True, savedata=True)
    fq, pf, mm = find_eigenmodes([(moon, 3),(moon2, 2)], elastic='69000e6,0.33', density=0.002712, showshape=True, savedata=True)
    plt.figure()
    plt.plot(fq)
    plt.show()

