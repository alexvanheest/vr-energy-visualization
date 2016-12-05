# VR Energy Visualization

The following is a series of methods written to manipulate OSISoft's PI Web API JSON files. These functions collect data from every building accessible from the "Hackathon" section of the Web API such that any buildings added after the competition's end will be collected as well. The data I looked at in particular includes measurements listed in the Elec (Shark) elements for each building, which provides concrete, constantly updated data for daily power usage, daily energy usage, and usage in watts.

This script is to be run on a web server. We created a simple Apache server using Amazon Web Services to accomplish this. This script interprets preexisting JSON files from the Web API and creates new ones every minute (when run with the appropriate, trivial bash script and as a cron job) copying the new data to a static "current data" file.

Included in this repository are the main Python script "generate-json.py," which reads and creates the necessary JSON files and a few example JSON files created on our web server. Bash scripts and crontab setup is not included but can easily be surmised from given Python script.

The VR portion of our project was created by Drew Siedel using C#, Unity, Android, Google's Streetview API, and more. It is designed to be viewed on the Samsung Gear VR with an Android device. The AWS web server serves as a go-between for our otherwise separate programs.

The following is a list of relevant links:

Video of Recorded Footage: https://www.youtube.com/watch?v=BiBG86p_Umk

DevPost Link: https://devpost.com/software/vr-energy-data-visualization

Drew Siedel's Source Code: https://github.com/dtsiedel/VREnergyVisualization

Accolades from Hackathon:
- Top 5 Overall
- Recipient of Lutron Prize
- 2nd Place in OSISoft Challenge

I'd like to thank OSISoft for granting us access to some live data from the PI Web API to use for our project and for recognizing our efforts at the LU Hacks Winter 2016 competition. I'd also like to thank Lutron for recognizing our work. And last but not least, I'd like to thank Drew Siedel for his work on the amazing frontend.
