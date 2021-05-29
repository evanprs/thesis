import random
import pickle
import logging
from pathlib import Path
import multiprocessing

from coolname import generate_slug
import numpy as np
from scipy.optimize import fmin, basinhopping
import tqdm
import multiprocessing_logging # TODO - this library only works on POSIX

import xy_interpolation as xy

VERSION = '1.2'

unflatten = lambda flatpts: [flatpts[:len(flatpts) // 2],  flatpts[len(flatpts) // 2:]]

def dict_append(dictionary, key, listvalue):
    if key in dictionary.keys():
        dictionary[key] += listvalue
    else:
        dictionary[key] = listvalue

def dict_add(dict1, dict2):
    """ Merges the contents of dict2 into dict1. All values of both must be lists """
    for key in dict2:
        dict_append(dict1, key, dict2[key])


def refine_wrapper(bell):
    # need a function that returns the bell object for multiprocessing
    # TODO - make this less bad
    random.seed(multiprocessing.current_process().pid)  # need to seed random to avoid file collisions 
    bell.refine()
    return bell


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
        self.name = generate_slug(2)
        self.eval_count = 0  # track number of evaluations, just for fun
        
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

        
        
    def evalFitness(self, flatpts, crosspenalty=100.0, progress_dict=None):
        """
        Fitness of points defining curve. Needs flattened points for use with fmin

        Args:
            flatpts (np.array): flattened points [x1,x2,...y1,y2,...] defining curve
            crosspenalty (float): value to return if curve is self-intersecting
            progress_dict (dict): shared dictionary for tracking progress during multiprocessing 

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
            fq, _, _ = xy.find_eigenmodes([(s, self.thickness)], self.elastic, self.density, name=self.name)
            if len(fq) == 0: raise ValueError("Simulation failed")
            fit = xy.fitness(fq[:n_freq], self.target)
            logging.debug("Bell %s evaluated to fit %s", self.name, fit)
            multiprocessing_logging.install_mp_handler()
            self.fits.append(fit)
            self.fqs.append(fq)
            return fit
        except ValueError as err:
            # if you give a constant value, the algorithm thinks it's finished
            logging.debug(f"Points {pts} evaluated to an invalid shape")
            return crosspenalty * (random.random()+1)
        finally:
            self.eval_count += 1

    def findOptimumCurve(self):
        """
        Uses basic downhill simplex optimization to find a curve with freqs target
    
        Returns:
            optpts (tuple): points (x,y) defining optimized curve
        """
        
        x, y = self.c0
        flatpts = np.append(x, y)
        if self.grade == 'coarse':
            ftol = 0.1
            xtol = 25
        else:
            ftol = 0.0  # mean relative error
            xtol = 5  # tolerance in mm
        
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
    
        # isolate best case
        self.best_fit = min(self.fits)
        self.best_fq = self.fqs[self.fits.index(self.best_fit)]
        
        return retdict


    def refine(self):
        if self.grade == 'coarse':
            self.grade = 'fine'
            c0_initial = self.c0  # save for reference
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


class Controller():
    """
    Controller class for managing process of optimizing targets and loading saved work
    """
    def __init__(self):
        self.candidates = {}
        self.roughed_candidates = {}
        self.finished_candidates = {}
        self.version = VERSION

        logging.basicConfig(filename="test.log",
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
         level="INFO")

        # TODO - move to View object
        # self.progress_manager = enlighten.get_manager() 
        Path('data').mkdir(exist_ok=True)
        self.data_path = Path('data') / generate_slug(2)
        Path(self.data_path).mkdir()


    def save(self, filename='controller.p'):
        # save whole state
        with open(self.data_path / filename,'wb') as outfile:
            pickle.dump(self, outfile)


    def load(self, filepath, append=False):
        """
        Places previous results in memory.

        Args:
            filepath (str): path to pickle file of previous save
            append (bool): if True, will attempt to append members rather than overwrite
        """
        with open(filepath, 'rb') as prev_savefile:
            prev_ctrl = pickle.load(prev_savefile)
        assert type(prev_ctrl) == Controller
        # assert prev_ctrl.version == self.version
        if append:
            dict_add(self.candidates, prev_ctrl.candidates)
            dict_add(self.roughed_candidates, prev_ctrl.roughed_candidates)
            dict_add(self.finished_candidates, prev_ctrl.finished_candidates)
        else:
            self.__dict__.update(prev_ctrl.__dict__)

    def process_bell(self, bell):
        # Wrapper since multiprocessing needs to return modified object
        random.seed(multiprocessing.current_process().pid)  # need to seed random to avoid file collisions 
        bell.findOptimumCurve() 
        return bell


    def make_candidates(self, target, parameters, attempts):
        """
        Creates bell objects for target parameters
        
        Args:
            target (array): Frequencies to optimize to
            parameters (dict): Bell object initialization arguments
            attempts (int): number of objects to create
        """    
        for _ in range(attempts):
            new_bell = Bell(target, **parameters)
            dict_append(self.candidates, tuple(target), [new_bell])

            
    def process_candidates(self, fit_tolerance):
        """
        Process all candidates to a given tolerance

        Args:
            fit_tolerance (float): acceptable fitness upper bound
        """
        # TODO - replace 'grade' with 'tolerance', make it a sliding scale
        if self.candidates == None: return None

        logging.info("started processing candidates")

        while any([len(cands) > 0 for cands in list(self.candidates)]):
            # take one candidate from each target
            to_process = []
            for target in self.candidates.keys():  # note that target is now a tuple, not array
                if len(self.candidates[target]) > 0:
                    to_process.append(self.candidates[target].pop())

            # do the work
            with multiprocessing.Pool() as pool:
                coarse_optimized = list(pool.imap(self.process_bell, to_process), total=len(to_process))

            for bell in coarse_optimized:
                target = tuple(bell.target)
                if bell.best_fit < fit_tolerance: # found a good enough candidate, ignore the rest
                    self.candidates[target] = []
                dict_append(self.roughed_candidates, target, [bell])
            
            self.save()
            
        
    def refine_candidates(self):
        if self.roughed_candidates == None: return None

        logging.info("started refining candidates")

        # find the best candidate for each target, optimize those
        finalists = []
        for target in self.roughed_candidates:
            cands = self.roughed_candidates[target]
            best = min(cands, key = lambda c: c.best_fit)  # raises TypeError if best_fit empty
            finalists.append(best)

        for bell in finalists: 
            logging.info(f"our finalist is {bell.name} with fit {bell.best_fit}")
        
        # run the calculation for all at once
        pool = multiprocessing.Pool()
        finished_candidates = list(tqdm.tqdm(pool.imap(refine_wrapper, finalists), total=len(finalists)))
        for cand in finished_candidates:
            self.finished_candidates[tuple(cand.target)] = cand
        
        self.save()




if __name__ == '__main__':
    # base_params = {
    # 'thickness': 6.35,   # choose a thickness of 1/4" (=6.35 mm)
    # 'ctrlpoints': 6,  # interpolate the bell curve from 6 points
    # 'grade': 'coarse', # for quick evaluation
    # 'scale': 300,  # initial bell size
    # }
    # attempts = 5
    # # minimum_fitness = 0.1  # this is below audible precision
    # target_0 = np.array([ 0.5,  1. ,  1.2,  1.5,  1.8,  2. ])*220 
    # # choose a fundamental (220 Hz) and a set of overtones
    # targets = [target_0 * 2**(n/12.0) for n in range(13)] # chromatic scale multiples
    
    # # Create controller object, add candidates
    # controller = Controller()
    # for target in targets:
    #     controller.make_candidates(target, base_params, attempts)
    
    # controller.process_candidates(0.1)
    # controller.refine_candidates()
    
    controller = Controller()
    controller.load('cont_done.p')
    controller.refine_candidates()
    