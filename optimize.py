from __future__ import print_function
import xy_interpolation as xy
import numpy as np
from scipy.optimize import fmin, basinhopping
from random import random
import pickle

VERSION = '1.1'

unflatten = lambda flatpts: [flatpts[:len(flatpts) // 2],  flatpts[len(flatpts) // 2:]]

class Bell():
    """
    Creates a bell curve waiting to be optimized.
    
    Attributes:
        version (str): version of code under which the bell was initialized
        thickness (float): thickness, in mm, of bell to be simulated
        target (np.array): desired eigenfrequencies of bell
        elastic (str): young's modulus in Pa and poisson's ratio, comma separated
        density (float): density of material in kg/cm^3
        scale (int, optional): the length scale of the initial random bell curve
        method (str, optional): method for optimizing curve, currently only simplex works
        grade (str, optional): either 'coarse' or 'fine', determines FEA mesh size
        ctrlpoints (int, optional): number of control points in curve, determines complexity
        c0 (list list, optional): initial curve to be optimized

    
    """
    def __init__(self, thickness, target, elastic='69000e6,0.33', density=0.002712,
                 scale=150, method='simplex', grade='fine', ctrlpoints=5, c0=None):
        self.version = VERSION
        self.thickness = thickness
        self.elastic = elastic
        self.density = density
        self.target = target
        self.scale = scale
        self.method = method
        self.grade = grade
        self.c0 = c0
        
        if self.c0 == None:
            self.ctrlpoints = ctrlpoints
            _, self.c0 = xy.make_random_shape(self.ctrlpoints, scale=self.scale, circ=True)
        else:
            self.ctrlpoints = len(self.c0[0])
        
        self.optpts = []
        self.allvecs = []
        self.fits = []
        self.fqs = []
        self.xopt = []
        self.best_fit = None
        self.best_fq = None

        
        
    def evalFitness(self, flatpts, crosspenalty=100.0*1000):
        """
        Fitness of points defining curve. Needs flattened points for use with fmin

        Args:
            flatpts (np.array): flattened points [x1,x2,...y1,y2,...] defining curve
            crosspenalty (float): value to return if curve is self-intersecting

        Returns:
            fitness (float): RSS of frequencies if valid, crosspenalty if not
        """
        assert len(flatpts) % 2 == 0
        x,y = unflatten(flatpts)
        pts = (x, y)
        n_freq = len(self.target)
        try:
            if self.grade == 'coarse':
                s = xy.make_shape(pts, max_output_len=50)
            else:
                s = xy.make_shape(pts, max_output_len=100)
            fq, _, _ = xy.find_eigenmodes(s, self.thickness, self.elastic, self.density)
            fit = xy.fitness(fq[:n_freq], self.target)
            print(fit)
            self.fits.append(fit)
            self.fqs.append(fq)
            return fit
        except ValueError as err:
            # if you give a constant value, the algorithm thinks it's finished
            print(err)
            return crosspenalty * (random()+1)


    def findOptimumCurve(self):
        """
        Uses basic downhill simplex optimization to find a curve with freqs target
    
        Returns:
            optpts (tuple): points (x,y) defining optimized curve
        """

        x, y = self.c0
        flatpts = np.append(x, y)
        if self.grade == 'coarse':
            ftol = 1.0
            xtol = 1.0
        else:
            ftol = .1
            xtol = .1
        
        if self.method == 'simplex':
            retvals = fmin(lambda pts: self.evalFitness(pts), flatpts, 
                disp=True, xtol=xtol, ftol=ftol, retall=True, maxiter=300)
       
        elif self.method == 'basinhopping':
            def test(f_new, x_new, f_old, x_old):
                c = (x_new[:len(x_new) // 2], x_new[len(x_new) // 2:])
                return not xy.curve_intersects(xy.interp(c)) # check for intersection
                # TODO - redundant - happens inside basinhopping anyways
            minimizer_kwargs = {'tol':ftol*100}
            res =  basinhopping(lambda pts: self.evalFitness(pts), flatpts, T=1,
                         accept_test=test, stepsize=20, disp=True, callback = print,
                         minimizer_kwargs=minimizer_kwargs)
            retvals = [res.x, list(res.x)]  # this is so indexing to look for xopt doesn't break
        
        else: raise ValueError("Invalid method selected")
    
        #  save the data for lata
        #  TODO - live update instead of waiting til end to write - better crash recovery
        labels = ['xopt','allvecs']
        retdict = dict(zip(labels,retvals))  # automatically ignores allvecs if absent
        retdict['fits'] = self.fits
        retdict['fqs'] = self.fqs
    
        outpts = retvals[0]
        x = outpts[:len(outpts) // 2]
        y = outpts[len(outpts) // 2:]
        self.optpts = (x, y)
        print(self.optpts)
    
        retdict['optpts'] = self.optpts # for redundancy 
        retdict['target'] = self.target
        retdict['c0'] = self.c0
        self.allvecs = retdict['allvecs']
        self.xopt = retdict['xopt']
        # TODO - this is ridiculous
    
        # isolate best case
        self.best_fit = min(self.fits)
        self.best_fq = self.fqs[self.fits.index(self.best_fit)]
        
        pickle.dump(retdict, open('vals.p','wb')) # TODO - account for overwriting
        pickle.dump(self, open('bell.b','wb'))
        return retdict



if __name__ == '__main__':
    # This is an example use case
    thick = 6.35  # choose a thickness of 1/4" (=6.35 mm)
    target_0 = np.array([.5,1,2,3,4])*440  # choose a fundamental (440 Hz) and a set of overtones
    ctrl_pts = 6 # interpolate the bell curve from 6 points
    minimum_fitness = 0.1  # this is greater than audible precision
    targets = [target_0 * 2**(n/12.0) for n in range(13)] # find look bells of that target in a chromatic scale
    
    attempts, bells = [], []  # these lists store the same information in two different ways
    for trg in targets:
        i = 0
        while i < 5:  # try a few times
            fits, fqs = [], [] # TODO - crude, fix this
            bell = Bell(thick, trg, ctrlpoints=ctrl_pts, grade='coarse') # initialize a bell
            
            retdict = bell.findOptimumCurve()  # optimize its shape
            
            attempts.append(retdict)  # add the result to `attempts`
            bells.append(bell)  # add the bell object to `bells`
            pickle.dump(attempts, open('attempts.p','wb'))  # save both to review later
            pickle.dump(bells, open('bells.p','wb'))
            i += 1
            if retdict['fits'][-1] < minimum_fitness : # good enough for now. If 
                break