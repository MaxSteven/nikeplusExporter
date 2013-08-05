#    This file is part of python-nikeplus-2013.
#
#    Copyright 2013 Daniel Alexander Smith
#    Copyright 2013 University of Southampton
#
#    python-nikeplus-2013 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    python-nikeplus-2013 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with python-nikeplus-2013.  If not, see <http://www.gnu.org/licenses/>.

import argparse, getpass, logging, nikeplus, pprint, os, json, nikeplusjson2tcx

""" A simple command-line client to demontrate usage of the library. """

parser = argparse.ArgumentParser(description = "Use the Nike+ API")
parser.add_argument('email', type = str, help = "E-mail address of the user in the Nike+ system")
parser.add_argument('start_date', type = str, help = "Start date, like: 2013-03-20")
parser.add_argument('end_date', type = str, help = "End date, like: 2013-03-21")
parser.add_argument('--debug', default = False, action="store_true", help = "Turn on verbose debugging")

args = vars(parser.parse_args())
password = getpass.getpass()

if args['debug']:
    logging.basicConfig(level = logging.DEBUG)

nikeplus = nikeplus.NikePlus()
nikeplus.login(args['email'], password)
nikeplus.get_token()

activities = nikeplus.get_activities(args['start_date'], args['end_date'])
#activities_all = []
activitiesDir = os.path.join(os.path.dirname(__file__), 'activities')
for activity_list in activities:
    if type(activity_list) != type([]):
        activity_list = [activity_list]
    for activity in activity_list:
        activity_id = activity['activityId']
        activity_timedate = activity['startTime'][0:10] + '_' + activity['startTime'][11:13] + '-' + activity['startTime'][14:16] + '-' + activity['startTime'][17:19]
        logging.debug("activity id: {0}".format(activity_id))
        logging.debug("activity_details: {0}".format(pprint.pformat(nikeplus.get_activity_detail(activity_id))))
        logging.debug("gps_data: {0}".format(pprint.pformat(nikeplus.get_gps_data(activity_id))))
        #activities_all.append(nikeplus.get_activity_detail(activity_id))
        #activities_all.append(nikeplus.get_gps_data(activity_id))

        if not os.path.exists(activitiesDir):
            os.makedirs(activitiesDir)

        filepath_activity = activitiesDir + '/Nikeplus_' + activity_timedate + '_' + activity_id + '_activity.json'
        with open(filepath_activity, 'w') as myFile:
            myFile.write( json.dumps( nikeplus.get_activity_detail(activity_id), indent=2) )

        filepath_gps = activitiesDir + '/Nikeplus_' + activity_timedate + '_' + activity_id + '_gps.json'
        with open(filepath_gps, 'w') as myFile:
            myFile.write( json.dumps( nikeplus.get_gps_data(activity_id), indent=2) )

        nikeplusjson2tcx.convert(activity_id)

#print json.dumps(activities_all, indent=2)