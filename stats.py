from time import sleep
import pickle
import matplotlib.pyplot as plt
from xy_interpolation import make_shape
from sounds import *

retdict = pickle.load(open('vals.p','rb'))
allvecs = retdict['allvecs']
fits = retdict['fits']
fqs = retdict['fqs']
target = retdict['target']
allpts = []
for vec in allvecs:
    x = vec[:len(vec) // 2]
    y = vec[len(vec) // 2:]
    allpts.append((x,y))

x0 = allpts[0][0]
y0 = allpts[0][1]
xmax = max(map(max, zip(*allpts)[0])) * 1.3
xmin = min(map(min, zip(*allpts)[0])) * 1.3
ymax = max(map(max, zip(*allpts)[1])) * 1.3
ymin = min(map(min, zip(*allpts)[1])) * 1.3

fq0 = fqs[0]

plt.ion()
fig = plt.figure()
ax1 = fig.add_subplot(121)
line1, = ax1.plot(x0, y0, '-')
marks1, = ax1.plot(x0, y0, 'x')
plt.xlabel('Position (mm)')
plt.ylabel('Position (mm)')
ax1.set_xlim([xmin,xmax])
ax1.set_ylim([ymin,ymax])

# add a freq plot
ax2 = fig.add_subplot(122)
line2, = ax2.plot(fq0, '-')
marks2, = ax2.plot(target, '-')
plt.xlabel('Overtone')
plt.ylabel('Frequency (Hz)')
ax2.set_ylim([min(target),max(target)])



# remove duplicates
keys = []
cleanpts, cleanfqs = [], []
for i, pts in enumerate(allpts):
    if pts[0][0] not in keys:
        cleanpts.append(pts)
        keys.append(pts[0][0])
        cleanfqs.append(fqs[i])

raw_input()

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=1)

for i, pts in enumerate(cleanpts):   


     
    marks1.set_xdata(pts[0])
    marks1.set_ydata(pts[1])
    c = make_shape(pts)
    line1.set_xdata(c[0])
    line1.set_ydata(c[1])   
    line2.set_ydata(cleanfqs[i])
    plt.draw()
    play_tone(stream,frequencies=fqs[i],length=0.1)
    
    # sleep(0.2)
stream.close()
p.terminate()
raw_input()
plt.figure()
plt.title('Fitness Convergence')
plt.plot(fits)
plt.yscale('log')
plt.show()
raw_input()