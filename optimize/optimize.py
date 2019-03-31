from __future__ import print_function
import xy_interpolation as xy
import numpy as np
from scipy.optimize import fmin, basinhopping
from random import random
import pickle

from thesis_bud import app

VERSION = '1.2'

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
    def __init__(self, target, thickness=6.35, elastic='69000e6,0.33', density=0.002712,
                 scale=150, method='simplex', grade='fine', ctrlpoints=5, c0=None):
        self.version = VERSION
        self.target = target
        self.thickness = thickness
        self.elastic = elastic
        self.density = density
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
        self.best_fit = None
        self.best_fq = None

        
        
    def evalFitness(self, flatpts, crosspenalty=100.0*1000, single_sim=False, num_freqs_to_sim=36):
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

            # If ng_vol had a memory error, fq will be empty
            while True:
                fq, _, _ = xy.find_eigenmodes([(s, self.thickness)], self.elastic, self.density, num_freqs_to_sim=num_freqs_to_sim)
                break
                # t_c = 0
                # if ( len(fq) > 0 ):
                #     if (t_c > 1):
                #         print(f"attempts at a shape: {t_c}")
                #     break
                # else:
                #     # Attempt to force a self-intersection
                #     # NOTE: This might be best in another try/catch block
                #     print("Curve did not create a valid mesh")
                #     t_c += 1

                #     s0 = s[0]
                #     s1 = s[1]
                #     s0 = np.random.shuffle(s0)
                #     s1 = np.random.shuffle(s1)
                #     s_pts = (s0, s1)
                    
                #     if self.grade == 'coarse':
                #         s = xy.make_shape(s_pts, max_output_len=50)
                #     else:
                #         s = xy.make_shape(s_pts, max_output_len=100)
            fq_nr = xy.find_frequencies(fq, self.target)
            fit = xy.fitness(fq_nr[:n_freq], self.target)
            xy.print_fitness_vals(fq_nr, self.target, fit)
            print(fit)
            app.logger.critical(fit)
            print("@shape: ", end="")
            print(pts)
            print("\n\n")
            self.fits.append(fit)
            self.fqs.append(fq)
            if single_sim:
                return fit, fq
            else:
                return fit
        # Don't do that weird thing, just throw the other catches down here!
        #   (that's kinda the point of this crosspenalty)
        except ValueError as err:
            # if you give a constant value, the algorithm thinks it's finished
            print(err)
            return crosspenalty * (random()+1)
        except FileNotFoundError as err:
            print(err)
            return crosspenalty * (random()+1)
        except AssertionError as err:
            print(err)
            return crosspenalty * (random()+1)
        except TypeError as err:
            print(err)
            return crosspenalty * (random()+1)


    def singleSimulation(self, num_freqs_to_sim=50):
        x, y = self.c0
        flatpts = np.append(x, y)
        if self.grade == 'coarse':
            ftol = 1.0
            xtol = 1.0
        else:
            ftol = .1
            xtol = .1

        fit, freqs = self.evalFitness(flatpts, single_sim=True, num_freqs_to_sim=num_freqs_to_sim)

        res = {
            'fit': fit,
            'frequencies': freqs
        }

        return res

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
                disp=True, xtol=xtol, ftol=ftol, retall=True, maxiter=10)  # Max Iter @ 10 to provide "quick" feedback
       
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
        # TODO - this is ridiculous
    
        # isolate best case
        self.best_fit = min(self.fits)
        self.best_fq = self.fqs[self.fits.index(self.best_fit)]
        
        pickle.dump(retdict, open('vals.p','wb')) # TODO - account for overwriting
        pickle.dump(self, open('bell.b','wb'))
        return retdict
    
    def refine(self):
        if self.grade == 'coarse':
            self.grade = 'fine'
            c0_initial= self.c0  # save for reference
            self.c0 = self.optpts  # start from the best
            retdict = self.findOptimumCurve()
            self.c0 = c0_initial
            return retdict
               
        
    def show(self):
        """ If the optimization has been run, shows the result in CalculiX."""
        if self.optpts:
            if self.grade == 'coarse':
                s = xy.make_shape(self.optpts, max_output_len=50)
            else:
                s = xy.make_shape(self.optpts, max_output_len=100)
            fq, _, _ = xy.find_eigenmodes([(s, self.thickness)], self.elastic, self.density, showshape=True)
    
    
if __name__ == '__main__':
    # This is an example use case
    bell_params = {
    'thickness': 6.35,   # choose a thickness of 1/4" (=6.35 mm)
    'ctrlpoints': 6,  # interpolate the bell curve from 6 points
    'grade': 'coarse', # for quick evaluation
    'scale': 300,  # initial bell size
    }
    
    
    minimum_fitness = 0.1  # this is below audible precision
    target_0 = np.array([ 0.5,  1. ,  1.2,  1.5,  1.8,  2. ])*440  # choose a fundamental (440 Hz) and a set of overtones
    targets = [target_0 * 2**(n/12.0) for n in range(13)] # chromatic scale multiples
    
    bells = []
    for trg in targets:
        i = 0
        while i < 5:  # try a few times
            bell = Bell(trg, **bell_params) # initialize a bell
            bell.findOptimumCurve()  # optimize its shape
            bells.append(bell) 
            pickle.dump(bells, open('bells.p','wb'))
            if bell.best_fit < minimum_fitness: # good enough for now.
                break
            i += 1
