from optimize import *

def runit():

    # A test curve
    shape_curve = (
        [
            0.00000000e+00,
            1.03486839e+02,
            2.00000000e+02,
            5.81410155e+01,
            1.03923048e+02,
            1.20000000e+02,
            1.03923048e+02,
            6.00000000e+01,
            7.34788079e-15,
            -6.00000000e+01,
            -1.03923048e+02,
            -1.20000000e+02,
            -1.03923048e+02,
            -5.81410155e+01,
            -2.00000000e+02,
            -1.03486839e+02
        ],
        [
            0.,
            143.60317865,
            307.91678992,
            637.37921841,
            860.,
            920.,
            980.,
            1023.92304845,
            1040.,
            1023.92304845,
            980.,
            920.,
            860.,
            637.37921841,
            307.91678992,
            143.60317865
        ]
    )

    num_attempts = 1  # Usually two tries is enough to get near enough to our targets
    num_targets = 1
    num_ratio = 1.067
    base_note = 440
    fit_min = 0.05
    # target = np.array([ num_ratio**-1, 1., num_ratio**1 ])*base_note
    target = np.array([ 
        261.6255653006,
        329.6275569129,
        391.9954359817,
        466.1637615181
     ])  # C E G Bb
    targets = [ target*( 2**( n/12.0 ) ) for n in range(num_targets) ]

    materials = {
        'galvanized': {
            '8': '4.269',
            '9': '3.891',
            '10': '3.510',
            '11': '3.1318',
            '12': '2.753',
            '14': '1.9939',  # NOTE: This and below is the !!DANGERZONE!!
            '16': '1.6129',
            '18': '1.310',
            '20': '1.005',
            '22': '0.853',
            '24': '0.701',
            '26': '0.551',
            '28': '0.474',
            '30': '0.398'
        }
    }

    # Set up material/simulation properties
    params_sheet = {
        'units': 'imperial',
        'material': 'galvanized',
        'density': 0.007850,
        'modulus': 200000e6,
        'ratio': 0.3,
        'width': 2,
        'height': 4,
        'gauge': 8
    }
    
    params_simulation = {  # NOTE: values to be filled in from above
        'thickness': float((materials[params_sheet['material']])[str(params_sheet['gauge'])]),  # NOTE: must be a number
        'target': target,  # NOTE: must be an np.array
        'elastic': str(params_sheet['modulus'])+","+str(params_sheet['ratio']),
        'density': float(params_sheet['density']),
        'scale': 800,
        'grade': 'coarse',
        'ctrlpoints': 5,
        'c0': shape_curve
    }

    # Simulation Scope
    bells = []  # hold our output
    for trg in targets:
        i = 0
        while ( i < num_attempts ):
            bell = Bell(**params_simulation)
            bell.findOptimumCurve()
            bells.append(bell)
            pickle.dump(bells, open('bells.p', 'wb'))
            if ( bell.best_fit < fit_min ):
                break
            else:
                params_simulation['c0'] = bell.optpts
            i += 1

    # pnts_to_dxf(bell.optpts)
    print("\n\n\n")
    print("="*30)
    print("Final Results: ")
    print(f"Fitness: {bell.best_fit}")
    print("Target FQs: ", end="")
    print(bell.target)
    print("Frequencies: ", end="")
    print(bell.best_fq)
    print("Points: ", end="")
    print(bell.optpts)
    print("Comparison: ")
    xy.print_fitness_vals(xy.find_frequencies(bell.best_fq, bell.target), bell.target, bell.best_fit)

    print("\n\n\n")
    print("Geometry to write to DXF: ")
    print(bell.optpts)
    """
    print("Now writing to DXF... ", end="")
    xy.pts_to_dxf(bell.optpts, "outputs/dxf/shape.dxf")
    print(" ...file created!")
    """

    return bell.optpts
    
if __name__ == '__main__':
    runit()
