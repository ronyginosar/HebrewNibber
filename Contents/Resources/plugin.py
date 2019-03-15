# encoding: utf-8

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#	BroadNibber-ish for Hebrew Glyphs
#
###########################################################################################################

import objc, math
from GlyphsApp import *
from GlyphsApp.plugins import *

class HEBNibber(FilterWithDialog):

	# Definitions of IBOutlets - GUI elements:

	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()
	# Text field in dialog
	widthField = objc.IBOutlet()
	heightField = objc.IBOutlet()
	angleField = objc.IBOutlet()

	def settings(self):
		self.menuName = Glyphs.localize({'en': u'HEBNibber'})
		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize({'en': u'Apply'})
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)

	# On dialog show
	def start(self):

		# Set default value
		# Glyphs.registerDefault('com.myname.myfilter.value', 15.0)
		NSUserDefaults.standardUserDefaults().registerDefaults_({
			"com.ronyginosar.HEBNibber.width": "50",
			"com.ronyginosar.HEBNibber.height": "10",
			"com.ronyginosar.HEBNibber.angle": "30",
		})

		# Set value of text field
		# self.myTextField.setStringValue_(Glyphs.defaults['com.myname.myfilter.value'])
		self.widthField.setStringValue_(Glyphs.defaults['com.ronyginosar.HEBNibber.width'])
		self.heightField.setStringValue_(Glyphs.defaults['com.ronyginosar.HEBNibber.height'])
		self.angleField.setStringValue_(Glyphs.defaults['com.ronyginosar.HEBNibber.angle'])

		# Set focus to text field
		self.widthField.becomeFirstResponder()

	# Action triggered by UI:
	@objc.IBAction
	def setWidth_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.ronyginosar.HEBNibber.width'] = sender.floatValue()
		# Trigger redraw
		self.update()

	@objc.IBAction
	def setHeight_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.ronyginosar.HEBNibber.height'] = sender.floatValue()
		# Trigger redraw
		self.update()

	@objc.IBAction
	def setAngle_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.ronyginosar.HEBNibber.angle'] = sender.floatValue()
		# Trigger redraw
		self.update()

	# Actual filter
	def filter(self, thisLayer, inEditView, customParameters): #todo thisLAyer
		# Called on font export, get value from customParameters
		if customParameters.has_key('width'):
			width = customParameters['width']
		if customParameters.has_key('height'):
			height = customParameters['height']
		if customParameters.has_key('angle'):
			angle = customParameters['angle']

		# Called through UI, use stored value
		else:
			width = float(Glyphs.defaults['com.ronyginosar.HEBNibber.width'])
			height = float(Glyphs.defaults['com.ronyginosar.HEBNibber.height'])
			angle = float(Glyphs.defaults['com.ronyginosar.HEBNibber.angle'])

		##################################
		#### FILTER CODE STARTS HERE #####
		##################################

		# cases of operation:
		# if angle > 0 we can use the copy path method
		# if angle is 0 - we need to output a monoline glyph with a straight pen angle
		# if one of the shift params is 0 - we nee to produce a monoline with a 45deg pen angle - that is what BroadNibber gives

		# thisLayer = Glyphs.font.selectedLayers[0] #TODO
		# thisLayer.beginChanges() # TODO increase performance and prevent undo problems

		# clean up path and prepare them for copying:
		thisLayer.addExtremePoints()
		thisLayer.addInflectionPoints()
		thisLayer.cleanUpPaths()
		thisLayer.correctPathDirection()

		########## TODO - something funny with the angle rational

		# if angle > 0 we can use the copy path method
		if angle != 0:
			#shift to rotate around origin
			xCenter = thisLayer.bounds.origin.x + thisLayer.bounds.size.width * 0.5
			yCenter = thisLayer.bounds.origin.y + thisLayer.bounds.size.height * 0.5
			shiftMatrix = [1, 0, 0, 1, -xCenter, -yCenter]
			thisLayer.applyTransform( shiftMatrix )

			# if one of the shift params is 0 - we nee to produce a monoline with a 45deg pen angle - that is what BroadNibber gives
			if width == 0 : width = height
			elif height == 0 : height = width

			# 45deg is a breaking point in the rotation, sin=cos. thus we modolus it
			angle %= 45
			angleRadians = math.radians( angle )
			rotationMatrix = [ math.cos(angleRadians), -math.sin(angleRadians), math.sin(angleRadians), math.cos(angleRadians), 0, 0 ]
			thisLayer.applyTransform( rotationMatrix )

			for path in thisLayer.paths:
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
			thisLayer.cleanUpPaths()
			thisLayer.correctPathDirection()

			#rotate and shift back
			angleRadians = math.radians( -angle )
			rotationMatrix = [ math.cos(angleRadians), -math.sin(angleRadians), math.sin(angleRadians), math.cos(angleRadians), 0, 0 ]
			thisLayer.applyTransform( rotationMatrix )

			shiftMatrix = [1, 0, 0, 1, xCenter, yCenter]
			thisLayer.applyTransform( shiftMatrix )

		# if angle is 0, we can (and need to) use offsetCurveFilter for best results
		elif angle == 0:
			offsetCurveFilter = NSClassFromString("GlyphsFilterOffsetCurve")
			offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_(
						thisLayer, # Layer
						width/2, # offsetX
						height/2, # offsetY
						True, # makeStroke
						False, # autoStroke
						0.5, # position
						None, # error
						None # shadow
						)
						#TODO self

		# thisLayer.endChanges() # TODO close beginChanges

		##################################
		#### FILTER CODE ENDS HERE #####
		##################################

	def generateCustomParameter( self ):
		return "%s; width:%s; height:%s; angle:%s;" % (
			self.__class__.__name__,
			Glyphs.defaults['com.ronyginosar.HEBNibber.width'],
			Glyphs.defaults['com.ronyginosar.HEBNibber.height'],
			Glyphs.defaults['com.ronyginosar.HEBNibber.angle'],
			)

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__

	#### to add methods of self. ####
	# def rotateLayer( self, thisLayer, angle ):
	# 	"""Rotates all paths in the thisLayer."""
