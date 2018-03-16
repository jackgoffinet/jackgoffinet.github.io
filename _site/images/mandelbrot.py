"""http://nbviewer.jupyter.org/gist/jfpuget/16eb22a3c26b6275d9dd"""

__author__ = "Jean-Francois Puget, Jack Goffinet"
__date__ = "February 2017"

import math
import cmath
import numpy as np
import pylab as pl
from collections import deque
from matplotlib import collections  as mc
import soundfile as sf

def mandelbrot(z,horizon,log_horizon,maxiter=80):
    c = z
    for n in range(maxiter):
        az = abs(z)
        if az > horizon:
            return n - np.log(np.log(az))/np.log(2) + log_horizon
        z = z*z + c
    return -1

def mandelbrot_set(xmin,xmax,ymin,ymax,width,height,maxiter):
    horizon = 2.0 ** 40
    log_horizon = np.log(np.log(horizon))/np.log(2)
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = mandelbrot(r1[i] + 1j*r2[j],maxiter,horizon, log_horizon)
    return (r1,r2,n3)

def unravel(z, delta, epsilon, theta, target_color, horizon, log_horizon):
    theta -= 0.25*math.pi
    temp_z = z + delta*(cmath.exp(1j*theta))
    color = mandelbrot(temp_z,horizon,log_horizon)
    delta_theta = 0.25*math.pi
    if color == -1:
        print "Error"
        quit()
    while color > target_color:
        delta *= 0.99
        temp_z = z + delta*(cmath.exp(1j*theta))
        color = mandelbrot(temp_z,horizon,log_horizon)
    i = 0
    while abs(color - target_color) > epsilon:
        i += 1
        if color > target_color:
            theta -= delta_theta
        else:
            theta += delta_theta
        temp_z = z + delta*(cmath.exp(1j*theta))
        color = mandelbrot(temp_z,horizon,log_horizon)
        delta_theta /= 2.0
        if i > 10:
            delta_theta = 0.25*math.pi
            delta *= 0.99
            theta -= 0.25*math.pi
            temp_z = z + delta*(cmath.exp(1j*theta))
            i = 0
    return temp_z, theta, delta

# def get_sample(z1, z2, target_color, horizon, log_horizon):
#     unit_vector = cmath.exp(1j*math.pi/2.0)*(z2-z1)/abs(z2-z1)
#     # delta = 0.01
#     delta = 0.01
#     temp_z = 0.5*(z1 + z2)
#     temp_c = mandelbrot(temp_z, horizon, log_horizon)
#     best = (temp_z, 100)
#     while True:
#         # print (temp_c, temp_z, delta)
#         if abs(temp_z-0.5*(z1+z2)) > 1.0:
#             return abs(0.5*(z1+z2)-best[0])
#         diff = target_color - temp_c
#         if abs(diff) < best[1]:
#             best = (temp_z, diff)
#         if abs(diff) < 0.01:
#             return abs(0.5*(z1+z2)-temp_z)
#         if temp_c == -1 or diff < 0:
#             temp_z -= unit_vector*delta
#             delta /= 2.0
#         temp_z += unit_vector*delta
#         temp_c = mandelbrot(temp_z, horizon, log_horizon)

def get_sample(z1, z2, target_color, horizon, log_horizon):
    unit_vector = cmath.exp(1j*math.pi/2.0)*(z2-z1)/abs(z2-z1)
    # delta = 0.01
    delta = 0.01
    temp_z = 0.5*(z1 + z2)
    temp_c = mandelbrot(temp_z, horizon, log_horizon)
    last_c = temp_c - 1.0
    i = 0
    while True:
        # print (temp_c, temp_z, delta)
        diff = target_color - temp_c
        if abs(diff) < 0.01:
            return abs(0.5*(z1+z2)-temp_z)
        if temp_c == -1 or abs(last_c - target_color) < abs(temp_c - target_color):
            i += 1
            temp_z -= 0.5*unit_vector*delta
            delta /= 2.0
            if i == 8:
                return abs(0.5*(z1+z2)-temp_z)
        else:
            temp_z += unit_vector*delta
            last_c = temp_c
        temp_c = mandelbrot(temp_z, horizon, log_horizon)

def to_point(z):
    return (z.real, z.imag)

def smooth(point_list):
    """discrete gaussian smoothing"""
    kernel = np.asarray([0.06136, 0.24477, 0.38774, 0.24477, 0.06136])
    queue = deque([point_list[0], point_list[1]])
    for i in range(len(point_list)-4):
        queue.append(np.dot(kernel,point_list[i:i+5]))
        point_list[i] = queue.popleft()
    for i in [len(point_list)-4, len(point_list)-3]:
        point_list[i] = queue.popleft()

def normalize(audio):
    avg = 0.001*np.sum(audio[:1000])
    out = np.copy(audio)
    out[:1000] -= avg
    for i in range(1000, len(audio)):
        avg += 0.001*(audio[i]-audio[i-1000])
        out[i] -= avg
    out[:1000] /= np.max(np.abs(out[:1000]))
    for i in range(1000, len(audio)):
        out[i] /= np.max(np.abs(out[i-1000:i]))
    return out

def complex_to_tuple(z):
    return (z.real, z.imag)

def argmin(iterable):
	min_element = iterable[0]
	argmin = 0
	for i in range(1, len(iterable)):
		if iterable[i] > min_element:
			min_element = iterable[i]
			argmin = i
	return argmin

horizon = 2.0 ** 40
log_horizon = np.log(np.log(horizon))/np.log(2)

# print get_sample(-1j*1.5, 0.01-1j*1.5, 10.0, horizon, log_horizon)
# quit()
target_color = 4.05098428962
z = -4.0-4.0*1j
delta = 0.1
epsilon = 0.01
theta = 4.96040945304-2*math.pi
l = [z]
colors = [4.05098428962]
iterations = 41000*58
for i in range(iterations):
    if i%41000==0:
        print str(i/41000)+" seconds"
    # target_color += 0.00003
    target_color *= 1.000001
    colors.append(target_color)
    z, theta, delta = unravel(z,delta,epsilon,theta,target_color,horizon,log_horizon)
    l.append(z)
print "target_color: "+str(target_color)
# audio
smooth(l)

audio = []
for i in range(iterations-1):
    if i%41000==0:
        print str(i/41000)+" seconds"
    audio.append(get_sample(l[i],l[i+1],0.2+colors[i]+0.01*colors[i]*colors[i],horizon,log_horizon))

smooth(audio)
audio = normalize(np.asarray(audio))
sf.write("mandelbrot6.wav",audio,41000)
