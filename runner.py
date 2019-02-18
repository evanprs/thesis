from optimize import *

if __name__ == '__main__':

    """
    shape_curve = (
        [
            356.43009552,
            -204.98362925,
            -209.00809199,
            208.32247307,
            392.51135997
        ],
        [
            243.90161053,
            552.32736935,
            461.13068339,
            -470.30762604,
            -333.72226511
        ]
    )
    """

    """
    shape_curve = (
        [
            0.000,
            105.709,
            200.000,
            73.086,
            103.923,
            120.000,
            103.923,
            60.000,
            7.347e-15,
            -60.000,
            -103.923,
            -120.000,
            -103.923,
            -73.086,
            -200.000,
            -105.709
        ],
        [
            0.000,
            124.255,
            281.810,
            610.093,
            860.000,
            920.000,
            980.000,
            1023.923,
            1040.000,
            1023.923,
            980.000,
            920.000,
            860.000,
            610.093,
            281.810,
            134.255
        ]
    )
    """

    """
    shape_curve = (
        [
            -3.93449949e-8,
            +1.05703082e+2,
            +1.99986242e+1,
            +7.31047987e+1,
            +1.03918709e+2,
            +1.20018272e+2,
            +1.03913589e+2,
            +6.00044842e+1,
            +7.34671284e-15,
            -6.22524091e+1,
            -1.03926088e+2,
            -1.20089432e+2,
            -1.03931019e+2,
            -7.30909948e+1,
            -1.99980193e+2,
            -1.05717905e+2
        ],
        [
            +3.08867699e-7,
            +1.24264823e+2,
            +2.82381148e+2,
            +6.10124288e+2,
            +8.60009941e+2,
            +9.19922525e+2,
            +9.80091286e+2,
            +1.02410984e+3,
            +1.03999278e+3,
            +1.02393602e+3,
            +9.80013174e+2,
            +9.19966819e+2,
            +8.59912236e+2,
            +6.10075072e+2,
            +2.84447078e+2,
            +1.34256910e+2
        ]
    )
    """

    # Another curve, manual entry at moment, will be entered later
    shape_curve = (
        [
            +0.00000000e+00,
            +1.17142941e+02,
            +2.00000000e+02,
            +5.52830230e+01,
            +1.03923048e+02,
            +1.20000000e+02,
            +1.03923048e+02,
            +6.00000000e+01,
            +7.34788079e-15,
            +6.00000000e+01,
            +1.03923048e+02,
            +1.20000000e+02,
            -1.03923048e+02,
            +5.52830230e+01,
            +2.00000000e+02,
            +1.17142941e+02
        ],
        [
            +0.00000000,
            +148.42105222,
            +306.64351977,
            +650.27737530,
            +860.00000000,
            +920.00000000,
            +980.00000000,
            +1023.92304845,
            +1040.00000000,
            +1023.92304845,
            +980.00000000,
            +920.00000000,
            +860.00000000,
            +650.27737530,
            +306.64351977,
            +148.42105222
        ]
    )

    num_attempts = 2  # Usually two tries is enough to get near enough to our targets
    num_targets = 1
    num_ratio = 1.067
    base_note = 440
    fit_min = 0.05
    # target = np.array([ num_ratio**-1, 1., num_ratio**1 ])*base_note
    # target = np.array([ 622.26, 783.99, 932.33, 1108.73, 1479.98 ])
    # target = np.array([ 311.13, 392.00, 466.16, 554.37, 739.99 ])
    target = np.array([ 
        261.6255653006,
        329.6275569129,
        391.9954359817,
        466.1637615181
     ])  # C E G Bb
    targets = [ target*( 2**( n/12.0 ) ) for n in range(num_targets) ]

    materials = {
        "galvanized": {
            "8": "4.269",
            "9": "3.891",
            "10": "3.510",
            "11": "3.1318",
            "12": "2.753",
            "14": "1.9939",  # This and below is the !!DANGERZONE!!
            "16": "1.6129",
            "18": "1.310",
            "20": "1.005",
            "22": "0.853",
            "24": "0.701",
            "26": "0.551",
            "28": "0.474",
            "30": "0.398"
        }
    }

    # Set up material/simulation properties
    'params_sheet': {
        'units': 'imperial',
        'material': 'galvanized',
        'density': 0.007850,
        'modulus': 200000e6,
        'ratio': 0.3,
        'width': 2,
        'height': 4,
        'gauge': 8
    }
    
    'params_simulation': {  # NOTE: values to be filled in from above
        'thickness': str(materials[params_sheet["sheet"]["material"]][params_sheet["sheet"]["gauge"]]),
        'target': target,  # NOTE: must be an np.array
        'elastic': str(params_sheet["sheet"]["modulus"])+","+str(params_sheet["sheet"]["ratio"]),
        'density': str(params_sheet["sheet"]["density"]),
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
    print("Now writing to DXF... ", end="")
    xy.pts_to_dxf(bell.optpts, "outputs/dxf/shape.dxf")
    print(" ...file created!")

