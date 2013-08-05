import json
from xml.etree.ElementTree import Element, SubElement, tostring
from pprint import pprint
import xml.dom.minidom
import datetime, time
import os
import numpy




class XMLGen():
	def __init__(self, *args):
		# Write XML
		self.root = Element('TrainingCenterDatabase', attrib={
															'xmlns':'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
															'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
															'xsi:schemaLocation':'http://www.garmin.com/xmlschemas/ActivityExtension/v2 http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd http://www.garmin.com/xmlschemas/FatCalories/v1 http://www.garmin.com/xmlschemas/fatcalorieextensionv1.xsd http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd'
													})
		self.folders = self.root.append(Element('Folders'))
		self.activities = SubElement(self.root, 'Activities')


def distanceInterp(distance, totalDistance):
	# Heartbeats
	distanceMps = []
	second = 0
	for i in range(0, len(distance)-1):
	
		# First 10 seconds, interpolate from 0 to first registered value
		if i == 0:
			interpolated = ( numpy.linspace(0.0, float(distance[i]), 10) )
			count = 1
			for item in interpolated:
				if count <= 10:
					distanceMps.append(item)
					#print str(count) + ': ' + str(round(item*100,2)) + '\t\t\t\t\t(' + str(second) + ' s)'
				count +=1
				second +=1
		

		interpolated = ( numpy.linspace(float(distance[i]), float(distance[i+1]), 10) )
		count = 1
		for item in interpolated:
			if count <= 10:
				distanceMps.append(item)
				#print str(count) + ': ' + str(round(item*100,2)) + '\t\t\t\t\t(' + str(second) + ' s)'
			count +=1
			second +=1


		# Last 10 seconds, interpolate from last known value to total distance
		if i == len(distance)-2:
			interpolated = ( numpy.linspace(float(distance[i]), totalDistance, 10) )
			count = 1
			for item in interpolated:
				if count <= 10:
					distanceMps.append(item)
					#print str(count) + ': ' + str(round(item*100,2)) + '\t\t\t\t\t(' + str(second) + ' s)'
				count +=1
				second +=1

		
	return distanceMps



def heartbeatsInterp(heartbeatsBpm):
	# Heartbeats
	heartbeatsBpmInterp = []
	second = 0
	for i in range(0, len(heartbeatsBpm)-1):

		# Remove any occurances of heartbeat 0
		if heartbeatsBpm[i] == '0':
			try:
				heartbeatsBpm[i] = heartbeatsBpm[i-1]
			except:
				pass
		if heartbeatsBpm[i+1] == '0':
			try:
				heartbeatsBpm[i+1] = heartbeatsBpm[i]
			except:
				pass


		'''A hartbeat is registered every 10 seconds. To get a heartbeat every second we need to fill the gap of 8 heartbeats.
		For the first 10 seconds, we will just use the same heartbeat as the one registered after the first 10 seconds.
		The same approach goes for the last 10 seconds, using the last registered heartbeat value.'''

		# First 10 seconds, add the first heartbeat value 10 times
		if i == 0:
			for x in range(0,10):
				heartbeatsBpmInterp.append( heartbeatsBpm[i] )
				#print str(x) + ': ' + str( heartbeatsBpm[i] ) + '\t\t\t\t\t(' + str(second) + ' s)'
				second +=1


		interpolated = ( numpy.linspace(float(heartbeatsBpm[i]), float(heartbeatsBpm[i+1]), 10) )
		count = 1
		for item in interpolated:
			if count <= 10:
				heartbeatsBpmInterp.append(int(round(item)))
				#print str(count) + ': ' + str(int(round(item))) + '\t\t\t\t\t(' + str(second) + ' s)'
			count +=1
			second +=1

		
		# Last 10 seconds, add the last heartbeat value 10 times
		if i == len(heartbeatsBpm)-2:
			for x in range(1,11):
				heartbeatsBpmInterp.append( heartbeatsBpm[i+1] )
				#print str(x) + ': ' + str( heartbeatsBpm[i] ) + '\t\t\t\t\t(' + str(second) + ' s)'
				second +=1
	return heartbeatsBpmInterp


def timeStampConversion(startTime):
	year = int(startTime[:4])
	month = int(startTime[5:7])
	day = int(startTime[8:10])
	letter1 = startTime[10:11]
	hour = int(startTime[11:13])
	minute = int(startTime[14:16])
	second = int(startTime[17:19])
	letter2 = startTime[19:20]
	return year, month, day, letter1, hour, minute, second, letter2

def currentTime(startTime, counter):
	addSeconds = int(counter)
	year, month, day, letter1, hour, minute, second, letter2 = timeStampConversion(startTime)

	startTimeObject = datetime.datetime(year, month, day, hour, minute, second)
	currentDateTimeObject = startTimeObject + datetime.timedelta(seconds=addSeconds)

	currentDate = currentDateTimeObject.date()
	currentTime = currentDateTimeObject.time()

	return (str(currentDate) + letter1 + str(currentTime) + letter2)


def jsonReader(jsonFilepath):
	# Read JSON
	json_file = os.path.join(jsonFilepath)
	json_data=open(json_file)
	data = json.load(json_data)
	#pprint(data)
	json_data.close()
	return data


def convert(nikeplusActivityID):
	activitiesDir = os.path.join(os.path.dirname(__file__), 'activities')
	
	for filename in os.listdir( activitiesDir ):
		if (nikeplusActivityID in filename) and ('activity' in filename):
			activity_file = os.path.join(activitiesDir, filename)
			activityData = jsonReader(activity_file)						# JSON activity data
		if (nikeplusActivityID in filename) and ('gps' in filename):
			gps_file = os.path.join(activitiesDir, filename)
			gpsData = jsonReader(gps_file)									# JSON GPS data
			waypoints = gpsData['waypoints']								# GPS data, waypoints

	xmlObject = XMLGen() 													# Create XML object

	activityID = activityData['activityId']									# JSON ID
	activityType = activityData['activityType']								# JSON Activity type, e.g.: RUN
	startTime = activityData['startTime']									# JSON Start time, e.g.: 2013-08-03T08:25:24Z
	activityTimeZone = activityData['activityTimeZone']						# JSON Timezone, e.g.: Europe/Stockholm
	status = activityData['status'] 										# JSON deviceType, e.g.: COMPLETE
	deviceType = activityData['deviceType']				 					# JSON deviceType, e.g.: IPHONE | SPORTWATCH
	
	calories = activityData['metricSummary']['calories'] 					# JSON calories
	fuel = activityData['metricSummary']['fuel'] 							# JSON fuel
	# distance skipped
	steps = activityData['metricSummary']['steps'] 							# JSON steps
	duration = activityData['metricSummary']['duration'] 					# JSON duration: 0:25:17.000
	

	metricsSize = len(activityData['metrics'])								# JSON metrics loop
	for x in range(0, metricsSize):
		if 'DISTANCE' in activityData['metrics'][x]['metricType']:
			print 'Found DISTANCE.'
			distance = activityData['metrics'][x]['values']					# JSON distance (10 second intervals)
			totalDistance = activityData['metricSummary']['distance']		# JSON total distance
			distanceMeters = distanceInterp(distance, totalDistance)		# Interpolation of distance (1 second intervals)

		if 'HEARTRATE' in activityData['metrics'][x]['metricType']:
			print 'Found HEARTRATE.'
			heartbeatsBpm = activityData['metrics'][x]['values']			# JSON heartbeats per minute (10 second intervals)
			heartbeatsBpmInterp = heartbeatsInterp(heartbeatsBpm)			# Interpolation of heartbeats (1 second intervals)

		if 'SPEED' in activityData['metrics'][x]['metricType']:				# TO DO
			print 'Found SPEED (TODO).'
		



	'''
	Building the XML Structure...
	'''

	if activityType == 'RUN':
		xmlObject.activity = SubElement(xmlObject.activities, 'Activity', attrib={'Sport':'Running'}) # Add XML entry
	else:
		xmlObject.activity = SubElement(xmlObject.activities, 'Activity') # Add XML entry

	xmlObject.id = SubElement(xmlObject.activity, 'id') # Add XML entry
	xmlObject.id.text = startTime # Add XML entry
	xmlObject.lap = SubElement(xmlObject.activity, 'Lap', attrib={'StartTime':startTime}) # Add XML entry
	
	xmlObject.totalTimeSeconds = SubElement(xmlObject.lap, 'TotalTimeSeconds') # Add XML entry
	durationSplit = time.strptime(duration.split('.')[0],'%H:%M:%S')
	durationSeconds = str( int( datetime.timedelta(hours=durationSplit.tm_hour,minutes=durationSplit.tm_min,seconds=durationSplit.tm_sec).total_seconds() ) )
	xmlObject.totalTimeSeconds.text = durationSeconds # Add XML entry

	xmlObject.distanceMeters = SubElement(xmlObject.lap, 'DistanceMeters') # Add XML entry
	xmlObject.distanceMeters.text = str(totalDistance) # Add XML entry

	xmlObject.calories = SubElement(xmlObject.lap, 'Calories') # Add XML entry
	xmlObject.calories.text = str(calories) # Add XML entry

	xmlObject.intensity = SubElement(xmlObject.lap, 'Intensity') # Add XML entry
	xmlObject.intensity.text = 'Resting' # Add XML entry

	xmlObject.triggerMethod = SubElement(xmlObject.lap, 'TriggerMethod') # Add XML entry
	xmlObject.triggerMethod.text = 'Manual' # Add XML entry

	xmlObject.track = SubElement(xmlObject.lap, 'Track') # Add XML entry

	# Loop per time unit START, based on GPS data
	if 'waypoints' in locals():
		for count in range(0, len(waypoints) ):
			xmlObject.trackpoint = SubElement(xmlObject.track, 'Trackpoint') # Add XML entry

			xmlObject.time = SubElement(xmlObject.trackpoint, 'Time') # Add XML entry
			xmlObject.time.text = currentTime(startTime, count) # Add XML entry

			xmlObject.position = SubElement(xmlObject.trackpoint, 'Position') # Add XML entry

			xmlObject.latitudeDegrees = SubElement(xmlObject.position, 'LatitudeDegrees') # Add XML entry
			xmlObject.latitudeDegrees.text = str( waypoints[count]['latitude'] ) # Add XML entry		
			xmlObject.longitudeDegrees = SubElement(xmlObject.position, 'LongitudeDegrees') # Add XML entry
			xmlObject.longitudeDegrees.text = str( waypoints[count]['longitude'] ) # Add XML entry

			xmlObject.altitudeMeters = SubElement(xmlObject.trackpoint, 'AltitudeMeters') # Add XML entry
			xmlObject.altitudeMeters.text = str( waypoints[count]['elevation'] ) # Add XML entry		
			
			xmlObject.distanceMeters = SubElement(xmlObject.trackpoint, 'DistanceMeters') # Add XML entry
			xmlObject.distanceMeters.text = str(distanceMeters[count]) # Add XML entry.....................

			if 'heartbeatsBpmInterp' in locals():
				xmlObject.heartRate = SubElement(xmlObject.trackpoint, 'HeartRateBpm', attrib={'xsi:type':'HeartRateInBeatsPerMinute_t'}) # Add XML entry
				xmlObject.value = SubElement(xmlObject.heartRate, 'Value') # Add XML entry
				xmlObject.value.text = str(heartbeatsBpmInterp[count]) # Add XML entry

			xmlObject.extensions = SubElement(xmlObject.trackpoint, 'Extensions') # Add XML entry
	# Loop per time unit END


	'''Inspect XML tree while building it '''
	#xmltree = xml.dom.minidom.parse(xml_fname) # Filename
	#xmltree = xml.dom.minidom.parseString( tostring( xmlObject.root ) ) # String
	#print xmltree.toprettyxml() # Only for debugging, do not save the TCX file with pretty print


	exportDir = os.path.join(os.path.dirname(__file__), 'export')
	if not os.path.exists(exportDir):
			os.makedirs(exportDir)
	activity_timedate = activityData['startTime'][0:10] + '_' + activityData['startTime'][11:13] + '-' + activityData['startTime'][14:16] + '-' + activityData['startTime'][17:19]
	filepath_tcx = os.path.join( exportDir, ('Nikeplus_' + activity_timedate + '_' + activityID + '.tcx') )
	#print filepath_tcx
	with open(filepath_tcx, 'w') as myFile:
		myFile.write( tostring( xmlObject.root ) )
		print 'Exported ' + filepath_tcx[(filepath_tcx.rfind('/')+1):]







