#MenuTitle: HEBNibber
# -*- coding: utf-8 -*-
__doc__="""
BroadNibber-ish for Hebrew Glyphs
"""
import objc, math
from GlyphsApp import *
from GlyphsApp.plugins import *


# Test Parameters
shiftX = 0
shiftY = 50
angle = 45

# cases of operation:
# if angle > 0 we can use the copy path method
# if angle is 0 - we need to output a monoline glyph with a straight pen angle
# if one of the shift params is 0 - we nee to produce a monoline with a 45deg pen angle - that is what BroadNibber gives

thisLayer = Glyphs.font.selectedLayers[0]
thisLayer.beginChanges() # increase performance and prevent undo problems

# clean up path and prepare them for copying:
thisLayer.addExtremePoints()
thisLayer.addInflectionPoints()
thisLayer.cleanUpPaths()
thisLayer.correctPathDirection()

# if angle > 0 we can use the copy path method
if angle != 0:
	#shift to rotate around origin
	xCenter = thisLayer.bounds.origin.x + thisLayer.bounds.size.width * 0.5
	yCenter = thisLayer.bounds.origin.y + thisLayer.bounds.size.height * 0.5
	shiftMatrix = [1, 0, 0, 1, -xCenter, -yCenter]
	thisLayer.applyTransform( shiftMatrix )

	# if one of the shift params is 0 - we nee to produce a monoline with a 45deg pen angle - that is what BroadNibber gives
	if shiftX == 0 : shiftX = shiftY
	elif shiftY == 0 : shiftY = shiftX

	# 45deg is a breaking point in the rotation, sin=cos. thus we modolus it
	angle %= 45
	angleRadians = math.radians( angle )
	rotationMatrix = [ math.cos(angleRadians), -math.sin(angleRadians), math.sin(angleRadians), math.cos(angleRadians), 0, 0 ]
	thisLayer.applyTransform( rotationMatrix )

	# rotation = NSAffineTransform.transform()
	# rotation.rotateByDegrees_(angle)
	# thisLayer.transform_checkForSelection_doComponents_(rotation,False,False)

	# shiftMatrix = [1, 0, 0, 1, xCenter, yCenter]
	# thisLayer.applyTransform( shiftMatrix )

	for path in thisLayer.paths:
		if not path.closed: # if an original path
			# copy each path into a newPath
			newPath = path.copy()
			newPath.reverse()
			# shift newPath
			for node in newPath.nodes:
				node.x += shiftX
				node.y += shiftY
			# note on path creation and connection:
			# instead of drawing the copied path by itself,
			# we add its nodes to the original path.
			# this no need to deal with closing paths.
			path.nodes.extend(newPath.nodes)
			path.closed = True

	# cleanup again and connect openings
	thisLayer.cleanUpPaths()
	thisLayer.correctPathDirection()

	#rotate and shift back
	angleRadians = math.radians( -angle )
	rotationMatrix = [ math.cos(angleRadians), -math.sin(angleRadians), math.sin(angleRadians), math.cos(angleRadians), 0, 0 ]
	thisLayer.applyTransform( rotationMatrix )

	# rotation = NSAffineTransform.transform()
	# rotation.rotateByDegrees_(-angle)
	# thisLayer.transform_checkForSelection_doComponents_(rotation,False,False)

	shiftMatrix = [1, 0, 0, 1, xCenter, yCenter]
	thisLayer.applyTransform( shiftMatrix )


# if angle is 0, we can (and need to) use offsetCurveFilter for best results
elif angle == 0:
	offsetCurveFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
				thisLayer, # Layer
				shiftX/2, # offsetX
				shiftY/2, # offsetY
				True, # makeStroke
				False, # autoStroke
				0.5, # position
				None, # error
				None # shadow
				)

thisLayer.endChanges() # close beginChanges
