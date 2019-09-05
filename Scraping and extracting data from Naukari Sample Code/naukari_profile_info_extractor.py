from NauFeaturesExtractor import nau_features_extractor
from pprint import pprint
"""

		Author: Anirudh Munj
		Date: 28/05/2019

		Extracts information from naukari profiles
		Uses profiles saved locally as HTML pages

"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import string
import json
import codecs
import requests
from collections import Counter



# Logging related
import logging
logging.basicConfig(filename='LOGS.log', level=logging.DEBUG)


# Professional Experience Related
def sort_professional_experience(soup):
	"""Sort professional experiences into individual ones"""
	try:
		cv_details_inner_wrap = soup.find(
			'div', attrs={'class': 'cv-details-inner-wrap'})
	except:
		logging.debug('Could not find: cv-details-inner-wrap')
		return None
	else:
		all_cv_details_inner = cv_details_inner_wrap.find_all(
			'div', attrs={'class': 'cv-details-inner'})
		content_div = all_cv_details_inner[2]
		professional_experience_marker = content_div.find(
			'div', attrs={'class': 'heading'}).text.strip().lower()
		content_div_soup = content_div.find('div', attrs={'class': 'content'})
		if professional_experience_marker == 'work experience':
			try:
				content_div = all_cv_details_inner[2]
				content_div_soup = content_div.find('div', attrs={'class': 'content'})
				# Get top level divs in content div
				content_all_divs = content_div_soup.find_all('div', recursive=False)

				# Get Individual companies indexes
				ind_companies_indexes = []
				for div_index, div_data in enumerate(content_all_divs):
					if div_data.attrs['class'][0] == 'exp-container':
						ind_companies_indexes.append(div_index)
					else:
						continue

				start_index = None
				end_index = None

				professional_experience_sorted = []
				for list_index, list_value in enumerate(ind_companies_indexes):
					try:
						start_index = ind_companies_indexes[list_index]
						end_index = ind_companies_indexes[list_index+1]
					except IndexError:
						# Will enter for the last element in the list
						professional_experience_sorted.append(
							content_all_divs[(ind_companies_indexes[-1]):])
					else:
						professional_experience_sorted.append(
							content_all_divs[start_index:end_index])
				return professional_experience_sorted
			except:
				logging.debug('PROFESSIONAL EXPERIENCE EXTRACTIONl: Went for a six!')
				return None
		else:
			logging.debug(
				'PROFESSIONAL EXPERIENCE EXTRACTION: Work experience div not found')
			return None


def extract_professional_experience_data(sorted_experience_data):
	"""Extract data from sorted expreiences"""
	extracted_data_consolidated = []
	for ind_company in sorted_experience_data:
		ind_exp_data = {
					'company_name': None,
			   					'designation': None,
			   					'duration': None,
			   					'summary': None,
			   					'projects_data': None
				}
		try:
			# This would be the experience container
			company_info_div = ind_company[0]
		except:
			logging.debug('PROFESSIONAL EXP: company_info_div not found')
		else:
			try:
				designation = company_info_div.find(
					'div', attrs={'class', 'time'}).text.strip()
				if designation:
					designation = ' '.join([word.strip() for word in designation.split()])
			except:
				logging.debug('SCRAPING ERROR: Professional experience designation')
			else:
				designation_cleaned, duration_extracted = nau_features_extractor.prof_exp_clean_duration_designation(
					designation)
				ind_exp_data['designation'] = designation_cleaned
				ind_exp_data['duration'] = nau_features_extractor.pro_exp_duration_calculations(
					duration_extracted)
			# Company name
			try:
				company_name = company_info_div.find(
					'div', attrs={'class': 'org'}).text.strip()
				if company_name:
					company_name = ' '.join([word.strip() for word in company_name.split()])
			except:
				logging.debug('SCRAPING ERROR: Professional experience comapny name')
			else:
				ind_exp_data['company_name'] = company_name

			# Description
			try:
				description = company_info_div.find(
					'div', attrs={'class': 'details'}).text.strip()
				if description:
					description = ' '.join([word.strip() for word in description.split()])
			except:
				logging.debug('SCRAPING ERROR: Professional experience description')
			else:
				ind_exp_data['summary'] = description

			try:
				all_projects_data = []
				for ind_project in ind_company[1:]:
					try:
						text_data = ind_project.text
					except:
						print('exception text_data individual project')
					else:
						text_data_cleaned = ' '.join([word.strip()
													for word in text_data.split()])
						all_projects_data.append(text_data_cleaned)
			except:
				ind_exp_data['projects_data'] = None
			else:
				ind_exp_data['projects_data'] = ' '.join(all_projects_data)

		extracted_data_consolidated.append(ind_exp_data)

	return extracted_data_consolidated


def extract_key_skills(soup):
	"""Extracting key skills from top container"""
	try:
		right_container = soup.find('div', attrs={'class': 'right-container'})
	except:
		return None
	else:
		try:
			key_skills = right_container.find(
				'p', attrs={'class': 'itSkill hKwd'}).text
		except:
			return None
		else:
			key_skills_splitted = [word.strip()
						  for word in key_skills.split(',')]
			key_skills_cleaned = [' '.join(skill.split())
						 for skill in key_skills_splitted]
			return key_skills_cleaned


def extract_basic_info(soup):
	"""
		Scrape basic profile information
		1. Name
		2. Total years of experience
		3. Current Salary
		4. Current Location
		5. Highest Degree
		6. Key skills
		7. Current company

	"""

	profile_basic_info = {
		'name': None,
		'total_experience': None,
		'total_experience_float': None,
		'current_salary': None,
		'current_location': None,
		'highest_degree': None,
		'key_skills_naukri': None,
	}

	# Get name container
	name_container = soup.find('div', attrs={'class': 'nameCont'})
	# Get all divs in nameCont
	name_container_contents = name_container.find_all('div')
	try:
		candidate_name_html = name_container_contents[0]
	except:
		logging.debug(
			'First key - Name html not found in name_container_contents')
	else:
		profile_basic_info['name'] = candidate_name_html.text.strip()

	try:
		candidate_exp_loc_sal_html = name_container_contents[1]
	except:
		logging.debug(
			'Second key - Experience, location, salary html not found in name_container_contents')
	else:
		candidate_exp_loc_sal_data = candidate_exp_loc_sal_html.find_all(
			'span')
		# Total experience is at index 0
		# Current compensation is at 1
		# Current location is at 2
		try:
			exp_data = candidate_exp_loc_sal_data[0].text.strip()
		except:
			logging.debug(
				'Experience text not found candidate_exp_loc_sal_data[0].text.strip()')
		else:
			profile_basic_info['total_experience'] = exp_data
			profile_basic_info['total_experience_float'] = nau_features_extractor.convert_total_exp_float(
				exp_data)

		try:
			sal_data = candidate_exp_loc_sal_data[1].text.strip()
		except:
			logging.debug(
				'Salary text not found candidate_exp_loc_sal_data[1].text.strip()')
		else:
			profile_basic_info['current_salary'] = sal_data

		try:
			current_location = candidate_exp_loc_sal_data[2].text.strip()
		except:
			logging.debug('Location text not found')
		else:
			profile_basic_info['current_location'] = current_location

		# Extracting key skills
		profile_basic_info['key_skills_naukri'] = extract_key_skills(soup)

	return profile_basic_info


def extract_academic_info(soup):
	"""Extract academic information"""
	try:
		acad_div = soup.find('div', attrs={'id': 'jump-education'})
	except:
		return None
	else:
		try:
			# list
			target_divs = acad_div.find_all(
				'div', attrs={'class': 'education-inner'})
		except:
			return None
		else:
			all_academic_exp = []
			for ind_acad in target_divs:
				ind_acad_exp = {
					'degree_level': None,
					'institute': None,
					'degree': None,
					'year': None
				}
				# Education level
				try:
					title = ind_acad.find(
						'div', attrs={'class': 'title'}).text.strip()
				except:
					logging.debug('Education title not found')
				else:
					ind_acad_exp['degree_level'] = title

				# Degree
				try:
					degree = ind_acad.find(
						'div', attrs={'class': 'detail'}).text.strip()
				except:
					logging.debug('Education degree not found')
				else:
					ind_acad_exp['degree'] = degree
					ind_acad_exp['year'] = nau_features_extractor.extract_year_from_degree(
						degree)

				# Institute
				try:
					institute = ind_acad.find(
						'div', attrs={'class': 'org'}).text.strip()
				except:
					logging.debug('Institute not found')
				else:
					ind_acad_exp['institute'] = institute

				all_academic_exp.append(ind_acad_exp)
			return all_academic_exp


def extract_professional_experience_skills(soup):
	"""Mentioned by the candidate - Top right of resume page"""
	try:
		cv_details_inner_wrap = soup.find(
			'div', attrs={'class': 'cv-details-inner-wrap'})
	except:
		logging.debug(
			'Could not find: cv-details-inner-wrap extract_professional_experience_skills()')
	else:
		all_cv_details_inner = cv_details_inner_wrap.find_all(
			'div', attrs={'class': 'cv-details-inner'})
		target_div = all_cv_details_inner[2]
		professional_experience_marker = target_div.find(
			'div', attrs={'class': 'heading'}).text.strip().lower()
		if professional_experience_marker == 'work experience':
			try:
				all_professional_experiences = target_div.find_all(
					'div', attrs={'class': 'project-details-box'})
				# for x in all_professional_experiences:
				#     print(x.text)
				#     print('#'*100)
			except:
				logging.debug(
					'List of professional experiences not found - exp-container (class)')
			else:
				combined_data_list = []
				for ind_exp in all_professional_experiences:
					data = ' '.join([word.strip()
											for word in ind_exp.text.split()])
					combined_data_list.append(data)
				return ' '.join(combined_data_list)


def extract_naukari_skills_info(soup):
	"""Extract Individual Skills information - End of resume page"""
	try:
		cv_details_inner_wrap = soup.find(
			'div', attrs={'class': 'cv-details-inner-wrap'})
	except:
		logging.debug('Could not find: cv-details-inner-wrap')
	else:
		try:
			it_skills = cv_details_inner_wrap.find(
				'div', attrs={'id': 'jump-it-skill'})
		except:
			logging.debug('SCRAPING ERROR: IT Skills table extraction')
			return None
		else:
			if it_skills:
				it_skills_data = []
				target_table = it_skills.find('table')
				for row in target_table.find_all('tr')[1:]:
					ind_skill_data = {
						'skill': None,
						'last_used_year': None,
						'skill_total_experience': None
					}
					for cell_index, cell_content in enumerate(row.find_all('td')):
						if cell_index == 0:
							ind_skill_data['skill'] = cell_content.text.strip()
						elif cell_index == 2:
							ind_skill_data['last_used_year'] = cell_content.text.strip(
							)
						elif cell_index == 3:
							ind_skill_data['skill_total_experience'] = cell_content.text.strip(
							)
						else:
							continue
					it_skills_data.append(ind_skill_data)
				return it_skills_data
			else:
				return None


def extract_resume_last_updated(soup):
	"""Extract last updated date"""
	target_div = soup.find('div', attrs={'class': 'tupleFoot'})
	# Find target span using the text it contains
	# Regex
	target_date = target_div.find(text=re.compile('^Modified'))
	if target_date:
		date_regex = re.compile(r"(Modified: )(.*\d)")
		cleaned_date = re.search(date_regex, target_date)
		if cleaned_date:
			try:
				return cleaned_date.group(2)
			except:
				return None
		else:
			return None
	else:
		return None

def extract_clean_complete_profile_text(soup):
	"""Data from complete profile page"""
	try:
		body_data = soup.find('div', attrs={'id': 'mainCvWrap'}).text
		body_data_cleaned = ' '.join([word.strip() for word in body_data.split()])
		body_data_cleaned = body_data_cleaned.replace('"', ' ')
	except:
		logging.debug('Body tag not found')
		return None
	else:
		return body_data_cleaned

def extract_linkedin_url(soup):
	"""Extract linkedin profile url"""
	try:
		online_presence_div = soup.find('div', attrs = {'id': 'jump-onlinePresence'})
	except:
		return None
	else:
		try:
			online_presence_links = online_presence_div.find_all('a', href=True)
		except:
			return None
		else:
			linkedin_profile_url = None
			linkedin_regex = re.compile(r'linkedin')
			if online_presence_links:
				for l in online_presence_links:
					linkedin_match = re.search(linkedin_regex, l['href'])
					if linkedin_match:
						linkedin_profile_url = l['href']
						break
					else:
						continue
			return linkedin_profile_url


	


def extract_github_repo_data(repo_url):
	"""Extract Github repositories data"""
	# Get Github repository
	request_response = requests.get(repo_url)
	# Get page text
	webpage_text = request_response.text
	# Create BS4 Soup
	github_repos_webpage_soup = BeautifulSoup(webpage_text, features='lxml')
	try:
		repo_data_container = github_repos_webpage_soup.find('div', attrs={'id': 'user-repositories-list'})
		logging.info('Repo data container found')
	except:
		logging.error('Did not find repositories conatiner')
		return None, None
	else:
		try:
			# Repository items
			repo_list = repo_data_container.find_all('li')
			logging.info('Github Repositories list items found')
		except:
			logging.error('Did not find list elements in webpage')
			return None, None
		else:
			repos_scraped_data = []
			for repo in repo_list:
				repo_data = {
					'topics': None,
					'language': None,
					'repo_name': None
				}
				try:
					topics_row = repo.find('div', attrs={'class': 'topics-row-container d-inline-flex flex-wrap flex-items-center f6 my-1'})
				except:
					logging.info('Did not find topics row')
				else:
					if topics_row != None:
						topics = topics_row.find_all('a', {'href':True})
						repo_data['topics'] = [topic['href'].rsplit('/')[-1] for topic in topics]
					else:
						pass
					try:
						language = repo.find('span', attrs = {'itemprop': 'programmingLanguage'})
					except:
						logging.info('Language not found')
					else:
						if language:
							repo_data['language'] = language.text
					try:
						repo_name = repo.find('a', attrs = {'itemprop': 'name codeRepository'})
					except:
						logging.info('Repository name not found')
					else:
						if repo_name:
							repo_name_raw = repo_name.text
							repo_name_cleaned = repo_name_raw.strip()
							repo_data['repo_name'] = repo_name_cleaned
					repos_scraped_data.append(repo_data)
			
			languages_all = []
			topics_all = []
			repos_name_all = []
			for dat in repos_scraped_data:
				if dat['topics'] != None:
					topics_all.extend(dat['topics'])
				if dat['language'] != None:
					languages_all.append(dat['language'])
				if dat['repo_name'] != None:
					repos_name_all.append(dat['repo_name'])


			languages_freq = dict(Counter(languages_all))
			topics_freq = dict(Counter(topics_all))
			return languages_freq, topics_freq, repos_name_all
			




def extract_github_url(soup):
	"""Extract Github url"""
	try:
		online_presence_div = soup.find('div', attrs = {'id': 'jump-onlinePresence'})
	except:
		return None, None
	else:
		try:
			online_presence_links_div = online_presence_div.find_all('a', href=True)
		except:
			return None, None
		else:
			github_profile_url = None
			github_regex = re.compile(r'github')
			if online_presence_links_div:
				for l in online_presence_links_div:
					github_match = re.search(github_regex, l['href'])
					if github_match:
						github_profile_url = l['href']
						break
					else:
						continue
			
			if github_profile_url != None:
				# Check if profile url or repositories url
				repositories_regex = re.compile(r'repositories$')
				repositories_match = re.search(repositories_regex, github_profile_url)
				if repositories_match:
					target_url = github_profile_url
				else:
					target_url = github_profile_url + "?tab=repositories"
				
				languages_freq, topics_freq, repos_name_all  = extract_github_repo_data(target_url)
				github_repo_data = {}
				github_repo_data['languages'] = languages_freq
				github_repo_data['topics'] = topics_freq
				github_repo_data['repos_name_all'] = repos_name_all
				github_profile_url = github_profile_url
				return github_profile_url, github_repo_data
			else:
				return None, None

def extract_contact_details(soup):
	"""Extract candidate contact details - email and phone no"""
	try:
		# Get email target div
		online_presence_div = soup.find('span', attrs = {'class': 'txtGreen bkt4 email'})
	except:
		return None
	else:
		try:
			email = online_presence_div.text
			email = email.strip()
		except:
			return None
		else:
			return email




def extract_professional_summary(all_resumes_list):
	"""main caller"""
	all_resumes_extracted_data = {}
	for resume in all_resumes_list:
		resume_html_bytes = resume.read()
		# TODO add check logging
		resume_html_string = str(resume_html_bytes, 'utf-8')

		try:
			# Create soup
			resume_soup = BeautifulSoup(resume_html_string, features='lxml')
		except:
			logging.debug('CONVERSION ERROR: Could not convert string to BS4 object')
		else:
			profile_data = {
				'data_source': 'naukari',
				'url': None,
				'name': None,
				'complete_profile_data_cleaned': None,
				'professional_summary_complete': None,
				'academic_summary_complete': None,
				'linkedin_url': None,
				'github_url': None,
				'github_data': None,
				'data_update_date': None,
				'highest_academic_qualification': None,
				'overall_years_experience': None,
				'overall_years_experience_float': None,
				'overall_technical_skills': None,
				'unspecified_technical_skills': None,
				'naukari_key_skills': None,
				'naukari_key_skills_annex': None,
				'current_ctc': None,
				'current_location': None,
				'location_preferences': None,
				'notice_period': None,
				'contact_email': None
			}

			# Basic Information of candidate
			profile_data['complete_profile_data_cleaned'] = extract_clean_complete_profile_text(resume_soup)
			profile_basic_info = extract_basic_info(resume_soup)
			profile_data['current_location'] = profile_basic_info['current_location']
			profile_data['current_ctc'] = profile_basic_info['current_salary']
			profile_data['highest_academic_qualification'] = profile_basic_info['highest_degree']
			profile_data['name'] = profile_basic_info['name']
			profile_data['overall_years_experience'] = profile_basic_info['total_experience']
			profile_data['naukari_key_skills'] = profile_basic_info['key_skills_naukri']
			profile_data['overall_years_experience_float'] = profile_basic_info['total_experience_float']
			profile_data['contact_email'] = extract_contact_details(resume_soup)
			profile_data['naukari_key_skills_annex'] = extract_naukari_skills_info(resume_soup)
			profile_data['data_update_date'] = extract_resume_last_updated(resume_soup)
			# Academic information
			profile_data['academic_summary_complete'] = extract_academic_info(
				resume_soup)

			# Professional Exprience Summary
			# Segregate professional experience data
			sorted_experience_data = sort_professional_experience(resume_soup)
			if sorted_experience_data == None:
				profile_data['professional_summary_complete'] = pro_exp_data_consolidated
			else:
				pro_exp_data_consolidated = extract_professional_experience_data(
					sorted_experience_data)
				profile_data['professional_summary_complete'] = pro_exp_data_consolidated

			# Extract data from github
			github_profile_url, github_repo_data = extract_github_url(resume_soup)
			profile_data['github_url'] = github_profile_url
			profile_data['github_data'] = github_repo_data

			# Extract linkedin url
			profile_data['linkedin_url'] = extract_linkedin_url(resume_soup)



			candidate_name = str(resume.filename)
			candidate_name = candidate_name.split('.htm')[0]
			candidate_name = candidate_name.split('/')[1]

			all_resumes_extracted_data[candidate_name] = profile_data
			
	with open('ALFA.json', 'w') as f:
		json.dump(all_resumes_extracted_data, f)

	return all_resumes_extracted_data


if __name__ == "__main__":
	pass  # TODO
