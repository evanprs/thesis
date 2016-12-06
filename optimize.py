from __future__ import print_function
from xy_interpolation import *
from scipy.optimize import fmin, basinhopping
from random import random
import pickle


THICKNESS = 6.35  # 1/4 inch in mm
TARGET = np.array([.5,1,1.25,1.5,2,2.5])*440
METHOD = 'simplex' # options: simplex, basinhopping
GRADE = 'fine' # options: coarse, fine

unflatten = lambda flatpts: [flatpts[:len(flatpts) // 2],  flatpts[len(flatpts) // 2:]]

class Bell():
    def __init__(self, thickness, target, method='simplex', grade='fine', ctrlpoints=5, c0=None):
        self.thickness = thickness
        self.target = target
        self.method = method
        self.grade = grade
        self.ctrlpoints = ctrlpoints
        self.c0 = None
        
        self.optpts = []
        self.allvecs = []
        self.fits = []
        self.fqs = []
        self.xopt = []
    
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
        pts = (x, y) # TODO - I can compress these two lines, right?
        n_freq = len(self.target)
        try:
            if self.grade == 'coarse':
                s = make_shape(pts, max_output_len=50)
            else:
                s = make_shape(pts, max_output_len=100)
            fq, _, _ = find_eigenmodes(s, self.thickness)
            fit = fitness(fq[:n_freq], self.target)
            print(fit)
            self.fits.append(fit)
            self.fqs.append(fq)
            return fit
        except ValueError:
            # if you give a constant value, the algorithm thinks it's finished
            # TODO - find something better
            print('Curve broke the solver')
            return crosspenalty * (random()+1)


    def findOptimumCurve(self):
        """
        Uses basic downhill simplex optimization to find a curve with freqs target
    
        Returns:
            optpts (tuple): points (x,y) defining optimized curve
        """
        if self.c0 == None:
            _, self.c0 = make_random_shape(6, scale=150, circ=True)
        x, y = self.c0
        flatpts = np.append(x, y)
    
        if self.method == 'simplex':
            if self.grade == 'coarse':
                retvals = fmin(lambda pts: self.evalFitness(pts), flatpts, 
                    disp=True, xtol = 1.0, ftol=1.0, retall=True, maxiter=300)
            else:
                retvals = fmin(lambda pts: self.evalFitness(pts), flatpts, 
                    disp=True, xtol = .1, ftol=.1, retall=True, maxiter=300)
        elif self.method == 'basinhopping':
            def test(f_new, x_new, f_old, x_old):
                c = (x_new[:len(x_new) // 2], x_new[len(x_new) // 2:])
                return not curve_intersects(interp(c)) # check for intersection
                # TODO - redundant - happens inside basinhopping anyways
            
            res =  basinhopping(lambda pts: self.evalFitness(pts), flatpts, T=1,
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
        self.optpts = (x, y)
        print(optpts)
    
        retdict['optpts'] = self.optpts # for redundancy 
        retdict['target'] = self.target
        retdict['c0'] = self.c0
        self.allvecs = retdict['allvecs']
        self.xopt = retdict['xopt']
        # TODO - this is ridiculous
    
        pickle.dump(retdict, open('vals.p','wb')) # TODO - account for overwriting
        pickle.dump(self, open('bell.b','wb'))
        return retdict



if __name__ == '__main__':
    attempts = []
    previous = pickle.load(open('chrom_todo.p'))
    targets = [a['target'] for a in previous]
    c0s = [a['optpts'] for a in previous]
    # targets = [TARGET * 2**(n/12.0) for n in range(13)]
    # targets = [ np.array([.5,1,2,3,4])*440 ]
    for trg, c0 in zip(targets, c0s):
        i = 0
        while i < 5:  # try a few times
            fits, fqs = [], [] # TODO - crude, fix this
            retdict = findOptimumCurve(trg,c0)
            attempts.append(retdict)
            pickle.dump(attempts, open('attempts.p','wb'))
            i += 1
            if retdict['fits'][-1] < 0.1 : # good enough
                break