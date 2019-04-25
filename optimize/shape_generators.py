import numpy as np
import xy_interpolation as xy
from random import random

from thesis_bud import app

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



def translate_shape_up(pts, dist):
	for n in range(len(pts[0])):
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



def pick_val(base_l, base_u, vary):
	return np.random.uniform(base_l*(1-vary), base_u*(1+vary))



def gen_petal(
	num_points=4, num_points_upper=2, num_points_lower=2,
	width_scale=0.25, length=1000, length_upper=-1, length_lower=-1,
	base_append=1, diameter_transducer=240, radius_extension=120,
	variant="curve", deviation_factor=0, symmetric=True,
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

	if length_lower is -1:
		length_lower = 1.5*width_scale
	if length_upper is -1:
		length_upper = 1 - length_lower

	scale_w_min = 100
	scale_w = (width_scale*length)/2
	scale_l = length

	valid_shape = False
	counter_fail = 0

	# app.logger.critical("got past the setup")

	while not valid_shape:
		try:
			# Determine length proportions
			p_lower = pick_val(length_lower, length_lower, deviation_factor)
			p_upper = 1 - p_lower
			
			# Create lower half r and t
			t_lower = np.linspace(-1*(1/2)*np.pi, 0, 1+num_points_lower, endpoint=False)
			# t_lower = np.delete(t_lower, 0)
			r_lower = np.array(p_lower*scale_l)
			# r_lower = np.array([])
			for ii in range(len(t_lower) - 1):
				scale_bound_l = min(p_lower*scale_l, scale_w)
				scale_bound_u = max(p_lower*scale_l, scale_w)
				scale_bound_d = scale_bound_u - scale_bound_l
				scale_bound_b = np.random.beta(3, 2)

				r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)
				while (r_curr*np.cos(t_lower[ii+1]) > scale_w):
					r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)

				r_lower = np.append(r_lower, r_curr)
			r_lower.sort()
			r_lower = np.flip(r_lower)

			# Create upper half r and t
			t_upper = np.linspace(0, (1/2)*np.pi, 1+num_points_upper, endpoint=False)
			# t_upper = np.delete(t_upper, 0)
			r_upper = np.array(scale_w)
			for ii in range(len(t_upper) - 1):
				scale_bound_l = min(p_upper*scale_l, scale_w)
				scale_bound_u = max(p_upper*scale_l, scale_w)
				scale_bound_d = scale_bound_u - scale_bound_l
				scale_bound_b = np.random.beta(2, 2)

				r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)
				app.logger.critical(f"r_curr = {r_curr} ~> x-comp = {r_curr*np.cos(t_upper[ii+1])} w/i b({(((diameter_transducer)/2))}, {scale_w})")
				while not ( scale_w > (r_curr*np.cos(t_upper[ii+1])) > ((diameter_transducer)/2) ):
					r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)
					app.logger.critical(f"r_curr = {r_curr} ~> x-comp = {r_curr*np.cos(t_upper[ii+1])} w/i b({(((diameter_transducer)/2))}, {scale_w})")
				
				app.logger.critical(f"------------ got past right upper ------------")

				r_upper = np.append(r_upper, r_curr)
			# r_upper.sort()

			# Create xs and ys
			rs = np.concatenate((r_lower, r_upper))
			ts = np.concatenate((t_lower, t_upper))

			# Generate right side of petal
			xs_r = rs*np.cos(ts)
			ys_r = rs*np.sin(ts)

			# Generate base of petal
			if base_append:
				app.logger.critical("add add the base")
				b_pts = gen_nodal_base(diameter_transducer, radius_extension)
				b_pts = translate_shape_up(b_pts, p_upper*scale_l)
			else:
				app.logger.critical("no.")
				b_pts = []

			if symmetric:
				# Generate left side of petal
				xs_l = -1*np.flip(xs_r[1:])
				ys_l = np.flip(ys_r[1:])
			else:
				# Create lower half r and t
				t_lower = np.linspace(-1*(1/2)*np.pi, 0, 1+num_points_lower, endpoint=False)
				# t_lower = np.delete(t_lower, 0)
				r_lower = np.array(p_lower*scale_l)
				# r_lower = np.array([])
				for ii in range(len(t_lower) - 1):
					scale_bound_l = min(p_lower*scale_l, scale_w)
					scale_bound_u = max(p_lower*scale_l, scale_w)
					scale_bound_d = scale_bound_u - scale_bound_l
					scale_bound_b = np.random.beta(3, 2)

					r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)
					while (r_curr*np.cos(t_lower[ii+1]) > scale_w):
						r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)

					r_lower = np.append(r_lower, r_curr)
				r_lower.sort()
				r_lower = np.flip(r_lower)

				# Create upper half r and t
				t_upper = np.linspace(0, (1/2)*np.pi, 1+num_points_upper, endpoint=False)
				# t_upper = np.delete(t_upper, 0)
				r_upper = np.array(scale_w)
				for ii in range(len(t_upper) - 1):
					scale_bound_l = min(p_upper*scale_l, scale_w)
					scale_bound_u = max(p_upper*scale_l, scale_w)
					scale_bound_d = scale_bound_u - scale_bound_l
					scale_bound_b = np.random.beta(2, 2)

					r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)
					app.logger.critical(f"r_curr = {r_curr} ~> x-comp = {r_curr*np.cos(t_upper[ii+1])} w/i b({(((diameter_transducer)/2))}, {scale_w})")
					while not ( scale_w > (r_curr*np.cos(t_upper[ii+1])) > ((diameter_transducer)/2) ):
						r_curr = pick_val(scale_bound_l, scale_bound_l + (scale_bound_b*scale_bound_d), deviation_factor)
						app.logger.critical(f"r_curr = {r_curr} ~> x-comp = {r_curr*np.cos(t_upper[ii+1])} w/i b({(((diameter_transducer)/2))}, {scale_w})")
				
					app.logger.critical(f"------------ got past left upper ------------")

					r_upper = np.append(r_upper, r_curr)
				# r_upper.sort()

				# Create xs and ys
				rs = np.concatenate((r_lower, r_upper))
				ts = np.concatenate((t_lower, t_upper))

				# Generate right side of petal
				xs_l = rs*np.cos(ts)
				ys_l = rs*np.sin(ts)

				xs_l = -1*np.flip(xs_l[1:])
				ys_l = np.flip(ys_l[1:])

			# Connect parts
			# app.logger.critical("upper and lower:")
			# app.logger.critical(f"{p_upper} + {p_lower} = {p_upper + p_lower} =?= {(p_upper + p_lower) == 1}")
			# app.logger.critical(f"{p_upper*scale_l} + {p_lower*scale_l} = {(p_upper + p_lower)*scale_l}")
			# if base_append:
			# 	app.logger.critical("yas")
			# else:
			# 	app.logger.critical("naw")
			if base_append:
				xs = np.append(xs_r, b_pts[0])
			else:
				xs = np.append(xs_r, 0)
			xs = np.append(xs, xs_l)
			if base_append:
				ys = np.append(ys_r, b_pts[1])
			else:
				ys = np.append(ys_r, p_upper*scale_l)
			ys = np.append(ys, ys_l)

			# Touchups
			pts = translate_shape_up((xs, ys), p_lower*scale_l)
			fit_pts = xy.make_shape(pts, max_out_len)

			return fit_pts, pts
		except ValueError:
			counter_fail += 1


def gen_amoeba(
	num_points=4, num_points_upper=2, num_points_lower=2,
	width_scale=0.25, length=1000, length_upper=-1, length_lower=-1,
	base_append=1, diameter_transducer=240, radius_extension=120,
	variant="curve", deviation_factor=0, symmetric=True,
	max_out_len=100
	):

	print("haha")

	return "meow"

