import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from itertools import combinations
import os
from time import sleep


def smart_mkdir(path):
    """
    Args:
        path: path of desired folder
    Returns:
        the path of the actual folder created
    """
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        copynum = 1  # to avoid duplicate names, append a number
        while os.path.exists(path + '-' + str(copynum)):
            copynum += 1
        path = path + '-' + str(copynum)
        os.makedirs(path)
    return path




def randpoints(n, scale=1):
    xp = np.random.random(n) * scale
    yp = np.random.random(n) * scale
    return xp, yp

def randthetas(n): # Not used at the moment
    """ Ensures that we cover the whole range."""
    thetas = randpoints(n, scale=2*np.pi)
    thetas[0] = 0
    thetas[-1] = 2*np.pi
    return thetas


def halve(ls):
    """ Splits a list of two sublists in half"""
    ls1 = ls[0][len(ls[0])//2:] ,(ls[1][len(ls[1])//2:])
    ls2 = ls[0][:len(ls[0])//2] ,(ls[1][:len(ls[1])//2])
    return ls1,ls2

def breakup(ls,order):
    """Breaks up ls into 2^order sublists"""
    if order == 1: # base case
        return halve(ls)
    else:
        ls1, ls2 = halve(ls)
        return breakup(ls1,order-1) + breakup(ls2,order-1)

def range_intersects(rng1,rng2):
    """ rng = (xmin, xmax)"""
    return (rng1[0] <= rng2[0] <= rng1[1] or 
            rng2[0] <= rng1[0] <= rng2[1] or
            rng1[0] <= rng2[1] <= rng1[1] or
            rng2[0] <= rng1[1] <= rng2[1])    
    
def box_intersects(box1,box2):
    """ box = (xmin,xmax,ymin,ymax)"""
    return (range_intersects((box1[0],box1[1]),(box2[0],box2[1])) and
            range_intersects((box1[2],box1[3]),(box2[2],box2[3]))  )

def curve_intersects_rec(c1,c2, thresh):
    if len(c1[0]) <= thresh: # base case
        return True
    # construct bounding boxes
    box1 = (np.min(c1[0]),np.max(c1[0]),np.min(c1[1]),np.max(c1[1]))
    box2 = (np.min(c2[0]),np.max(c2[0]),np.min(c2[1]),np.max(c2[1]))
    
    if SHOW_STEPS:
        plt.figure()
        plt.axis((-1,2,-1,2))
        plt.plot(c1[0],c1[1],c2[0],c2[1])
        plt.title(str(box_intersects(box1,box2)) + ' size =' + str(len(c1[0])))
        plt.show()
    
    if box_intersects(box1,box2): #split the curves in half, recurse
        c1a, c1b = halve(c1)
        c2a, c2b = halve(c2)
        return (curve_intersects_rec(c1a,c2a,thresh) or 
                curve_intersects_rec(c1a,c2b,thresh) or
                curve_intersects_rec(c1b,c2a,thresh) or
                curve_intersects_rec(c1b,c2b,thresh) )
    else:
        return False

def curve_intersects(c, thresh = 100):
    """ Takes as input two curves c1 = [x,y]
    Returns True if c1 and c2 intersect. 
    Works by recursing on bounding boxes.
    Thanks to the lovely Pomax for the method."""
    assert len(c[0]) == len(c[1])
    assert len(c[0]) > 10 # it'll give true by default if you start with a small list

    # Hacky fix - some self-intersections get lost if you don't break it up enough
    cs = breakup(c,3)
    c_pairs = combinations(cs,r=2) # try each combination

    if SHOW_FAILS:
        plt.figure()
        plt.axis((-0.5,1.5,-0.5,1.5))
        for curve in cs:
            plt.plot(curve[0],curve[1], thresh)
        plt.show()
    
    for pair in c_pairs:
        if curve_intersects_rec(pair[0],pair[1], thresh):
            return True
       
    if SHOW_WINS:
        plt.figure()
        for curve in cs:
            plt.plot(curve[0],curve[1])
        plt.show()

    return False

def interp(points, n = 2000):
    """Takes as input list points = (x,y)
    returns a list [xnew,ynew] of interpolated points of length n.
    n is only matters for curve_intersects, n=2000 seems to work."""
    tck, u = interpolate.splprep(points, s=0, per=True)
    unew = np.linspace(0,1,n)
    xnew,ynew = interpolate.splev(unew, tck)
    xnew = np.delete(xnew,0) # need to remove duplicate points
    ynew = np.delete(ynew,0)
    return xnew,ynew


def make_shape(pts, max_output_len = 100):
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
    pts = tuple(map(lambda x: np.append(x,x[0]), pts))
    fit_pts = interp(pts)
    if curve_intersects(fit_pts):
        raise ValueError("Curve is self-intersecting")
    sparse_pts = tuple(map(lambda ls:ls[::len(fit_pts[0])//max_output_len + 1], fit_pts))
    return sparse_pts

def make_random_shape(n_pts, max_output_len = 100, scale=500):
    """ Interpolate a random shape out of n_pts starting points.
    Starts to take way too long for n_pts > 9
    
    Args:
        n_pts: number of points from which to interpolate the curve
        max_output_len: the max number of points in the interpolated curve
        scale: the range [0,scale] in which to randomly generate points
        
    Returns:
        fit_pts: a tuple (x,y) of the interpolated curve points
        rand_pts: a tuple (x,y) of the points used to make the curve
    """
    valid_shape = False
    failcounter = 0
    while not valid_shape:
        try:
            rand_pts = randpoints(n_pts, scale)
            fit_pts = make_shape(rand_pts, max_output_len)
            valid_shape = True
             #print(str(failcounter) + ' fails')
            return fit_pts, rand_pts
        except ValueError:
            failcounter += 1




def curve_to_fbd(curve, thick, fbd_filepath):
    """
    Converts a set of (x,y) points to a .fbd file.
    WARNING - will overwrite old files
    WARNING - will ruin things downstream if you give it a bad curve
    
    Args:
        curve: the (x,y) points to be converted. Do not duplicate endpoints
        thick: the thickness of the desired solid
        fbd_filepath: path to output file
    """
    BIAS = 4
    assert len(curve[0]) == len(curve[1])
    n_pts = len(curve[0])
    with open(fbd_filepath,'w') as fbdfile:
        # build points
        i = 0
        while i < n_pts: 
            fbdfile.write('pnt p'+str(i)+' '+str(curve[0][i])+' '+str(curve[1][i])+' 0\n')
            i += 1
        
        # build lines
        i = 0
        while i < n_pts :  
            fbdfile.write('line l'+str(i)+' p'+str(i)+' p'+str((i+1)%n_pts)+' '+str(BIAS)+'\n')
            i += 1
        
        # combine all but the first 2 of the lines into one
        fbdfile.write('lcmb U0 + l2\n')
        i = 3
        while i < n_pts:
            fbdfile.write('lcmb U0 ADD - l'+str(i)+'\n')
            i += 1

        # try and make a surface from it?
        fbdfile.write('gsur s1 + BLEND + U0 + l0 + l1\n' )
        
        # put everything so far into set 'botpts'
        fbdfile.write('seta botpts se all\n') 
        
        # translate everything up by the thickness
        fbdfile.write('swep all toppts tra 0 0 '+str(thick)+' \n')
        
        # do something the developer suggested
        fbdfile.write('div all 2'+ ' \n')
        
        # mesh using tetrahedrons, write mesh to file, and quit
        fbdfile.write('elty all te10\n')
        fbdfile.write('mesh all \n')
        fbdfile.write('send all abq \n')
        fbdfile.write('quit \n')



# TODO - check a model against solidworks to make sure this works
# This code provides the input parameters to run the simulation
# Units:  Temp(K), Length(MM), Force(N), Density(10**3*KG/MM**3)

inptext = '''
*include, input=all.msh
*MATERIAL,NAME=Al
*ELASTIC
69000e6,0.3
*DENSITY
2700
*SOLID SECTION,ELSET=Eall,MATERIAL=Al
*STEP, PERTURBATION 
*FREQUENCY
20
*NODE PRINT,FREQUENCY=0
*EL PRINT,FREQUENCY=0
*NODE FILE
U
*EL FILE
S
*END STEP'''

def make_inp(name='test'):
    with open('./'+name+'.inp','w') as inpfile:
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
    with open(path,'r') as datfile:
        # get frequencies
        for i in range(7):
            datfile.next()
        for line in datfile:
            if line == '\n': break
            raw_freq.append((line.strip().split('  ')))
            
        # get participation factors
        for i in range(4):
            datfile.next()
        for line in datfile:
            if line == '\n': break
            raw_part.append((line.strip().split('  ')))
            
        # get effective modal masses
        for i in range(4):
            datfile.next()
        for line in datfile:
            if line == '\n': break
            raw_modm.append((line.strip().split('  ')))
            
    # convert strings to floats
    fq = map(float, [rf[3] for rf in raw_freq]) # only get Hz
    pf = [map(float, [num for num in pftxt[1:]]) for pftxt in raw_part]
    mm = [map(float, [num for num in pftxt[1:]]) for pftxt in raw_part]
    
    return (fq,pf,mm)

def find_eigenmodes(curve, thickness, showshape=False, name='test'):
    '''
    Use the cgx/ccx FEM solver to find the eigenmodes of a plate
    Units of curve and thickness are in mm
    
    Args:
        curve (tuple): the points (x,y) of the curve, don't duplicate endpoint
        thickness (float): the thickness of the desired plate
        showshape (bool): if True, cgx will show the deformed result
        name (string): name of the folder to be created
    Returns:
        fq (list): eigenfrequencies
        pf (list): participation factors (x,y,z,x_rot,y_rot,z_rot)
        mm (list): effective modal mass (x,y,z,x_rot,y_rot,z_rot)

    '''
    totalSuccess = False
    while not totalSuccess:
        folder_path = smart_mkdir('./'+name+'')
        os.chdir(folder_path)
        make_inp()
        curve_to_fbd(curve, thickness, './'+name+'.fbd')
        os.system('cgx -b '+name+'.fbd')
        if showshape:
            os.system('ccx '+name+' ; cgx '+name+'.frd '+name+'.inp')
        else:
            os.system('ccx '+name)

        foundfile = False
        failcounter = 0
        while not foundfile:
            try:    
                data = parse_dat(name+'.dat')
                foundfile = True
                totalSuccess = True
            except:  #TODO: check the type of error
                failcounter += 1
                sleep(.1) # wait for ccx to finish
            if failcounter > 10:  # should not take this long
                print('failed on',os.getcwd())
                break
        os.chdir('..')
    
    
    fq, pf, mm = [d[6:] for d in data] # ignore the trivial
    return fq, pf, mm



# TODO - improve this criteria to include prominence of harmonics
def fitness(fq_ideal,fq_actual):
    assert len(fq_ideal) == len(fq_actual)  # just in case
    fq_id = np.array(fq_ideal)
    fq_ac = np.array(fq_actual)
    return(sum((fq_id-fq_ac)**2))




SHOW_STEPS = False
SHOW_WINS = False
SHOW_FAILS = False


if __name__ == "__main__":
    s, r = make_random_shape(8, max_output_len = 50, scale=100)
    fq, pf, mm = find_eigenmodes(s,5)
    plt.figure()
    plt.plot(fq)
    plt.show()



