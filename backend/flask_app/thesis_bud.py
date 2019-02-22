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
        'galvanized': {
            '8': '4.269',
            '9': '3.891',
            '10': '3.510',
            '11': '3.1318',
            '12': '2.753',
            '14': '1.9939'
            }
        }
    fit_min = 0.5

    valid = False

    if ('material' in inp) and ('density' in inp) and ('modulus' in inp) and ('ratio' in inp) and ('gauge' in inp) and ('target' in inp) and ('scale' in inp) and ('grade' in inp) and ('ctrlpoints' in inp):
        valid = True
    else:
        return "ERROR: Input not provided correctly\n"

    prm = {
        'thickness': float((materials[inp['material']])[str(inp['gauge'])]),
        'target': np.array(inp['target']),
        'elastic': str(inp['modulus'])+","+str(inp['ratio']),
        'density': float(inp['density']),
        'scale': float(inp['scale']),
        'grade': str(inp['grade']),
        'ctrlpoints': int(inp['ctrlpoints']),
    }

    bells = []
    b = Bell(**prm)
    b.findOptimumCurve()
    bells.append(b)
    
    res['version'] = b.version
    res['thickness'] = b.thickness
    res['elastic'] = b.elastic
    res['density'] = b.density
    res['scale'] = b.scale
    res['grade'] = b.grade
    #res['initial'] = b.c0
    #res['final'] = b.optpts
    res['fit'] = float(b.best_fit)
    #res['frequencies'] = b.best_fq

    return jsonify(res)


#==============================================================================
# "fill up that there flask"
#==============================================================================

if __name__ == '__main__':
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)
