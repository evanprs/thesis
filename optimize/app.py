# Python imports
import os, sys, time, uuid, json, subprocess
# Flask imports
from flask import Flask, jsonify, request, Response, send_file
# CORS imports (enables api-like interaction)
from flask_cors import CORS, cross_origin
# Requests (python 'axios')
import requests

# Simulation and Optimization Portions
from optimize import *
from notes import *
from to_lily import *


# Initalize the Flask App
# 	we also set where to search for our static files
app = Flask(__name__,
	static_folder = './../dist/static',
	template_folder = './../dist')
# Declare CORS compliant app
#   we also strictly set which resources are CORS-able
# CORS(app,
# 	resources={
# 		r"/sculptures": {
# 			"origins": "*"
# 		}
# 	})
# NOTE: this is actually enough for our needs
CORS(app)

#==============================================================================
# Data (postgreslite-lite-xlite-edition)
#==============================================================================

SCULPTURES = [
	{
		'id': uuid.uuid4().hex,
		'name': 'Flower 1',
		'target_frequencies': [
			220,
			275,
			365.2,
			385,
			512.6
		],
		'material_params': {
			"material": "Galvanized Steel",
			"modulus": 200000e6,
			"ratio": 0.3,
			"density": 0.007850,
			"gauge": 8,
		},
		'simulation_params': {
			"ctrlpoints": 5,
			"frequency_total": 20,
			"grade": "coarse",
			"c0": {
				"x": [
					3.171835209791645e-14,
					73.80728273096405,
					105.36648638776205,
					142.37347203841293,
					161.76093006775497,
					161.875,
					154.55654217061695,
					130.4540260412193,
					147.82158381637606,
					60,
					55.43277195067721,
					42.42640687119285,
					22.96100594190539,
					3.67394039744206e-15,
					-22.961005941905384,
					-42.426406871192846,
					-55.43277195067721,
					-60,
					-125.88717386693405,
					-141.1472627190168,
					-149.6078207797557,
					-161.875,
					-157.341445808329,
					-151.8009635653124,
					-116.25253930174182,
					-72.19127222642628
				],
				"y": [
					0,
					290.8445410152726,
					372.97547311231233,
					414.55961770431094,
					465.4406877400327,
					518,
					582.0194159205587,
					648.4540260412193,
					874.8728724609662,
					1355,
					1377.9610059419053,
					1397.4264068711927,
					1410.4327719506773,
					1415,
					1410.4327719506773,
					1397.4264068711927,
					1377.9610059419053,
					1355,
					821.918522478372,
					659.1472627190168,
					579.9695884040582,
					518,
					466.87666522311144,
					407.71014417760824,
					357.992106696218,
					295.8181099409908
				]
			}
		},
		'geometry_params': {
			"num_points_upper": 3,
			"num_points_lower": 4,
			"num_points": (3 + 4),
			"width_scale": 0.25,
			"length_upper": 0.60,
			"length_lower": 0.40,
			"length": 1000,
			"base_append": True,
			"diameter_transducer": 120,
			"radius_extension": 60,
			"variant": "standard",
			"symmetric": False
		},
		'results_store': {}
	}
]

MATERIALS = {
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

MIN_FITNESS = 0.5

#==============================================================================
# Helpers
#==============================================================================
def remove_sculpture(sculpture_id):
	for sculpture in SCULPTURES:
		if sculpture['id'] == sculpture_id:
			SCULPTURES.remove(sculpture)
			return True
	return False

def retrieve_sculpture(sculpture_id):
	for sculpture in SCULPTURES:
		if sculpture['id'] == sculpture_id:
			return sculpture
	return False

@app.route('/boop')
def boop():
	return jsonify('boop!')


#==============================================================================
# Routes
#==============================================================================
@app.route('/')
def route_index():
	# 'heartbeat'
	return jsonify('boop!')

@app.route('/sculptures', methods=['GET', 'POST'])
def all_sculptures():
	res = {
		'status': 'success'
	}

	# Determine if GET or POST
	if request.method == 'POST':
		# CREATE
		current_sculpture = request.get_json()
		SCULPTURES.append({
			'id': uuid.uuid4().hex,
			'name': current_sculpture.get('name'),
			'target_frequencies': current_sculpture.get('target_frequencies'),
			'material_params': current_sculpture.get('material_params'),
			'simulation_params': current_sculpture.get('simulation_params'),
			'geometry_params': current_sculpture.get('geometry_params'),
			'results_store': current_sculpture.get('results_store')
		})
		res['message'] = 'Sculpture created!'
	else:
		# READ
		res['sculptures'] = SCULPTURES

	return jsonify(res)


@app.route('/sculptures/<sculpture_id>', methods=['GET', 'PUT', 'DELETE'])
def one_sculpture(sculpture_id):
	res = {
		'status': 'success'
	}

	# Determine if PUT or DELETE
	if request.method == 'GET':
		# GET
		current_sculpture = retrieve_sculpture(sculpture_id)

		res['sculpture'] = current_sculpture
	elif request.method == 'PUT':
		# UPDATE
		current_sculpture = retrieve_sculpture(sculpture_id)
		updated_sculpture = request.get_json()

		# Remove old copy
		remove_sculpture(sculpture_id)
		# Append new copy
		SCULPTURES.append({
			'id': sculpture_id,
			'name': (updated_sculpture.get('name') or current_sculpture.get('name')),
			'target_frequencies': (updated_sculpture.get('target_frequencies') or current_sculpture.get('target_frequencies')),
			'material_params': (updated_sculpture.get('material_params') or current_sculpture.get('material_params')),
			'simulation_params': (updated_sculpture.get('simulation_params') or current_sculpture.get('simulation_params')),
			'geometry_params': (updated_sculpture.get('geometry_params') or current_sculpture.get('geometry_params')),
			'results_store': (updated_sculpture.get('results_store') or current_sculpture.get('results_store')),
		})

		res['message'] = 'Sculpture updated!'
	elif request.method == 'DELETE':
		# DELETE
		remove_sculpture(sculpture_id)

		res['message'] = 'Sculpture removed!'

	return jsonify(res)

@app.route('/sculptures/<sculpture_id>/generate_petal', methods=['GET'])
def sculpture_generate_petal(sculpture_id):
	res = {
		'status': 'success'
	}

	if request.method == 'GET':

		# Get Current Params
		current_sculpture = retrieve_sculpture(sculpture_id)
		geometry_params = current_sculpture['geometry_params']

		# Generate new shape
		interpolated_points, points = xy.gen_petal(**geometry_params)
		output_points = {
			'x': [x for x in points[0]], # avoiding ndarray
			'y': [y for y in points[1]] # avoiding ndarray
		}

		# Remove old copy
		remove_sculpture(sculpture_id)
		# Append new copy
		new_sculpture = {
			'id': sculpture_id,
			'name': current_sculpture.get('name'),
			'target_frequencies': current_sculpture.get('target_frequencies'),
			'material_params': current_sculpture.get('material_params'),
			'simulation_params': current_sculpture.get('simulation_params'),
			'geometry_params': current_sculpture.get('geometry_params'),
			'results_store': {}
		}
		new_sculpture['simulation_params']['c0'] = output_points
		SCULPTURES.append(new_sculpture)

		res['message'] = 'Sculpture geometry generated!'

	return jsonify(res)

@app.route('/sculptures/<sculpture_id>/check_current_frequencies', methods=['GET'])
def sculpture_check_current_frequencies(sculpture_id):
	res = {
		'status': 'success'
	}

	if request.method == 'GET':

		# Get Current Params
		current_sculpture = retrieve_sculpture(sculpture_id)
		local_material = current_sculpture['material_params']
		local_targets = current_sculpture['target_frequencies']
		local_simulation = current_sculpture['simulation_params']
		local_geometry_params = current_sculpture['geometry_params']

		# Setup Simulation
		params = {
			'thickness': float((MATERIALS[local_material['material']])[str(local_material['gauge'])]),
			'target': np.array(local_targets),
			'elastic': f"{local_material['modulus']},{local_material['ratio']}",
			'density': float(local_material['density']),
			'scale': float(local_geometry_params['length']),
			'grade': str(local_simulation['grade']),
			'ctrlpoints': int(local_simulation['ctrlpoints']),
			'c0': [
				local_simulation['c0']['x'],
				local_simulation['c0']['y']
			]
		}

		# Run Simulation
		b = Bell(**params)
		simulation_results = b.singleSimulation(int(local_simulation['frequency_total']) + 6)

		res['fitness'] = float(simulation_results['fit'])
		res['frequencies'] = [f for f in simulation_results['frequencies']]

		# Remove old copy
		remove_sculpture(sculpture_id)
		# Append new copy
		new_sculpture = {
			'id': sculpture_id,
			'name': current_sculpture.get('name'),
			'target_frequencies': current_sculpture.get('target_frequencies'),
			'material_params': current_sculpture.get('material_params'),
			'simulation_params': current_sculpture.get('simulation_params'),
			'geometry_params': current_sculpture.get('geometry_params'),
			'results_store': {
				'fit': res['fitness'],
				'frequencies': res['frequencies']
			}
		}
		SCULPTURES.append(new_sculpture)

	return jsonify(res)

@app.route('/sculptures/<sculpture_id>/optimize', methods=['GET'])
def sculpture_optimize(sculpture_id):
	res = {
		'status': 'success'
	}

	if request.method == 'GET':

		# Get Current Params
		current_sculpture = retrieve_sculpture(sculpture_id)
		local_material = current_sculpture['material_params']
		local_targets = current_sculpture['target_frequencies']
		local_simulation = current_sculpture['simulation_params']
		local_geometry_params = current_sculpture['geometry_params']

		# Setup Simulation
		params = {
			'thickness': float((MATERIALS[local_material['material']])[str(local_material['gauge'])]),
			'target': np.array(local_targets),
			'elastic': f"{local_material['modulus']},{local_material['ratio']}",
			'density': float(local_material['density']),
			'scale': float(local_geometry_params['length']),
			'grade': str(local_simulation['grade']),
			'ctrlpoints': int(local_simulation['ctrlpoints']),
			'c0': [
				local_simulation['c0']['x'],
				local_simulation['c0']['y']
			]
		}

		count_attempts = 0
		b = Bell(**params)

		try:
			b.findOptimumCurve()
			count_attempts += 1
			app.logger.critical("****************")
			app.logger.critical("fitness: ")
			app.logger.critical(str(b.best_fit))
			app.logger.critical("*****************")
		except AssertionError:
			count_attempts += 1
			count_attempts -= 1
		except TypeError:
			count_attempts += 1
			count_attempts -= 1

		if not (float(b.best_fit) < float(MIN_FITNESS)):
			while (count_attempts < 1):
				try:
					b.refine()
					count_attempts += 1
					app.logger.critical("****************")
					app.logger.critical("fitness: ")
					app.logger.critical(str(b.best_fit))
					app.logger.critical("*****************")
				except AssertionError:
					count_attempts += 1
					count_attempts -= 1
				except TypeError:
					count_attempts += 1
					count_attempts -= 1

				if (float(b.best_fit) < float(min_fit_acc)):
					break

		# app.logger.critical("    now final_x:")
		result_x = [x for x in b.optpts[0]]
		# if type(b.c0[0]) == np.ndarray:
		# 	res['final_x'] = b.optpts[0].tolist()
		# else:
		# 	res['final_x'] = b.optpts[0]

		# app.logger.critical("    now final_y:")
		result_y = [y for y in b.optpts[1]]
		# if type(b.c0[1]) == np.ndarray:
		# 	res['final_y'] = b.optpts[1].tolist()
		# else:
		# 	res['final_y'] = b.optpts[1]

		# app.logger.critical("    now fit:")
		result_fit = float(b.best_fit)

		# app.logger.critical("    now frequencies:")
		result_frequencies = [f for f in b.best_fq]
		# if type(b.best_fq) == np.ndarray:
		# 	res['frequencies'] = b.best_fq.tolist()
		# else:
		# 	res['frequencies'] = b.best_fq

		results = {
			'fit': result_fit,
			'frequencies': result_frequencies
		}

		output_points = {
			'x': [x for x in b.optpts[0]], # avoiding ndarray
			'y': [y for y in b.optpts[1]] # avoiding ndarray
		}

		# Remove old copy
		remove_sculpture(sculpture_id)
		# Append new copy
		new_sculpture = {
			'id': sculpture_id,
			'name': current_sculpture.get('name'),
			'target_frequencies': current_sculpture.get('target_frequencies'),
			'material_params': current_sculpture.get('material_params'),
			'simulation_params': current_sculpture.get('simulation_params'),
			'geometry_params': current_sculpture.get('geometry_params'),
			'results_store': results
		}
		new_sculpture['simulation_params']['c0'] = output_points
		SCULPTURES.append(new_sculpture)

		return jsonify(res)
	
	return jsonify({
		'status': 'failure'
	})

@app.route('/sculptures/<sculpture_id>/get_dxf', methods=['GET'])
def sculpture_get_dxf(sculpture_id):
	res = {
		'status': 'success'
	}

	if request.method == 'GET':

		# Get Current Params
		current_sculpture = retrieve_sculpture(sculpture_id)
		local_material = current_sculpture['material_params']
		local_targets = current_sculpture['target_frequencies']
		local_simulation = current_sculpture['simulation_params']
		local_geometry_params = current_sculpture['geometry_params']

		points = (local_simulation['c0']['x'], local_simulation['c0']['y'])

		xy.pts_to_dxf(points)

		return send_file('test.dxf', as_attachment=True)
	
	return jsonify({
		'status': 'failure'
	})

@app.route('/sculptures/<sculpture_id>/get_pdf', methods=['GET'])
def sculpture_get_pdf(sculpture_id):
	res = {
		'status': 'success'
	}

	if request.method == 'GET':

		# Get Current Params
		current_sculpture = retrieve_sculpture(sculpture_id)
		results = current_sculpture['results_store']

		if ('frequencies' in results.keys()):

			# Declare Tolerance
			tolerance_factor = 8
			tolerance = 1/tolerance_factor

			file_name = "Test"
			frequencies = results.get('frequencies')
			notes = []
			for f in frequencies:
				notes.append(Note(f, 1))

			notes = extract_notes_in_range(notes)

			scale_harmonics = get_all_scale_harmonics(notes, tolerance)
			value_harmonics = get_all_value_harmonics(notes, tolerance)
			reltv_harmonics = get_all_value_harmonics(notes, tolerance, 1)

			app.logger.debug('Writing lilypond file...')
			app.logger.critical('---')
			subprocess.call(['ls', '-l'])
			app.logger.critical('---')
			subprocess.call(['rm', 'output.ly'])
			app.logger.critical('---')
			subprocess.call(['ls', '-l'])
			app.logger.critical('---')
			subprocess.call(['rm', 'output.pdf'])
			app.logger.critical('---')
			subprocess.call(['ls', '-l'])
			app.logger.critical('---')
			file = open('output.ly', 'w+')
			file.write(generate_lily_content("Results", notes, scale_harmonics, value_harmonics, reltv_harmonics))
			file.close()
			app.logger.debug('...wrote lilypond file')

			app.logger.debug('Writing to PDF...')
			subprocess.call(['lilypond', 'output.ly'])
			app.logger.debug('...wrote PDF')

			return send_file('output.pdf', as_attachment=True)
		
		else:
			sculpture_check_current_frequencies(sculpture_id)
			sculpture_get_pdf(sculpture_id)
			# return jsonify({
			# 	'status': 'failure',
			# 	'message': 'Frequencies missing, run either check_current_frequencies or optimize_shape first!'
			# })

	return jsonify(False)







#==============================================================================
# Runtime operations
#==============================================================================
if __name__ == '__main__':
	# ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
	ENVIRONMENT_DEBUG = True
	app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)