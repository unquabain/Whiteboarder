#!/usr/bin/env python
import cairo
import os, sys, pygame
from pygame.locals import *
from whiteboard import Scene


scene = Scene()
scene.start_beat("Beat")
scene.current_beat.start_subbeat()
movemode = False
startmove = False
while 1:
	for event in pygame.event.get():
		if event.type == MOUSEBUTTONDOWN:
			print "MOUSEBUTTONDOWN"
			if movemode:
				startmove = True
				d = pygame.mouse.get_rel()
			else:
				scene.current_beat.current_subbeat.start_stroke(scene.brush)
				scene.current_beat.current_subbeat.current_stroke.record_event(
					scene.camera.point_out(pygame.mouse.get_pos())
				)
		elif event.type == MOUSEMOTION:
			if movemode:
				if startmove:
					delta = pygame.mouse.get_rel()
					scene.move_camera(delta)
			else:
				if scene.current_beat.current_subbeat.current_stroke is not None:
					scene.current_beat.current_subbeat.current_stroke.record_event(
						scene.camera.point_out(pygame.mouse.get_pos())
					)
		elif event.type == MOUSEBUTTONUP:
			print "MOUSEBUTTONUP"
			if movemode:
				startmove = False
			else:
				scene.current_beat.current_subbeat.end_stroke()
		elif event.type == KEYDOWN:
			if event.key == 109:
				movemode = not movemode
				print "movemode %s"%movemode
			elif event.key == 61:
				print "Zoom In"
				scene.scale_camera(1.1)
			elif event.key == 45:
				print "Zoom Out"
				scene.scale_camera(1/1.1)
			elif event.key == 32:
				print "New Subbeat"
				scene.current_beat.end_subbeat()
				scene.current_beat.start_subbeat()
			else:
				print event.key, event.unicode
		elif event.type == QUIT:
			sys.exit()
	# screen.blit(background, (0, 0))
	scene.draw()
