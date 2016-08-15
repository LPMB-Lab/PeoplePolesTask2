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

###################
##  CONSTANTS
###################

# Key commands
KEYS = { 'reset'	: 'r'
		,'debug'	: 'd'
		,'start'	: 's'
		,'nextTrial': ' '
}

OPTOTRAK_IP = '192.219.236.36'

NO_GVS 		= "NGVS"
LEFT_GVS 	= "LGVS"
RIGHT_GVS 	= "RGVS"

# Locations for cylinders during learning phase
learnCylinderLocations = [
	[-1,0,-1.5],
	[-1,0,1.5],
	[1,0,1.5],
	[1,0,-1.5]]
	
# 4 Triangles for testing
TWO_THREE_LEFT_TRIANGLE = [
	[-1,0,-1.5],
	[1,0,-1.5],
	[1,0,1.5],
	["TWO_THREE_LEFT_TRIANGLE"]
]

TWO_THREE_RIGHT_TRIANGLE = [
	[1,0,-1.5],
	[-1,0,-1.5],
	[-1,0,1.5],
	["TWO_THREE_RIGHT_TRIANGLE"]
]

THREE_TWO_LEFT_TRIANGLE = [
	[-1,0,-1.5],
	[-1,0,1.5],
	[1,0,1.5],
	["THREE_TWO_LEFT_TRIANGLE"]
]

THREE_TWO_RIGHT_TRIANGLE = [
	[1,0,-1.5],
	[1,0,1.5],
	[-1,0,1.5],
	["THREE_TWO_RIGHT_TRIANGLE"]
]

# The actual trials will be stored here
trials = []
	
viz.setMultiSample(8)
viz.fov(60)
viz.go()

################
##  OCULUS
################

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

# Hide and trap mouse since we will be using virtual canvas mouse
viz.mouse.setVisible(False)
viz.mouse.setTrap(True)

#####################
## OPTOTRAK3
#####################

# This part is to be uncommented for the Optotrack stuff
# Linking the avatar to the Optotrack rigid bodies
opto = viz.add('optotrak.dle', 0, OPTOTRAK_IP)
body = opto.getBody(0)
optoLink = viz.link(body, viz.MainView, mask=viz.LINK_POS)
	
#####################
## SIMULATION
#####################

#Set up the environment and proximity sensors
scene = viz.addChild('newMaze.osgb')

#Create proximity manager and set debug on. Toggle debug with d key
manager = vizproximity.Manager()
manager.setDebug(viz.ON)
debugEventHandle = vizact.onkeydown(KEYS['debug'],manager.setDebug,viz.TOGGLE)

#Add main viewpoint as proximity target
target = vizproximity.Target(viz.MainView)
manager.addTarget(target)

#fade to true color when viewpoint moves near
def EnterCylinder(e, cylinder):
	cylinder.remove()

#add cylinders and create a proximity sensor around each one
cylinderSensors = []

#Add a sensor in the center of the room for the participant to return to after each trial
centerSensor = vizproximity.Sensor(vizproximity.CircleArea(1.5,center=(0.0,0.0)),None)
manager.addSensor(centerSensor)

#Add vizinfo panel to display instructions
info = vizinfo.InfoPanel("Explore the environment")

def ExportTrials():
	i = datetime.datetime.now()
	fileName = "%s_%s_%s_%s_%s_%s.txt" % (i.year, i.month, i.day, i.hour, i.minute, i.second)
	print fileName
	
	
	export_data = open(str(fileName), 'a')
	
	for i in range (0, len(trials)):
		export_data.write( str(i+1) + ". " + str(trials[i][1]) + ", " + str(trials[i][0][3][0]) + "\n")
		
	export_data.flush()
		
def AddCylinder(color, position):

	cylinder = vizshape.addCylinder(height=5,radius=0.2)
	cylinder.setPosition(position)
	cylinder.color(color)
	
	sensor = vizproximity.addBoundingBoxSensor(cylinder,scale=(1,1,1))
	
	cylinderSensors.append(sensor)
	
	manager.addSensor(sensor)
	manager.onEnter(sensor, EnterCylinder, cylinder)
	
def GenerateTrials():
	
	# Left Start Trials
	leftStartTrials = []
	
	# Right Start Trials
	rightStartTrials = []

	# Trial generation
	for i in range (0, 3):
		
		# Left Triangle Right GVS
		trial = [THREE_TWO_LEFT_TRIANGLE, RIGHT_GVS]
		leftStartTrials.append(trial)
		
		# Left Triangle Left GVS
		trial = [THREE_TWO_LEFT_TRIANGLE, LEFT_GVS]
		leftStartTrials.append(trial)
		
		# Left Triangle No GVS
		trial = [THREE_TWO_LEFT_TRIANGLE, NO_GVS]
		leftStartTrials.append(trial)
		leftStartTrials.append(trial)
		
		# Left Triangle2 Right GVS
		trial = [TWO_THREE_LEFT_TRIANGLE, RIGHT_GVS]
		leftStartTrials.append(trial)
		
		# Left Triangle2 Left GVS
		trial = [TWO_THREE_LEFT_TRIANGLE, LEFT_GVS]
		leftStartTrials.append(trial)
		
		# Left Triangle2 No GVS
		trial = [TWO_THREE_LEFT_TRIANGLE, NO_GVS]
		leftStartTrials.append(trial)
		leftStartTrials.append(trial)
		
		# Right Triangle Right GVS
		trial = [THREE_TWO_RIGHT_TRIANGLE, RIGHT_GVS]
		rightStartTrials.append(trial)
		
		# Right Triangle Left GVS
		trial = [THREE_TWO_RIGHT_TRIANGLE, LEFT_GVS]
		rightStartTrials.append(trial)
		
		# Right Triangle No GVS
		trial = [THREE_TWO_RIGHT_TRIANGLE, NO_GVS]
		rightStartTrials.append(trial)
		rightStartTrials.append(trial)
		
		# Right Triangle2 Right GVS
		trial = [TWO_THREE_RIGHT_TRIANGLE, RIGHT_GVS]
		rightStartTrials.append(trial)
		
		# Right Triangle2 Left GVS
		trial = [TWO_THREE_RIGHT_TRIANGLE, LEFT_GVS]
		rightStartTrials.append(trial)
		
		# Right Triangle2 Right GVS
		trial = [TWO_THREE_RIGHT_TRIANGLE, NO_GVS]
		rightStartTrials.append(trial)
		rightStartTrials.append(trial)

	# Shuffle the Trials
	random.shuffle(leftStartTrials)
	random.shuffle(rightStartTrials)

	# Add the left/right trials to the main trials one after another
	# so that the start position alternates from left/right
	for i in range (0, len(leftStartTrials)):
		trials.append(leftStartTrials[i])
		trials.append(rightStartTrials[i])

def learnPhase():

	
	# Provide instructions for the participant
	info.setText("Walk to each pillar that appears.")

	# Hide instructions after 5 seconds
	yield viztask.waitTime(5)

	for i in range (0,len(learnCylinderLocations)):
		
		AddCylinder(viz.RED, learnCylinderLocations[i])

		# Get sensor for this trial
		sensor = cylinderSensors[i]

		# The yielded command returns a viz.Data object with information
		# about the proximity event such as the sensor, target involved
		yield vizproximity.waitEnter(sensor)

	info.setText("Calibration is complete.")
	
	# Start testing phase after 5 seconds
	yield viztask.waitTime(5)

def testPhase():
	
	for i in range (0, len(trials)):
		
		print("Test Number: " + str(i + 1))
		
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

def experiment():

	# Generate the trials
	GenerateTrials()
	
	ExportTrials()
	
	#Wait for spacebar to begin experiment
	yield viztask.waitKeyDown(KEYS['start'])
	yield learnPhase()
	yield testPhase()

	#Log results to file
	try:
		with open('experiment_data.txt','w') as f:

			#write trial data to file
			for i in range(0, len(trials)):
				data += "{0}. {1}".format(i, trials[i][1])
			f.write(data)
	except IOError:
		viz.logWarn('Could not log results to file. Make sure you have permission to write to folder')

viztask.schedule(experiment)
