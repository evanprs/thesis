import random
import numpy
from deap import algorithms, base, creator, tools
from xy_interpolation import *

THICKNESS = 6.35
TARGET = np.array([.5,1.0,1.5,2.0])
NUM_POINTS = 8
POPULATION = 10
NGEN = 10

def evalOneMax(individual):
    return numpy.sum(individual[0]),

def evalTestFreq(individual):
    try:
        s = make_shape(individual,max_output_len=50)
        fq, _, _ = find_eigenmodes(s, THICKNESS)
        fit = fitness(fq[:len(TARGET)],TARGET),
        return fit
    except ValueError:
        return (5000), # self-intersecting. very bad. TODO - how bad?

def crossover_points(ind1,ind2):
    """
    Performs two-point crossover on the points of two individuals.
    """
    x1,y1 = ind1
    x2,y2 = ind2
    pts1 = zip(x1,y1)
    pts2 = zip(x2,y2)
    newpts1,newpts2 = tools.cxTwoPoint(pts1,pts2)
    c1 = zip(*newpts1)
    c2 = zip(*newpts2)
    ind1 = creator.Individual(np.array(c1))
    ind2 = creator.Individual(np.array(c2))
    return ind1, ind2
    

creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("pts", lambda: make_random_shape(NUM_POINTS, scale=400)[1]) 
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.pts)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


toolbox.register("evaluate", evalTestFreq)
toolbox.register("mate", crossover_points)
# TODO - set a scale for sigma
toolbox.register("mutate", lambda i:tools.mutGaussian(i, mu=0.0, sigma=400.0, indpb=0.05))
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    random.seed(64)
    
    pop = toolbox.population(n=POPULATION) # TODO - pick a good number
    
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
    algorithms.eaSimple(pop, toolbox, cxpb=0.90, mutpb=0.2, ngen=NGEN, stats=stats, halloffame=hof)

    return pop, stats, hof




if __name__ == "__main__":
    pop,stats,hof = main()
    print hof





