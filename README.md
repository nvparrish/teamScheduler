This project takes in a spreadsheet with available times of people in various
time zones and uses a genetic algorithm to identify groups of a specified
size where all members have common available meeting times over the course of
one week.
This project currently does not attempt to handle the edge cases that arise
when trying to deal with international time zones such as various time shifts
like daylight savings time or any time zones that are at half-hour intervals.
To use this program, you need to ask all participants to fill out a Google
spreadsheet showing which hours of each day they are available to have a
team meeting.

To start, it is useful to set up a virtual environtment
pip3 install virtualenv
python3 -m venv <your-env>
source <your-env>/bin/activate
pip3 install google-api-python-client 
pip3 install google-auth-oauthlib
pip3 install pandas
