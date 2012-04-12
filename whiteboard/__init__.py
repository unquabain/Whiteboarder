from numpy import *
from numpy.linalg import *
from whiteboard.trig import Radian, Angle
import os, sys, pygame
from pygame.locals import *
import cairo
from datetime import datetime, timedelta
import copy
class Brush(object):
	def __init__(self, color, scale, aspect, rotation):
		self.color = color
		self.scale = scale
		self.aspect = aspect
		self.rotation = rotation

		width = aspect
		height = 1
		left = width/(-2.)
		top = height/(-2.)
		right = left+width
		bottom = top+height

		c = Camera()
		c.scale(scale)
		c.rotate(rotation)

		pp = c.points_in( (
			( left, top ), 
			( right, top ),
			( left, bottom ),
			( right, bottom )
		) )
		bbtop = min( ( p[1] for p in pp ) )
		bbbottom = max( ( p[1] for p in pp ) )
		bbleft = min( ( p[0] for p in pp ) )
		bbright = max( ( p[0] for p in pp ) )
		self.bbox = pygame.Rect( bbleft, bbtop, bbright - bbleft, bbbottom - bbtop )
		self.points = pp
		



class Camera(object):
	def __init__(self):
		self.matrix = array([
			[1., 0., 0.],
			[0., 1., 0.],
			[0., 0., 1.]
		])
		self.dirty_rectangles = []
	def move(self, delta):
		mm = array([
			[1., 0., delta[0]],
			[0., 1., delta[1]],
			[0., 0., 1. ]
		])
		self.matrix = dot(self.matrix, mm)
		print self.matrix
	def rotate(self, angle):
		if not isinstance(angle, Angle):
			angle = Radian(angle)
		mm = array([
			[ angle.cos(), -angle.sin(), 0. ],
			[ angle.sin(), angle.cos(),  0. ],
			[ 0.,          0.,           1. ]
		])
		self.matrix = dot(self.matrix, mm)
	def scale(self, x, y=None):
		if y is None: y = x
		mm = array([
			[ x, 0., 0. ],
			[ 0., y, 0. ],
			[ 0., 0., 1. ]
		])
		self.matrix = dot(self.matrix, mm)
	def point_in(self, point):
		pm = array([
			[point[0]],
			[point[1]],
			[1.]
		])
		pt = dot(self.matrix, pm)
		return pt[0][0], pt[1][0]

	def vector_in(self, vector):
		mm = array([
			[ self.matrix[0][0], self.matrix[0][1] ],
			[ self.matrix[1][0], self.matrix[1][1] ]
		])
		pm = array([
			[vector[0]],
			[vector[1]]
		])
		pt = dot(mm, pm)
		return pt[0][0], pt[1][0]
	def vector_out(self, vector):
		mm = array([
			[ self.matrix[0][0], self.matrix[0][1] ],
			[ self.matrix[1][0], self.matrix[1][1] ]
		])
		pm = array([
			[vector[0]],
			[vector[1]]
		])
		pt = dot(inv(mm), pm)
		return pt[0][0], pt[1][0]

	def points_in(self, points):
		return [ self.point_in(pp) for pp in points ]
	def point_out(self, point):
		pm = array([
			[point[0]],
			[point[1]],
			[1.]
		])
		pt = dot(inv(self.matrix), pm)
		return pt[0][0], pt[1][0]
	def points_out(self, points):
		return [ self.point_out(pp) for pp in points ]
	def rect_in(self, rect):
		p = (
			( rect.left, rect.top ),
			( rect.left + rect.width, rect.top ),
			( rect.left + rect.width, rect.top + rect.height),
			( rect.left , rect.top + rect.height )
		)
		pm = self.points_in(p)
		
		bp = (
			min( ( p[0] for p in pm ) ),
			max( ( p[0] for p in pm ) ),
			min( ( p[1] for p in pm ) ),
			max( ( p[1] for p in pm ) ),
		)
		return pygame.Rect(
			bp[0],
			bp[2],
			bp[1]-bp[0],
			bp[3]-bp[2]
		)
	def rect_out(self, rect):
		p = (
			( rect.left, rect.top ),
			( rect.left + rect.width, rect.top ),
			( rect.left + rect.width, rect.top + rect.height),
			( rect.left , rect.top + rect.height )
		)
		pm = self.points_out(p)
		
		bp = (
			min( ( p[0] for p in pm ) ),
			max( ( p[0] for p in pm ) ),
			min( ( p[1] for p in pm ) ),
			max( ( p[1] for p in pm ) ),
		)
		return pygame.Rect(
			bp[0],
			bp[2],
			bp[1]-bp[0],
			bp[3]-bp[2]
		)
	def draw(self, brush, points):
		points = self.points_in(points)

		def dist(l, r):
			return sqrt(
				(r[0]-l[0])*(r[0]-l[0])
				+
				(r[1]-l[1])*(r[1]-l[1])
			)
		def slope( l, r) :
			return (
				( r[1] - l[1] )
				/
				(r[0] - l[0] )
			)
		def angle( l, r ) :
			if r[0] == l[0]:
				a = math.pi/2. 
				if r[1]<l[1]:
					a += math.pi
			elif r[1] == l[1]:
				a = 2.*math.pi
			else:
				a = arctan(slope(l , r))
			if l[0]>r[0]:
				a += math.pi
			if a < 0.:
				a += 2.0*math.pi
			elif a > 2.0*math.pi:
				a -= 2.0*math.pi
			return Radian(a)
				
				
		context = self.context
		context.new_path()

		context.set_source_rgb(*brush.color)
		context.set_line_width(brush.scale * self.matrix[0][0])
		if len(points) == 4:
			d1 = dist(points[0], points[1])
			d2 = dist(points[1], points[2])
			d3 = dist(points[2], points[3])

			a1 = angle(points[0], points[1])
			a2 = angle(points[1], points[2])
			a3 = angle(points[2], points[3])

			while abs(a1-a2)>3*math.pi/2.:
				if a1 < a2:
					a1 += 2.*math.pi
				else:
					a2 += 2.*math.pi
			while abs(a2-a3)>3*math.pi/2.:
				if a2 < a3:
					a2 += 2.*math.pi
				else:
					a3 += 2.*math.pi
			aa1 = Radian(((a1 * d1)+(a2*d2))/(d1+d2))


			aa2 = Radian(((a2 * d2)+(a3*d3))/(d2+d3))

			if abs(a2-a3)>3*math.pi/2.:
				aa2 = Radian(math.pi-aa2)
				context.set_source_rgb(0, 255, 0)


			cp1 = ( points[1][0] + aa1.cos()*d2/3., points[1][1] + aa1.sin()*d2/3. )
			cp2 = ( points[2][0] - aa2.cos()*d2/3., points[2][1] - aa2.sin()*d2/3. )

			args = [ coord for p in ( cp1, cp2, points[2] ) for coord in p ]
			if reduce(
				lambda x, y: { True: True, False: x }[math.isnan(y)],
				args,
				False
			):
				context.set_source_rgb(255, 0, 0)
				context.move_to(*(points[1]))
				context.line_to(*(points[2]))
			else:
			
				context.move_to(*(points[1]))
				context.curve_to(*args)

				"""
				context.stroke()

				context.set_line_width(1.5)
				context.new_path()
				context.move_to(*points[1])
				context.line_to(*cp1)
				context.set_source_rgb(0, 0, 200)
				context.stroke()
				context.new_path()
				context.move_to(*points[2])
				context.line_to(*cp2)
				context.set_source_rgb(255, 0, 0)
				"""
			context.stroke()


		# self.dirty_rectangles.append( pygame.draw.line(self.screen, brush.color, p1, p2, brush.scale).inflate(scale) )

			

class CameraKeyframe(Camera):
	def __init__(self, time, isstop=True):
		super(CameraKeyframe, self).__init__()
		self.time = time
		self.isstop = isstop

class StrokeEvent(object):
	def __init__(self, time, pos, pressure = 1.0):
		self.time = time
		self.pos = pos
		self.pressure = pressure

class Stroke(object):
	def __init__(self, time, brush):
		self.time = time
		self.start = datetime.now()
		self.events = []
		self.brush = copy.copy(brush)
		self.drawn = 0
	def record_event(self, pos, pressure=1.0):
		self.events.append(StrokeEvent( datetime.now() - self.start, pos, pressure ) )
		return self.events[-1]

	def draw(self, camera):
		for i in range(len(self.events)):
			points = self.events[i:i+4]
			camera.draw(self.brush, [ p.pos for p in points ])
		self.drawn = len(self.events)
	def draw_current(self, camera):
		for i in range(self.drawn, len(self.events)):
			camera.draw(self.brush, [ p.pos for p in self.events[i-4:i] ])
		self.drawn = len(self.events)


class SubBeat(object):
	def __init__(self, number):
		self.number = number
		self.strokes = []
		self.current_stroke = None
		self.started = datetime.now()
	def start_stroke(self, brush):
		time = datetime.now() - self.started
		if self.current_stroke is not None:
			self.strokes.append(self.current_stroke)
		self.current_stroke = Stroke(time, brush)
		return self.current_stroke
	def end_stroke(self):
		self.strokes.append(self.current_stroke)
		self.current_stroke = None

	def draw(self, camera):
		for s in self.strokes:
			if s is not None:
				s.draw(camera)
	def draw_current(self, camera):
		if self.current_stroke is not None:
			self.current_stroke.draw_current(camera)



class Beat(object):
	def __init__(self, name, number):
		self.name = name
		self.number = number
		self.subbeats = []
		self.current_subbeat = None
	def start_subbeat(self):
		if self.current_subbeat is None:
			self.current_subbeat = SubBeat(0)
		else:
			self.subbeats.append(self.current_subbeat)
			self.current_subbeat = SubBeat(self.current_subbeat.number + 1)
		return self.current_subbeat
	def end_subbeat(self):
		if self.current_subbeat is not None:
			self.current_subbeat.end_stroke()
			self.subbeats.append(self.current_subbeat)
			self.current_subbeat = None

	def draw(self, camera):
		for sb in self.subbeats:
			sb.draw(camera)
		if self.current_subbeat is not None:
			self.current_subbeat.draw(camera)
	def draw_current(self, camera):
		if self.current_subbeat is not None:
			self.current_subbeat.draw_current(camera)


class Scene(object):
	def __init__(self):
		self.beats = []
		self.camera = Camera()
		self.brush = Brush( (0, 0, 0), 3, 0.33, Radian(math.pi/4.) )
		self.current_beat = None
		self.cached_surface = None
		self.camera_moved = True
		pygame.init()

		ar = 16.0/9.0

		size = width, height = 1080, int(1080/ar)
		self.size = size
		self.width = width
		self.height = height

		self.scale_camera(1.0,1.0)
		screen = pygame.display.set_mode(size, 0, 32)
		self.screen = screen
		pixels = pygame.surfarray.pixels2d(screen)
		self.cairo_surface = cairo.ImageSurface.create_for_data(
			pixels.data, cairo.FORMAT_RGB24, width, height
		)


	def start_beat(self, name=None):
		if name is None:
			if self.current_beat is None:
				name = "Beat"
				number = 0
			else:
				name = self.current_beat.name
				number = self.current_beat.number + 1
		else:
			number = 0

		if self.current_beat is not None:
			self.beats.append(self.current_beat)
		self.current_beat = Beat(name, number)
		return self.current_beat

	def end_beat(self):
		if self.current_beat is not None:
			self.current_beat.end_subbeat()
			self.beats.append(self.current_beat)
			self.current_beat = None

	def draw(self):
		self.camera.screen = self.screen
		self.camera.context = cairo.Context(self.cairo_surface)
		self.camera.dirty_rectangles = []
		if self.camera_moved:
			self.camera.context.set_source_rgb(255, 255, 255)
			self.camera.context.rectangle(0, 0, self.width, self.height)
			self.camera.context.fill()
			for b in self.beats:
				b.draw(self.camera) 
			if self.current_beat is not None:
				self.current_beat.draw(self.camera)
				self.current_beat.draw_current(self.camera)
			pygame.display.update()
			self.camera_moved = False
		else:
			if self.current_beat is not None:
				self.current_beat.draw_current(self.camera)
			pygame.display.update()
			# pygame.display.update(self.camera.dirty_rectangles)
	def move_camera(self, delta):
		self.camera.move(self.camera.vector_out(delta))
		# self.camera.move(delta)
		self.camera_moved = True
	def scale_camera(self, scalex, scaley=None):
		cx = self.width/2.
		cy = self.height/2.
		p1 = self.camera.point_out((cx, cy))
		# self.camera.move([-c for c in p])
		self.camera.scale(scalex, scaley)
		p2 = self.camera.point_out((cx, cy))
		self.camera.move(( p2[0]-p1[0], p2[1]-p1[1] ))
		# self.camera.move(p)
		self.camera_moved = True
	def rotate_camera(self, angle):
		self.camera.rotate(angle)
		self.camera_moved = True

