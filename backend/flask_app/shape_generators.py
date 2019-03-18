import numpy as np
import xy_interpolation as xy
from random import random

def ptl_find_thinner_half(pts):
	"""
	Determines if a petal's source is pointed down or up
	Intended to keep the thinner part of a petal pointed up

	Args:
		pts: a list of x values representing half of a petal 
	
	Returns:
		( 1): when top of petal is thinner than bottom
		(-1): when bottom of petal is thinner
		( 0): when thin section is ambiguous (or error)
	"""
		
	if (pts[0] < pts[2]):
		#print("Thin on the bot")
		return -1
	elif (pts[0] > pts[2]):
		#print("Thin on the top")
		return 1
	else:
		print("ERROR: I don't know what happened")
		return 0



def ptl_flip_vertically(x_vals, y_vals):
	"""
	Flips the points of a petal vertically across it's center
	Intended to keep the thinner part of a petal pointed up

	Args:
		x_vals: the x values of the petal curve
		y_vals: the y values of the petal curve
	
	Returns:
		x_vals: flipped x values of petal curve
		y_vals: flipped y values of petal curve
	"""

	tmp_x = x_vals[0]
	tmp_y = y_vals[0]
	
	x_vals[0] = x_vals[2]
	y_vals[0] = y_vals[2]

	x_vals[2] = tmp_x
	y_vals[2] = tmp_y

	return x_vals, y_vals



def translate_base(pts, dist):
	for n in range(0, 9):
		pts[1][n] += dist
	
	return pts



def make_base(base_d=240, max_out_len=100):
	base_r = base_d / 2
	base_t = np.linspace(-1*np.pi/2,3*np.pi/2, 13)

	new_x = []
	new_y = []
	# not across all to make space for mounting
	for n in range(2, 11):
		new_x.append(base_r * np.cos(base_t[n]))
		new_y.append(base_r * np.sin(base_t[n]))
	
	pts = np.array(new_x), np.array(new_y)
	return pts



def gen_nodal_base(diameter_transducer=240, radius_extension=120):
	# Prepare variables
	circle_bound_plr_low = 0
	circle_bound_plr_upp = np.pi
	circle_bound_num_low = 0
	circle_bound_num_upp = 9
	circle_bound_num = 9

	# radius_extension = diameter_transducer / 2
	radius_transducer = diameter_transducer / 2
	radius_separation = np.linspace(circle_bound_plr_low, circle_bound_plr_upp, circle_bound_num)
	new_x = []
	new_y = []

	for ii in range(circle_bound_num_low, circle_bound_num_upp):
		new_x.append(radius_extension * np.cos(radius_separation[ii]));
		new_y.append(radius_extension * np.sin(radius_separation[ii]));

	for ii in range(0, len(new_y)):
		new_y[ii] += radius_transducer

	pts = np.array(new_x), np.array(new_y)

	return pts



def make_random_petal(max_wth=25, max_len=100, base_d=240, extn_d=120, max_out_len=100, scale=600, pointy=False):
	"""
	Randomly generates a (vaguely) petal shape. Given the ratio of width to
	length and the length in millimeters.
	"""
	
	s_wth = max_wth/100
	s_len = max_len/100

	valid_shape = False
	fail_counter = 0

	while not valid_shape:
		try:
		  # Points A and B
			if pointy:
				xs_l = np.append(np.random.uniform(0.1, 0.5), 1)
			else:
				xs_l = np.append(np.random.uniform(1/2, 3/4), 1)
			# Point C
			xs_l = np.append(xs_l, np.random.uniform(1/5, 2/3))

			# Points A and B
			ys_l = np.append(np.random.uniform(1/16, 1/8), np.random.uniform(1/4, 1/2))
			# Point C
			ys_l = np.append(ys_l, np.random.uniform(5/6, 15/16))
			
			# Check if oriented correctly
			if (ptl_find_thinner_half(xs_l) == -1):
				#print("We had to flip it.")
				#xs_l, ys_l = ptl_flip_vertically(xs_l, ys_l)
				xs_l = np.flip(xs_l)
				ys_l = np.flip(ys_l)

			# Create the base
			# b_pts = translate_base(make_base(base_d), base_d/2 + scale)
			b_pts = translate_base(gen_nodal_base(base_d, extn_d), scale)

			# Points (ABC)', also scale
			xs_l *= ( ( s_wth/2 ) * scale)
			xs_r = -1*np.flip(xs_l)

			# Points (ABC)', also scale
			ys_l *= (s_len * scale)
			ys_r = np.flip(ys_l)

			# Append the sections
			xs = np.append(np.append(0, xs_l), np.append(b_pts[0], xs_r))
			ys = np.append(np.append(0, ys_l), np.append(b_pts[1], ys_r))

			pts = xs, ys
			fit_pts = xy.make_shape(pts, max_out_len)

			valid_shape = True
			return fit_pts, pts

		except ValueError:
			fail_counter += 1
	return True



def gen_petal(
 num_points=4, num_points_upper=2, num_points_lower=2,
 width_scale=0.20, length=500, length_upper=0.75, length_lower=0.25,
 diameter_transducer=240, radius_extension=120,
 variant="curve", deviation_factor=0,
 max_out_len=100
 ):

	if not isinstance(num_points, int):
		raise TypeError("ERROR: Number of points must be integer")
	if variant not in ["curve", "point", "standard", "custom"]:
		raise TypeError("ERROR: Selected variant not supported")
	
	if variant not in "custom":
		if variant in "point":
			deviation_factor = 0.20
		elif variant in "curve":
			deviation_factor = 0.10
		elif variant in "standard":
			deviation_factor = 0.00
		

	
	# Variable assignment
	if num_points is not (num_points_upper + num_points_lower):
		num_points_upper = int(round(num_points/2, 0))
		num_points_lower = int(round(num_points/2, 0))
		# return False, str((num_points_upper, num_points_lower))

	scale_w = width_scale/2
	scale_l = length

	valid_shape = False
	counter_fail = 0

	while not valid_shape:
		try:
			# Determine length proportions
			p_lower = np.random.uniform(length_lower*(1-deviation_factor), length_lower*(1+deviation_factor))
			
			# Create lower half
			s_lower = np.linspace(0, -1*(1/2)*np.pi, 1+num_points_lower, endpoint=False)
			s_lower = np.delete(s_lower, 0)

			# Create upper half
			s_upper = np.linspace(0, (1/2)*np.pi, 1+num_points_upper, endpoint=False)
			s_upper = np.delete(s_upper, 0)

			return False, str(np.concatenate((s_lower, s_upper)))
			

			# Build lower portion of petal
			return False, True
		except ValueError:
			counter_fail += 1
	
	return False, False