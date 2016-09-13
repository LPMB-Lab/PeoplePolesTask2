import random
import viz
import viztask
import vizact
import vizinfo
import vizproximity
import vizshape
import oculus
import vizmat
import math
import time
import array
import datetime
import steamvr

###################
##  CONSTANTS
###################

# Key commands
KEYS = { 'reset'	: 'r'
		,'debug'	: 'd'
		,'start'	: 's'
		,'nextTrial': ' ' # Refers to a space bar
}

OPTOTRAK_IP = '192.219.236.36'

# Real Trials
CONDITIONS = ['POLES', 'AVATAR_FORWARD', 'AVATAR_BACKWARD']
APERTURES = [1.0, 1.4, 1.8]
TRIALS_PER_APERTURE = 5

# Catch Trials
C_CONDITIONS = ['AVATAR_FORWARD_MOVE', 'AVATAR_BACKWARD_MOVE']
C_APERTURES = [1.0, 1.4, 1.8]
CTRIALS_PER_APERTURE = 1

HMD_TYPE = {
	'OCULUS': 0,
	'VIVE': 1,
	'NONE': 2
}

TRACKING_TYPE = { 
	'OPTOTRAK': 0,
	'VIVE': 1,
	'NONE': 2
}

HMD = HMD_TYPE['NONE']
TRACKING = TRACKING_TYPE['NONE']

# Locations for cylinders during learning phase
learnCylinderLocations = [
	[-1,0,-1.5],
	[-1,0,1.5],
	[1,0,1.5],
	[1,0,-1.5]]

###################
##  TRIAL
###################

class Trial():
	def __init__(self, condition, aperture):
		self.condition = condition
		self.aperture = aperture
	
	def toString(self):
		return "%0.1f, %s" % (self.aperture, self.condition)

###################
##  SIMULATION
###################

class PeoplePolesTask2():
	def __init__(self):
		self.trials = []
		self.cylinderSensors = []
		self.hmd = None
		self.info = vizinfo.InfoPanel("")
		self.manager = vizproximity.Manager()
		self.learnCylinderLocations = [
			[-1,0,-1.5],
			[-1,0,1.5],
			[1,0,1.5],
			[1,0,-1.5]]
		
		self.crate_1 = viz.addChild('crate.osgb')
		self.crate_1.setScale(2, 2, 2)
		self.crate_1.setPosition(2, 1, 0)
		# self.crate_1.visible(viz.OFF)
		
		self.crate_2 = viz.addChild('crate.osgb')
		self.crate_2.setScale(2, 2, 2)
		self.crate_2.setPosition(-2, 1, 0)
		
		self.initializeSimulation()
	
	def initializeSimulation(self):
		
		#Set up the environment and proximity sensors
		scene = viz.addChild('../assets/newMaze.osgb')
		# scene = viz.addChild('lab.osgb')
		# wall = viz.addChild('crescent_mesh.osgb')

		#Create proximity manager and set debug on. Toggle debug with d key
		self.manager.setDebug(viz.ON)
		debugEventHandle = vizact.onkeydown(KEYS['debug'], self.manager.setDebug,viz.TOGGLE)

		#Add main viewpoint as proximity target
		target = vizproximity.Target(viz.MainView)
		self.manager.addTarget(target)

		#Add a sensor in the center of the room for the participant to return to after each trial
		centerSensor = vizproximity.Sensor(vizproximity.CircleArea(1.5,center=(0.0,0.0)),None)
		self.manager.addSensor(centerSensor)
		
		self.info.setText("Explore the environment")
		
		###################
		## HMD Initialization
		###################
		
		if HMD == HMD_TYPE['OCULUS']:
			# Setup Oculus Rift HMD
			hmd = oculus.Rift()
			if not hmd.getSensor():
				sys.exit('Oculus Rift not detected')

			# Go fullscreen if HMD is in desktop display mode
			if hmd.getSensor().getDisplayMode() == oculus.DISPLAY_DESKTOP:
				viz.window.setFullscreen(True)

			# Setup heading reset key
			vizact.onkeydown(KEYS['reset'], hmd.getSensor().reset)

			# Link HMD Orientation to mainview
			viewLink = viz.link(hmd.getSensor(), viz.MainView, mask=viz.LINK_ORI)

			# Apply user profile eye height to view
			profile = hmd.getProfile()
			if profile:
				viewLink.setOffset([0,profile.eyeHeight,0])
			else:
				viewLink.setOffset([0,1.8,0])
				
			hideMouse()
		elif HMD == HMD_TYPE['VIVE']:
			hmd = steamvr.HMD()

			if not hmd.getSensor():
				sys.exit('Vive not detected')
			viz.link(hmd.getSensor(), viz.MainView)
			
			hideMouse()
		else:
			print("No HMD Set")

		###################
		## Tracking Initialization
		###################
		if TRACKING == TRACKING_TYPE['OPTOTRAK']:
			opto = viz.add('optotrak.dle', 0, OPTOTRAK_IP)
			body = opto.getBody(0)
			optoLink = viz.link(body, viz.MainView, mask=viz.LINK_POS)

		###################
		## Generate Trials
		###################

		# Trial generation
		for i in range (0, TRIALS_PER_APERTURE):
			for j in range (0, len(CONDITIONS)):
				for k in range (0, len(APERTURES)):
					self.trials.append(Trial(CONDITIONS[j], APERTURES[k]))
		
		# Catch trial generation
		for i in range (0, CTRIALS_PER_APERTURE):
			for j in range (0, len(C_CONDITIONS)):
				for k in range (0, len(C_APERTURES)):
					self.trials.append(Trial(C_CONDITIONS[j], C_APERTURES[k]))

		random.shuffle(self.trials)
		
		###################
		## Export Trials
		###################
		i = datetime.datetime.now()
		fileName = "%s_%s_%s_%s_%s_%s.txt" % (i.year, i.month, i.day, i.hour, i.minute, i.second)
		print fileName
		
		export_data = open(str(fileName), 'a')
		
		for i in range (0, len(self.trials)):
			export_data.write("%s. %s \n" % (str(i+1), self.trials[i].toString()))
			
		export_data.flush()

	def AddCylinder(self, color, position):
		cylinder = vizshape.addCylinder(height=5,radius=0.2)
		cylinder.setPosition(position)
		cylinder.color(color)
		
		sensor = vizproximity.addBoundingBoxSensor(cylinder,scale=(1,1,1))
		
		self.cylinderSensors.append(sensor)
		
		self.manager.addSensor(sensor)
		self.manager.onEnter(sensor, self.EnterCylinder, cylinder)

	# Remove cylinder on enter
	def EnterCylinder(self, e, cylinder):
		cylinder.remove()

	def learnPhase(self):
		# Provide instructions for the participant
		self.info.setText("Walk to each marker that appears.")

		# Hide instructions after 5 seconds
		yield viztask.waitTime(5)

		for i in range (0,len(self.learnCylinderLocations)):
			
			self.AddCylinder(viz.RED, self.learnCylinderLocations[i])

			# Get sensor for this trial
			sensor = self.cylinderSensors[i]

			# The yielded command returns a viz.Data object with information
			# about the proximity event such as the sensor, target involved
			yield vizproximity.waitEnter(sensor)

		self.info.setText("Calibration is complete.")
		
		# Start testing phase after 5 seconds
		yield viztask.waitTime(5)

	def testPhase(self):
		for i in range (0, len(self.trials)):
			
			print("Test Number %s : %s" % (str(i + 1), self.trials[i].toString()))
			
			for j in range (0, 3):
				
				if (j==0):
					AddCylinder(viz.RED, trials[i][0][j])
					print("Created cylinder #" + str(j+1))
				else:
					AddCylinder(viz.GREEN, trials[i][0][j])
					print("Created cylinder #" + str(j+1))
				
				sensor = cylinderSensors[j + 3*i + len(learnCylinderLocations)]
				print("Waiting for sensor collision with sensor #" + str(j+1))
				info.setText(trials[i][1])
				yield vizproximity.waitEnter(sensor)
				
				if (j == 2):
					# Make screen black until nextTrial key is pressed
					viz.scene(2)
					yield viztask.waitKeyDown(KEYS['nextTrial'])
					viz.scene(1)


		info.setText('Thank You. You have completed the experiment')
		
	def hideMouse():
		# Hide and trap mouse since we will be using virtual canvas mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)

def experiment():
	simulation = PeoplePolesTask2()

	#Wait for spacebar to begin experiment
	yield viztask.waitKeyDown(KEYS['start'])
	yield simulation.learnPhase()
	yield simulation.testPhase()

	#Log results to file
	try:
		with open('experiment_data.txt','w') as f:

			#write trial data to file
			for i in range(0, len(trials)):
				data += "{0}. {1}".format(i, trials[i][1])
			f.write(data)
	except IOError:
		viz.logWarn('Could not log results to file. Make sure you have permission to write to folder')

# Preliminary setup
viz.setMultiSample(8)
viz.fov(60)
viz.go()	
viztask.schedule(experiment)