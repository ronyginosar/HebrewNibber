#MenuTitle: HEBNibber
# -*- coding: utf-8 -*-
__doc__="""
BroadNibber-ish for Hebrew Glyphs
"""
import objc, math, copy
from GlyphsApp import *
from GlyphsApp.plugins import *

# Master Definitions
m1_width = 60
m1_height = 100
m1_angle = 45

m2_width = 85
m2_height = 180
m2_angle = 45

m3_width = 120
m3_height = 160
m3_angle = 45

m4_width = 75
m4_height = 90
m4_angle = 45

m5_width = 70
m5_height = 70
m5_angle = 0

m6_width = 50
m6_height = 110
m6_angle = 0

m7_width = 55
m7_height = 190
m7_angle = 0

m8_width = 130
m8_height = 125
m8_angle = 0

# cases of operation:
# if angle > 0 we can use the copy path method
# if angle is 0 - we need to output a monoline glyph with a straight pen angle
# if one of the shift params is 0 - we nee to produce a monoline with a 45deg pen angle - that is what BroadNibber gives

pathLayer = Glyphs.font.selectedLayers[0].parent.layers[8] # layer 0
# clean up path and prepare them for copying:
pathLayer.addExtremePoints()
pathLayer.addInflectionPoints()
pathLayer.cleanUpPaths()
pathLayer.correctPathDirection()

m1 = [m1_width , m1_height , m1_angle]
m2 = [m2_width , m2_height , m2_angle]
m3 = [m3_width , m3_height , m3_angle]
m4 = [m4_width , m4_height , m4_angle]
m5 = [m5_width , m5_height , m5_angle]
m6 = [m6_width , m6_height , m6_angle]
m7 = [m7_width , m7_height , m7_angle]
m8 = [m8_width , m8_height , m8_angle]
m = [m1, m2, m3, m4, m5, m6, m7, m8]

# thisLayer.beginChanges() # increase performance and prevent undo problems

OUTPUTLAYERS = range(0, 8)

# copy path to master
for layer in OUTPUTLAYERS:
 	currMaster = Glyphs.font.selectedLayers[0].parent.layers[layer].background
	currMaster.paths = []
	currMaster.components = []

 	if (pathLayer.paths):
 		currMaster.paths = copy.copy(pathLayer.paths)

 	if (pathLayer.components):
		currMaster.components = copy.copy(pathLayer.components)

	currMaster.guides = copy.copy(pathLayer.guides)

 	if (pathLayer.anchors):
		currMaster.anchors = copy.copy(pathLayer.anchors)

	width = m[layer][0]
	height = m[layer][1]
	angle = m[layer][2]

	# if angle > 0 we can use the copy path method
	if angle != 0:
		#shift to rotate around origin
		xCenter = currMaster.bounds.origin.x + currMaster.bounds.size.width * 0.5
		yCenter = currMaster.bounds.origin.y + currMaster.bounds.size.height * 0.5
		shiftMatrix = [1, 0, 0, 1, -xCenter, -yCenter]
		currMaster.applyTransform( shiftMatrix )

		# if one of the shift params is 0 - we nee to produce a monoline with a 45deg pen angle - that is what BroadNibber gives
		if width == 0 : width = height
		elif height == 0 : height = width

		# 45deg is a breaking point in the rotation, sin=cos. thus we modolus it
		angle %= 45
		angleRadians = math.radians( angle )
		rotationMatrix = [ math.cos(angleRadians), -math.sin(angleRadians), math.sin(angleRadians), math.cos(angleRadians), 0, 0 ]
		currMaster.applyTransform( rotationMatrix )

		# rotation = NSAffineTransform.transform()
		# rotation.rotateByDegrees_(angle)
		# thisLayer.transform_checkForSelection_doComponents_(rotation,False,False)

		# shiftMatrix = [1, 0, 0, 1, xCenter, yCenter]
		# thisLayer.applyTransform( shiftMatrix )

		for path in currMaster.paths:
			if not path.closed: # if an original path
				# copy each path into a newPath
				newPath = path.copy()
				newPath.reverse()
				# shift newPath
				for node in newPath.nodes:
					node.x += width
					node.y += height
				# note on path creation and connection:
				# instead of drawing the copied path by itself,
				# we add its nodes to the original path.
				# this no need to deal with closing paths.
				path.nodes.extend(newPath.nodes)
				path.closed = True

		# cleanup again and connect openings
		currMaster.cleanUpPaths()
		currMaster.correctPathDirection()

		#rotate and shift back
		angleRadians = math.radians( -angle )
		rotationMatrix = [ math.cos(angleRadians), -math.sin(angleRadians), math.sin(angleRadians), math.cos(angleRadians), 0, 0 ]
		currMaster.applyTransform( rotationMatrix )

		# rotation = NSAffineTransform.transform()
		# rotation.rotateByDegrees_(-angle)
		# thisLayer.transform_checkForSelection_doComponents_(rotation,False,False)

		shiftMatrix = [1, 0, 0, 1, xCenter, yCenter]
		currMaster.applyTransform( shiftMatrix )


	# if angle is 0, we can (and need to) use offsetCurveFilter for best results
	elif angle == 0:
		offsetCurveFilter = NSClassFromString("GlyphsFilterOffsetCurve")
		offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
					currMaster, # Layer
					width/2, # offsetX
					height/2, # offsetY
					True, # makeStroke
					False, # autoStroke
					0.5, # position
					None, # error
					None # shadow
					)

# thisLayer.endChanges() # close beginChanges
