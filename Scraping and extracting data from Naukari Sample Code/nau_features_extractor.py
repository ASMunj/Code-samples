import re
import string
import time
import datetime
from functools import reduce
import math
from dateutil.parser import parse
#TODO Add logging
# Regex : Extraction duration
PRO_EXP_DURATION_REGEX = re.compile(
	"[a-z]{3,4}\s+\d{4}\s+to\s+[a-z]{3,4}\s((\d){4}|date|present)$")

# Regex : Extract year from academic degree
ACAD_EXP_YEAR_EXTRACT_REGEX = re.compile(r"\d{4}$")

# Global values
PRESENT_DATE = datetime.datetime.today().strftime('%Y-%m-%d')


def prof_exp_clean_duration_designation(raw_designation_text):
	"""
		
		Extract duration from designation string
		Returns duration and designation as seperate entites
		If not found, return None

	"""
	designation = None
	duration = None

	try:
		raw_designation_text = raw_designation_text.lower()
	except AttributeError:
		return designation, duration
	else:
		try:
			duration_match = re.search(
				PRO_EXP_DURATION_REGEX, raw_designation_text)
			duration_match = duration_match.group(0)
		except:
			return designation, duration
		else:
			duration = duration_match
			designation = raw_designation_text.replace(duration, '')
			designation = ' '.join([word.strip()
									for word in designation.split()])
			return designation, duration


def pro_exp_duration_calculations(extracted_duration):
	"""Calculating duration metrics"""

	to_present_date_replacements = ('till', ''), ('date', str(PRESENT_DATE)), ('now', str(
		PRESENT_DATE)), ('present', str(PRESENT_DATE)), ('current', str(PRESENT_DATE))

	duration_data = {
		"extracted_duration": None,
		"start_date": None,
		"end_date": None,
		"tenure_days": None,
		"tenure_years": None
	}

	if extracted_duration == None:
		return None
	else:
		extracted_duration = extracted_duration.strip().lower()
		try:
			extracted_duration.split('to')
		except:
			#TODO
			return None
		else:
			# Convert Till date to current date
			duration_transformed = reduce(lambda a, kv: a.replace(*kv), to_present_date_replacements, extracted_duration)
			# Seperate start and end dates
			start_date = duration_transformed.split('to')[0].strip()
			end_date = duration_transformed.split('to')[-1].strip()
			# Converting to dates
			# Also has times
			start_datex = str(parse(start_date))
			end_datex = str(parse(end_date))

			# Start dates
			start_datex = start_datex.split(' ')[0]
			start_datex_splitted = start_datex.split('-')
			start_date_datetime = datetime.date(int(start_datex_splitted[0]), int(start_datex_splitted[1]), int(start_datex_splitted[2]))

			# End dates
			end_datex = end_datex.split(' ')[0]
			end_datex_splitted = end_datex.split('-')
			end_date_datetime = datetime.date(int(end_datex_splitted[0]), int(end_datex_splitted[1]), int(end_datex_splitted[2]))
			# Duration days and months calcualtions
			duration_days = end_date_datetime - start_date_datetime
			duration_months = round((duration_days.days/30)/12, 2)


			duration_data['start_date'] = str(start_date_datetime)
			duration_data['end_date'] = str(end_date_datetime)
			duration_data['extracted_duration']= extracted_duration
			duration_data['tenure_days'] = int(duration_days.days)
			duration_data['tenure_years'] = float(duration_months)

			return duration_data


def extract_year_from_degree(degree):
	"""Extract year from degree - Academic Qualifications"""
	if degree == None:
		return None
	else:
		try:
			year_match = re.search(ACAD_EXP_YEAR_EXTRACT_REGEX, degree)
			year_match = year_match.group(0)
		except:
			return None
		else:
			return year_match.strip()


def convert_total_exp_float(total_exp_raw):
	if total_exp_raw == None:
		return None
	else:
		try:
			match = re.findall(r"\d{1,2}", total_exp_raw)
		except:#TODO Logging
			return 0
		else:
			if len(match) == 2:
				exp_years = int(match[0])
				exp_months = int(match[-1])

				if exp_years == 0 and exp_months == 0:
					return 0
				elif exp_years > 0 and exp_months > 0:
					total_exp = exp_years  + round(exp_months/12, 2)
					return total_exp
				elif exp_years > 0 and exp_months == 0:
					return  exp_years
				else:
					return round(exp_months / 12, 2)
			else:#TODO Logging
				return 0
			
