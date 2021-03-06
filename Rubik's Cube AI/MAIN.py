import pygame as pg
import numpy as np
from time import perf_counter as pf
from os import system
from Cube_functions import *
from AI import *

_ = system("cls")


W = 700
theta = np.pi/2		# field of view
Zv = 1000
f = W/np.tan(theta/2)
win = pg.display.set_mode((W, W))
pg.display.set_caption("Rubik's Cube AI")
pg.font.init()
font = pg.font.SysFont("georgia", 20)


# creating the cube
s = 50		# size of each small cube
surfaces = np.zeros((6, 3, 3, 4, 3))	# 6 faces, 3x3 squares each, 4 (x,y,z) coordinates for each squares
# left face, centre
surfaces[0, 1, 1] = np.array([[-3*s, -s, s], [-3*s, -s, -s], [-3*s, s, -s], [-3*s, s, s]])
# front face, centre
surfaces[1, 1, 1] = np.array([[-s, s, -3*s], [-s, -s, -3*s], [s, -s, -3*s], [s, s, -3*s]])
# top face, centre
surfaces[2, 1, 1] = np.array([[-s, -3*s, -s], [-s, -3*s, s], [s, -3*s, s], [s, -3*s, -s]])

for i in range(3):
	for j in range(3):
		# left face
		surfaces[0, i, j] = surfaces[0, 1, 1]
		surfaces[0, i, j, :, 2] -= (i-1)*2*s
		surfaces[0, i, j, :, 1] += (j-1)*2*s

		# front face
		surfaces[1, i, j] = surfaces[1, 1, 1]
		surfaces[1, i, j, :, 0] += (i-1)*2*s
		surfaces[1, i, j, :, 1] += (j-1)*2*s

		# top face
		surfaces[2, i, j] = surfaces[2, 1, 1]
		surfaces[2, i, j, :, 0] += (i-1)*2*s
		surfaces[2, i, j, :, 2] -= (j-1)*2*s

# right face
surfaces[3] = surfaces[0]
surfaces[3, ..., 0] += 6*s
surfaces[3, ..., 2] *= -1

# back face
surfaces[4] = surfaces[1]
surfaces[4, ..., 2] += 6*s
surfaces[4, ..., 0] *= -1

# bottom face
surfaces[5] = surfaces[2]
surfaces[5, ..., 1] += 6*s
surfaces[5, ..., 0] *= -1


"""
initial faces:
0 -> left, red
1 -> front, green
2 -> top, yellow
3 -> right, orange
4 -> back, blue
5 -> bottom, white
"""

clrs = {0:(255, 0, 38), 1:(36, 255, 50), 2:(255, 238, 0), 3:(255, 100, 0), 4:(21, 113, 243), 5:(255, 255, 255)}
colors = np.zeros((54, 3))
for i in clrs.keys():
	colors[i*9:i*9+9] = clrs[i]

instructions = ["Shuffle: S", "Solve: A", "Rotate Cube: Arrow Keys"]

solves = 0
success = 0
avgf2l = avgcrs = avgoll = avgpll = avg = 0.0

def play(moves_to_take, anim):
	global alpha, beta
	for x in moves_to_take:
		if x<12:
			if anim:
				for _ in range(turn_speed):
					for event in pg.event.get():
						if event.type == pg.QUIT:
							exit()

					keyp = pg.key.get_pressed()
					if keyp[pg.K_UP]:
						beta += inc
					elif keyp[pg.K_DOWN]:
						beta -= inc
					if keyp[pg.K_LEFT]:
						alpha += inc
					elif keyp[pg.K_RIGHT]:
						alpha -= inc
					turn_face(x, np.pi/turn_speed/2, surfaces)
					draw()
				turn_face(x, -np.pi/2, surfaces)

			moves[x](colors)
		elif x==12:
			change_front(0, colors)
			alpha += np.pi/2
		elif x==13:
			change_front(1, colors)
			alpha -= np.pi/2
		# draw()

def AI(animate=True):
	t = pf()
	n = 0
	pll = 0
	f2l = 0
	crs = 0
	oll  = 0

	if not check_solve(colors):
		moves_to_take = cross(colors)
		n += np.sum(np.array(moves_to_take)<12)
		crs += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = align_cross(colors)
		n += np.sum(np.array(moves_to_take)<12)
		crs += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = corners(colors)
		n += np.sum(np.array(moves_to_take)<12)
		f2l += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = edges(colors)
		n += np.sum(np.array(moves_to_take)<12)
		f2l += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = yellow_cross(colors)
		n += np.sum(np.array(moves_to_take)<12)
		oll += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = yellow_face(colors)
		n += np.sum(np.array(moves_to_take)<12)
		oll += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = pll_corners(colors)
		n += np.sum(np.array(moves_to_take)<12)
		pll += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

		moves_to_take = pll_edges(colors)
		n += np.sum(np.array(moves_to_take)<12)
		pll += np.sum(np.array(moves_to_take)<12)
		play(moves_to_take, animate)

	t = pf()-t

	global solves, success, avgf2l, avgcrs, avgoll, avgpll, avg
	solves += 1

	if check_solve(colors):
		success += 1

	avgf2l += f2l
	avgcrs += crs
	avgoll += oll
	avgpll += pll
	avg += n

	print(f"{success}/{solves} --  {round(t*1, 3)} seconds, {n} moves. Cross: {crs}, F2L: {f2l}, OLL: {oll}, PLL: {pll}")

def shuffle(animate=True, moves=50):
	x = np.random.randint(0, 12, size=moves)
	play(x, animate)

# drawing
def draw_surface(s, v):
	# s -> 4, 2-D coordinates in cyclic order
	pg.draw.polygon(win, colors[v], s)
	for i in range(3):
		pg.draw.line(win, (32, 32, 32), s[i], s[i+1], 6)
	pg.draw.line(win, (32, 32, 32), s[0], s[3], 6)
	"""details of each square
	if v==13:
		t = font.render("Front", True, (0,0,0))
		win.blit(t, np.mean(s, axis=0)-np.array([t.get_width()/2, t.get_height()/2]))
	if v==22:
		t = font.render("Up", True, (0,0,0))
		win.blit(t, np.mean(s, axis=0)-np.array([t.get_width()/2, t.get_height()/2]))
	t = font.render(str(v), True, (0,0,0))
	win.blit(t, np.mean(s, axis=0)-np.array([t.get_width()/2, t.get_height()/2]))
	"""
	
def draw():
	win.fill(((0, 0, 0)))
	cube, z = project_surfaces(np.copy(surfaces))

	dc = {z[x] : x for x in range(54)}
	z.sort()

	for k in reversed(z):
		v = dc[k]
		draw_surface(cube[v], v)

	for i, t in enumerate(instructions):
		text = font.render(t, True, (255, 255, 255))
		win.blit(text, (10, i*30 + 10))

	pg.display.update()

def project_surfaces(cube):
	h = (cube[..., 0]**2 + cube[..., 2]**2)**0.5
	a = np.arctan(cube[..., 2]/(cube[..., 0] + 1e-8)) - alpha
	c = np.where(cube[..., 0]>=0, 1, -1)
	cube[..., 0] = c*h*np.cos(a)
	cube[..., 2] = c*h*np.sin(a)

	h = (cube[..., 1]**2 + cube[..., 2]**2)**0.5
	a = np.arctan(cube[..., 2]/(cube[..., 1] + 1e-8)) - beta
	c = np.where(cube[..., 1]>=0, 1, -1)
	cube[..., 1] = c*h*np.cos(a)
	cube[..., 2] = c*h*np.sin(a)

	z = np.mean(cube[..., 2], axis=3).reshape(54)
	
	return W//2 + (f*cube[..., :2]/(Zv+cube[..., 2:])).reshape(54, 4, 2), z


alpha, beta = np.pi/4 + 0.01, -np.pi/4 + 0.01				# default viewing angles
inc = 0.02													# angle increase on pressing arrow keys
turn_speed = 25												# MUST BE A POWER OF 5 (5, 25, 125, 625...); less is more (it is actually the number of frames spent per turn)
wait = 150													# wait (in msec) after some functions

# its = 100
# for _ in range(its):
# 	shuffle(False)
# 	# draw()
# 	pg.time.delay(15)
# 	AI(False)
# 	# draw()
# 	pg.time.delay(15)

# print(f"\nAVERAGE MOVES -- Cross: {round(avgcrs/its)}, F2L: {round(avgf2l/its)}, OLL: {round(avgoll/its)}, PLL: {round(avgpll/its)}, Total: {round(avg/its)}\n")

while True:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			exit()
	keyp = pg.key.get_pressed()

	if keyp[pg.K_UP]:
		beta += inc
	if keyp[pg.K_DOWN]:
		beta -= inc
	if keyp[pg.K_LEFT]:
		alpha += inc
	if keyp[pg.K_RIGHT]:
		alpha -= inc

	if keyp[pg.K_s]: # and (keyp[pg.K_LSHIFT] or keyp[pg.K_RSHIFT]):
		shuffle()
		pg.time.delay(wait)

	if keyp[pg.K_a]: # and (keyp[pg.K_LCTRL] or keyp[pg.K_RCTRL]):
		AI()
		pg.time.delay(wait)

	draw()

