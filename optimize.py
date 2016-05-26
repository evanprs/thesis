from __future__ import print_function
from xy_interpolation import *
from scipy.optimize import fmin, basinhopping
from random import random
import pickle


THICKNESS = 6.35  # 1/4 inch in mm
TARGET = np.array([.5,1,1.2,1.5,2,2.5])*440
METHOD = 'simplex' # options: simplex, basinhopping
GRADE = 'course' # options: course, fine

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
        if GRADE == 'course':
            s = make_shape(pts, max_output_len=50)
        else:
            s = make_shape(pts, max_output_len=100)
        fq, _, _ = find_eigenmodes(s, THICKNESS)
        fit = fitness(fq[:n_freq], target)
        print(fit)
        fits.append(fit)
        fqs.append(fq)
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
        _, c0 = make_random_shape(7, scale=150, circ=True)
    x, y = c0
    flatpts = np.append(x, y)
    
    if METHOD == 'simplex':
        if GRADE == 'course':
            retvals = fmin(lambda pts: evalFitness(pts, target), flatpts, 
                disp=True, xtol = 1.0, ftol=1.0, retall=True, maxiter=300)
        else:
            retvals = fmin(lambda pts: evalFitness(pts, target), flatpts, 
                disp=True, xtol = .1, ftol=.1, retall=True, maxiter=300)
    elif METHOD == 'basinhopping':
        def test(f_new, x_new, f_old, x_old):
            c = (x_new[:len(x_new) // 2], x_new[len(x_new) // 2:])
            return not curve_intersects(interp(c)) # check for intersection
            # TODO - redundant - happens inside basinhopping anyways
            
        res =  basinhopping(lambda pts: evalFitness(pts, target), flatpts, T=1,
                     accept_test= test, stepsize=200, disp=True, callback = print)
        retvals = [res.x]
    else: raise ValueError("Invalid method selected")
    
    #  save the data for lata
    #  TODO - live update instead of waiting til end to write - better crash recovery
    labels = ['xopt','allvecs']
    retdict = dict(zip(labels,retvals))  # automatically ignores allvecs if absent
    retdict['fits'] = fits
    retdict['fqs'] = fqs
    
    outpts = retvals[0]
    x = outpts[:len(outpts) // 2]
    y = outpts[len(outpts) // 2:]
    optpts = (x, y)
    print(optpts)
    
    retdict['optpts'] = optpts # for redundancy 
    retdict['target'] = target
    retdict['c0'] = c0
    
    pickle.dump(retdict, open('vals.p','wb')) # TODO - account for overwriting
    return optpts, retdict



if __name__ == '__main__':
    
    attempts = []
    targets = [TARGET * 2**(n/12.0) for n in range(13)]
    for trg in targets:
        i = 0
        while i < 5:  # try 10 times
            fits, fqs = [], [] # TODO - crude, fix this 
            optpts, retdict = findOptimumCurve(trg)
            attempts.append(retdict)
            pickle.dump(attempts, open('attempts.p','wb'))
            i += 1
    
    
