import multiprocessing
from time import sleep
import random


def flatten(lss):
    return [item for sublist in lss for item in sublist]

def get_candidate(process_dict):
    """
    Returns a random candidate from a dict of candidates indexed by target

    Args:
        process_dict (dict (key -> list))

    Returns:
        candidate, target
    """

    if len(flatten(process_dict.values())) == 0:  #  if dict is empty, we're done
        return None

    # no empty sublists allowed. Any process popping from sublists should ensure this
    assert all([len(process_dict[trg]) > 0 for trg in process_dict]) 
    
    
    target = random.choice(list(process_dict.keys()))
    candidate = process_dict[target].pop()
    if len(process_dict[target]) == 0:
        del process_dict[target] # make sure we've got no empty sublists
    return target, candidate 



def process(arg):
    trg, i = arg
    pid = multiprocessing.current_process().pid
    random.seed(pid)
    value = random.random()
    sleep(random.random())
    print(f'process {trg}{i} finished! value = {value}')
    return trg, value

if __name__ == "__main__":
    to_process = {}
    targets = ['a','b','c','d','e']
    attempts = 5
    thresh = 0.75
    for trg in targets:
        to_process[trg] = [i for i in range(attempts)]  

    # num_workers = multiprocessing.cpu_count()
    
    #let's pretend we're a tiny cpu for now
    num_workers = 4

    finished = False
    while not finished:
        args = []
        # get up to num_workers candidates to process
        for _ in range(num_workers):
            if (arg := get_candidate(to_process)) != None:
                args.append(arg)
            else:
                finished = True

        with multiprocessing.Pool(num_workers) as pool:
            results = pool.map(process, args)
            print('finished eval!')
        
        for trg, value in results:
            if value > thresh: # success! don't process any more
                print(f"we have succeeded! {trg} got {value}")
                to_process.pop(trg, None) # others in group might do the same, so can't use del
        