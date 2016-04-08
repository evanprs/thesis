from time import sleep
import optimize
import pickle
import matplotlib.pyplot as plt
from xy_interpolation import make_shape

retdict = pickle.load(open('vals.p','rb'))
xopt = retdict['xopt']
allvecs = retdict['allvecs']
fits = retdict['fits']
allpts = []
for vec in allvecs:
    x = vec[:len(vec) // 2]
    y = vec[len(vec) // 2:]
    allpts.append((x,y))

x0 = allpts[0][0]
y0 = allpts[0][1]

plt.ion()
fig = plt.figure()
plt.title('Development of Shape')
ax = fig.add_subplot(111)
line, = ax.plot(x0, y0, '-')
marks, = ax.plot(x0, y0, 'x')

# remove duplicates
keys = []
cleanpts = []
for pts in allpts:
    if pts[0][0] not in keys:
        cleanpts.append(pts)
        keys.append(pts[0][0])

for pts in cleanpts:    
    marks.set_xdata(pts[0])
    marks.set_ydata(pts[1])
    c = make_shape(pts)
    line.set_xdata(c[0])
    line.set_ydata(c[1])    
    plt.draw()
    sleep(0.1)
    
raw_input()
plt.figure()
plt.title('Fitness Convergence')
plt.plot(fits)
plt.yscale('log')
plt.show()
raw_input()