from __future__ import print_function
from xy_interpolation import *
from scipy.optimize import fmin
from random import random
import pickle


THICKNESS = 6.35/2  # 1/4 inch in mm
TARGET = np.array([0.22,0.44,0.528,0.66,0.88,1.1])*1000

def evalFitness(flatpts, target, crosspenalty=100.0*1000):
    """
    Fitness of points defining curve. Needs flattened points for use with fmin

    Args:
        flatpts (np.array): flattened points [x1,x2,...y1,y2,...] defining curve
        target (np.array): desired eigenfrequencies
        crosspenalty (float): value to return if curve is self-intersecting

    Returns:
        fitness (float): RSS of frequencies if valid, crosspenalty if not
    """
    assert len(flatpts) % 2 == 0
    x = flatpts[:len(flatpts) // 2]
    y = flatpts[len(flatpts) // 2:]
    pts = (x, y)
    n_freq = len(target)
    try:
        s = make_shape(pts, max_output_len=50)
        fq, _, _ = find_eigenmodes(s, THICKNESS)
        fit = fitness(fq[:n_freq], target)
        print(fit)
        fits.append(fit)
        return fit
    except ValueError:
        # if you give a constant value, the algorithm thinks it's finished
        # TODO - find something better
        print('Curve broke the solver')
        return crosspenalty * (random()+1)


def findOptimumCurve(target, c0=None):
    """
    Uses basic downhill simplex optimization to find a curve with freqs target
    
    Args:
        target (np.array): desired eigenfrequencies
        c0 (tuple): points (x,y) defining curve of initial test shape
    Returns:
        optpts (tuple): points (x,y) defining optimized curve
    """
    if c0 == None:
        _, c0 = make_random_shape(10, scale=150, circ=True)
    x, y = c0
    flatpts = np.append(x, y)
    
    retvals = fmin(lambda pts: evalFitness(pts, target), flatpts, disp=True,
                     ftol=0.1, callback = print, retall=True)
    retvals = list(retvals) # want want to append the fitness values
    
    retvals.append(fits)
    pickle.dump(retvals, open('vals.p','wb')) # TODO - account for overwriting
    
    outpts = retvals[0]
    x = outpts[:len(outpts) // 2]
    y = outpts[len(outpts) // 2:]
    optpts = (x, y)
    return optpts



if __name__ == '__main__':
    fits = [] # TODO - crude, fix this 
    optpts = findOptimumCurve(TARGET)
    print(optpts)
    # curve = make_shape(optpts, max_output_len=50)
    # print(find_eigenmodes(curve, THICKNESS, showshape=True)[0])