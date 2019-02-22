## Sound Sculpture via Web

Uses a flask framework to run optimizations online

Prepared to host online via a docker-compose configuration

Based on code by /evanprs for optimization



input format:
curl -H "Content-Type: application/json" \
    --request POST \
    --data '{
	'material': 'galvanized',
	'density': 0.007850,
	'modulus': 200000e6,
	'ratio': 0.3,
	'gauge': 8,
	'target': [ 440.0, 550.0 ],
	'scale': 500,
	'grade': 'coarse',
	'ctrlpoints': 5
    } \
    0.0.0.0:5000/api/get_cll_to_ths

output format:
json token
