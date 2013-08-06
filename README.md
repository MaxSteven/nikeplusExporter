nikeplusExporter
====================

Features
- Python module to access the new Nike Plus (Nike+) API using python
- Download Nike+ data (JSON format)
- Export Nike+ data (TCX format)

JSON download support:
- Activity data, any Nike+ device
- GPS data, any Nike+ device with GPS

TCX export support
- Nike+ Running app with GPS (tested on iPhone5)
- Nike+ Sportwatch GPS with footpod and Polar Wearlink+ heart rate monitor

This has not been tested yet:
- Nike+ Running app: treadmill/indoor mode
- Nike+ Sportwatch GPS with footpod
- Nike+ Fuelband
- Nike+ Sportband
- Nike+ Running app: iPod with or without heart rate monitor link

Roadmap
- TCX export support for most common scenarios
- GUI

Usage
-----
Just enter `python client.py` followed by the following arguments:
- email address
- start date
- end date

Optional arguments are `--debug`, which will spew out data in the prompt and `-h`, which will show all arguments.

Example: `python client.py john.doe@gmail.com 2012-01-01 2013-01-01` – this will download all workouts throughout the year (this will take a while if you're a frequent runner). 

You will be prompted for your password each time you execute client.py. All workouts will be downloaded into a folder called "archive" and all TCX conversions will end up in a folder called "export".
