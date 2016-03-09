import random
import numpy
from deap import algorithms, base, creator, tools
from xy_interpolation import *


def evalOneMax(individual):
    return numpy.sum(individual[0]),

def evalTestFreq(individual):
    try:
        s = make_shape(individual,max_output_len=50)
        # plt.figure()
        # plt.plot(s[0],s[1])
        # plt.show()
        fq, _, _ = find_eigenmodes(s, 5)
        fit = fitness(fq[:4],np.array([.5,1.0,1.5,2.0])),
        print('~~EVALUATING FITNESS~~')
        print('fq =',fq[:4])
        print('fitness = ',fit)
        return fit
    except ValueError:
        return (5000), # self-intersecting. very bad. TODO - how bad?


def cxTwoPointCopy(ind1, ind2):
    """Execute a two points crossover with copy on the input individuals. The
    copy is required because the slicing in numpy returns a view of the data,
    which leads to a self overwritting in the swap operation. It prevents
    ::
    
        >>> import numpy
        >>> a = numpy.array((1,2,3,4))
        >>> b = numpy.array((5.6.7.8))
        >>> a[1:3], b[1:3] = b[1:3], a[1:3]
        >>> print(a)
        [1 6 7 4]
        >>> print(b)
        [5 6 7 8]
    """
    size = len(ind1)
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else: # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2]         = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()
        
    return ind1, ind2




creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMin)

# TODO - add the thickness as a gene
toolbox = base.Toolbox()
toolbox.register("pts", lambda: make_random_shape(4, scale=400)[1]) 
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.pts)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


toolbox.register("evaluate", evalTestFreq)
toolbox.register("mate", cxTwoPointCopy)
# TODO - set a scale for sigma
toolbox.register("mutate", lambda i:tools.mutGaussian(i, mu=0.0, sigma=1.0, indpb=0.05))
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    random.seed(64)
    
    pop = toolbox.population(n=10) # TODO - pick a good number
    
    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(1, similar=numpy.array_equal)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    
    # TODO - set ngen to something reasonable
    algorithms.eaSimple(pop, toolbox, cxpb=0.90, mutpb=0.2, ngen=10, stats=stats, halloffame=hof)

    return pop, stats, hof




if __name__ == "__main__":
    pop,stats,hof = main()
    print hof





