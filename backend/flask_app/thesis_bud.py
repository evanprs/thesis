import os
import sys
import time
from flask import Flask, jsonify, request, Response
import requests

#sim sim sim
from optimize import *
from runner import runit

app = Flask(__name__)

#==============================================================================
# Helper Methods Go Here
#==============================================================================



#==============================================================================
# App Methods (routes) Go Here
#==============================================================================

@app.route('/')
def index():
    return "Looking golden ponyboy\n"

@app.route('/bc')
def bc():
    p = {
        'thickness': 6.35,
        'ctrlpoints': 5,
        'grade': 'coarse',
        'scale': 300,
    }
    t = np.array([ 400. , 440., 500. ])
    b = Bell(t, **p)
    
    return str(b.c0)+"\n"

@app.route('/api/get_pts_of_shp')
def get_pts_of_shp():
    p = {
        'thickness': 4.269,
        'ctrlpoints': 5,
        'grade': 'coarse',
        'scale': 800,
    }
    t = np.array([ 440*[ 0.5, 1., 1.2, 1.5 ] ])
    b = Bell(t, **p)

    return str(b.c0)+"\n"

@app.route('/api/gen_ptl_shp')
def gen_ptl_shp():
    fit_pts, pts = xy.make_random_petal(scale=840, base_d=120, extn_d=30, max_wth=20)
    return str(pts)

@app.route('/api/gen_ptl_neue', methods=['POST'])
def gen_ptl_pts():

    inp = request.get_json()
    prm = {}
    res = {}

    if ('num_points_upper' in inp) and ('num_points_lower' in inp):
        prm['num_points_lower'] = int(inp['num_points_lower'])
        prm['num_points_upper'] = int(inp['num_points_upper'])
        prm['num_points'] = int(inp['num_points_upper']) + int(inp['num_points_lower'])
    elif ('num_points' in inp):
        prm['num_points_lower'] = int(round(inp['num_points']/2, 0))
        prm['num_points_upper'] = int(round(inp['num_points']/2, 0))
        prm['num_points'] = int(inp['num_points'])
    
    if ('width_scale' in inp):
        prm['width_scale'] = float(inp['width_scale'])
    
    if ('length' in inp):
        prm['length'] = float(inp['length'])
    
    if ('length_upper' in inp):
        prm['length_upper'] = float(inp['length_upper'])
    
    if ('length_lower' in inp):
        prm['length_lower'] = float(inp['length_lower'])
    
    if ('diameter_transducer' in inp):
        prm['diameter_transducer'] = float(inp['diameter_transducer'])
    
    if ('radius_extension' in inp):
        prm['radius_extension'] = float(inp['radius_extension'])
    
    if ('deviation_factor' in inp):
        prm['deviation_factor'] = float(inp['deviation_factor'])
    
    if ('max_out_len' in inp):
        prm['max_out_len'] = int(inp['max_out_len'])

    if inp['variant'] not in ["curve", "point", "standard", "custom"]:
        raise TypeError("ERROR: Selected variant not supported")
    else:
        prm['variant'] = str(inp['variant'])

    # a = 3
    # b = 5
    # c = a + b
    # fit_pts, pts = xy.gen_petal(num_points_upper=a, num_points_lower=b, num_points=c, length_upper=0.60, length_lower=0.30, diameter_transducer=120, radius_extension=30, length=838, variant="standard")

    fit_pts, pts = xy.gen_petal(**prm)
    return str(pts)

@app.route('/api/get_cll_to_tst')
def get_cll_to_tst():
    b = runit()
    return str(b)+"\n"

@app.route('/api/get_cll_to_ths', methods=['POST'])
def get_cll_to_ths():

    # First, accept our input
    inp = request.get_json() # Gnabbed from the request framework
    res = {}
    materials = {
        "Carbon Steel": {
            "7": 4.554,
            "8": 4.175,
            "9": 3.797,
            "10": 3.416,
            "11": 3.038,
            "12": 2.656,
            "14": 1.897,
            "16": 1.518,
            "18": 1.214,
            "20": 0.911,
            "22": 0.759,
            "24": 0.607,
            "26": 0.454,
            "28": 0.378
        },
        "Aluminum": {
            "7": 3.665,
            "8": 3.264,
            "9": 2.906,
            "10": 2.588,
            "11": 2.305,
            "12": 2.053,
            "14": 1.628,
            "16": 1.291,
            "18": 1.024,
            "20": 0.812,
            "22": 0.644,
            "24": 0.511,
            "26": 0.405,
            "28": 0.321,
            "30": 0.255
        },
        "Stainless Steel": {
            "8": 4.365,
            "9": 3.968,
            "10": 3.571,
            "11": 3.175,
            "12": 2.778,
            "14": 1.984,
            "16": 1.587,
            "18": 1.27,
            "20": 0.952,
            "22": 0.794,
            "24": 0.635,
            "26": 0.476,
            "28": 0.396,
            "30": 0.318
        },
        "Galvanized Steel": {
            "8": 4.269,
            "9": 3.891,
            "10": 3.51,
            "11": 3.132,
            "12": 2.753,
            "14": 1.994,
            "16": 1.613,
            "18": 1.31,
            "20": 1.005,
            "22": 0.853,
            "24": 0.701,
            "26": 0.551,
            "28": 0.474,
            "30": 0.398
        },
        "Brass": {
            "7": 3.665,
            "8": 3.264,
            "9": 2.906,
            "10": 2.588,
            "11": 2.305,
            "12": 2.053,
            "14": 1.628,
            "16": 1.291,
            "18": 1.024,
            "20": 0.812,
            "22": 0.644,
            "24": 0.511,
            "26": 0.405,
            "28": 0.321,
            "30": 0.255
        },
        "Copper": {
            "7": 4.572,
            "8": 4.191,
            "9": 3.759,
            "10": 3.404,
            "11": 3.048,
            "12": 2.769,
            "14": 2.108,
            "16": 1.651,
            "18": 1.245,
            "20": 0.889,
            "22": 0.711,
            "24": 0.559,
            "26": 0.457,
            "28": 0.356,
            "30": 0.305
        }
    }
    fit_min = 0.5

    valid = False

    if ('material' in inp) and ('density' in inp) and ('modulus' in inp) and ('ratio' in inp) and ('gauge' in inp) and ('target' in inp) and ('scale' in inp) and ('grade' in inp) and ('ctrlpoints' in inp):
        valid = True
    else:
        return "ERROR: Input not provided correctly"

    if inp['custom-shape']:
        if inp['shape-type'] == "petal":
            fit_pts, pts = xy.make_random_petal(scale=inp['scale'], base_d=inp['transducer-diameter'], extn_d=inp['transducer-extension'], max_wth=inp['width-scale'])
        else:
            return "ERROR: Custom shapes not supported in this version"

    prm = {
        'thickness': float((materials[inp['material']])[str(inp['gauge'])]),
        'target': np.array(inp['target']),
        'elastic': str(inp['modulus'])+","+str(inp['ratio']),
        'density': float(inp['density']),
        'scale': float(inp['scale']),
        'grade': str(inp['grade']),
        'ctrlpoints': int(inp['ctrlpoints']),
    }

    if inp['custom-shape']:
        prm['c0'] = pts
        # return str(pts)

    bells = []
    count_att = 0
    b = Bell(**prm)
    # while (count_att < 1):
        # try:
    b.findOptimumCurve()
            # count_att += 1
        # except AssertionError:
        #     count_att = 0
        # except TypeError:
        #     count_att = 0
    bells.append(b)
    
    # res['version'] = b.version
    # res['target'] = b.target
    res['thickness'] = b.thickness
    # res['elastic'] = b.elastic
    # res['density'] = b.density
    # res['scale'] = b.scale
    # res['grade'] = b.grade
    res['initial_x'] = b.c0[0].tolist()
    res['initial_y'] = b.c0[1].tolist()
    # res['initial'] = b.c0
    res['final_x'] = b.optpts[0].tolist()
    res['final_y'] = b.optpts[1].tolist()
    # res['final'] = b.optpts
    res['fit'] = float(b.best_fit)
    res['frequencies'] = b.best_fq
    # res['frequencies'] = b.best_fq

    app.logger.info("==========================================================")
    app.logger.info("got this output:")
    app.logger.info(str(res))
    app.logger.info("==========================================================")

    return jsonify(res)


#==============================================================================
# "fill up that there flask"
#==============================================================================

if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)
