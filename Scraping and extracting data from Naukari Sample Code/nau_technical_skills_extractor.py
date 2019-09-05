import re
import string
from collections import Counter
import json

from NauFeaturesExtractor import nau_prepare_js_regex
from NauFeaturesExtractor import nau_extract_non_js_skills

import mapped_keywords as mapped_keywords

all_variations_technical_skills = []
for main_key, key_variations in mapped_keywords.m_dict_technical.items():
	key_variations = [word.lower() for word in key_variations]
	key_variations = [word.strip() for word in key_variations]
	all_variations_technical_skills.extend(key_variations)


def remap_technical_skills(skills_list):
	"""Remapping technical skills using mapped_keywords"""
	# Store remapped technical skills
	remapped_technical_skills = []
	for raw_skill in skills_list:
		raw_skill = raw_skill.strip()
		if raw_skill in all_variations_technical_skills:
			for mapped_key, key_variations in mapped_keywords.m_dict_technical.items():
				key_variations = [word.lower() for word in key_variations]
				key_variations = [word.strip() for word in key_variations]
				if raw_skill in key_variations:
					remapped_technical_skills.append(mapped_key)
					break
				else:
					continue
		else:
			remapped_technical_skills.append(raw_skill)
	return remapped_technical_skills


def technical_skills_duplicate_remover(mapped_skills_list):
	"""Removed duplicates from mapped skills"""
	if mapped_skills_list != None:
		return list(set(mapped_skills_list))
	else:
		return None


def technical_skills_frequency_counts(mapped_skills_list):
	"""Get frequency coutns of mapped technical skills"""
	if mapped_skills_list != None:
		technical_skills_counts = dict(Counter(mapped_skills_list))
		return technical_skills_counts
	else:
		return None



def get_prof_exp_target_dump(pro_exp_data):
	"""Combine professional experience data for tech skills extraction"""
	combined_data_list = []
	try:
		try:
			combined_data_list.append(pro_exp_data['summary'])
		except:
			pass
		try:
			combined_data_list.append(pro_exp_data['projects_data'])
		except:
			pass
	except:
		print('TODO Log')
	else:
		combined_data_str_lowered = ' '.join([el.lower() for el in combined_data_list if el!= None])
		combined_data_ret = ' '.join([word.strip() for word in combined_data_str_lowered.split()])
		return combined_data_ret
	


def extract_technical_skills(required_skills_regex, optional_skills_regex, extraction_data_dump):
	"""Extract technical skills from extraction_data_dump(str) using prebuilt regexes"""
	if isinstance(extraction_data_dump, str):
		technical_skills = {
			'ext_required_skills_raw': None,
			'ext_required_skills_mapped': None,
			'ext_required_skills_mapped_frequency': None,
			'ext_required_skills_unique': None,
			'ext_optional_skills_raw': None,
			'ext_optional_skills_mapped': None,
			'ext_optional_skills_mapped_frequency': None,
			'ext_optional_skills_unique': None
		}
		if len(extraction_data_dump.strip()) == 0:
			return None
		else:
			# Fetch required skills
			required_skills_match = re.findall(
				required_skills_regex, extraction_data_dump.lower())

			if required_skills_match:
				technical_skills['ext_required_skills_raw'] = required_skills_match
				technical_skills['ext_required_skills_mapped'] = remap_technical_skills(
					required_skills_match)
				technical_skills['ext_required_skills_mapped_frequency'] = technical_skills_frequency_counts(
					technical_skills['ext_required_skills_mapped'])
				technical_skills['ext_required_skills_unique'] = technical_skills_duplicate_remover(
					technical_skills['ext_required_skills_mapped'])

			# Fetch optional skills
			optional_skills_match = re.findall(
				optional_skills_regex, extraction_data_dump.lower())

			if optional_skills_match:
				technical_skills['ext_optional_skills_raw'] = optional_skills_match
				technical_skills['ext_optional_skills_mapped'] = remap_technical_skills(
					optional_skills_match)
				technical_skills['ext_optional_skills_mapped_frequency'] = technical_skills_frequency_counts(
					technical_skills['ext_optional_skills_mapped'])
				technical_skills['ext_optional_skills_unique'] = technical_skills_duplicate_remover(
					technical_skills['ext_optional_skills_mapped'])

			return technical_skills
	else:
		return None



		
def tech_skills_extractor(candidates_data_for_extraction, search_terms_unmapped):
	"""Main caller for extracting technical skills from resume extracted data"""
	required_skills_regex, optional_skills_regex = nau_prepare_js_regex.prepare_search_terms(
		search_terms_unmapped)
	# Loop through individual resumes
	for resume_data_id, resume_data in candidates_data_for_extraction.items():
		# Loop through individual professional experiences
		# Get professional experience data - Cleaned
		if resume_data['professional_summary_complete'] != None:
			if len(resume_data['professional_summary_complete']) > 0:
				for ind_pro_exp in resume_data['professional_summary_complete']:
					ind_pro_exp['professional_exp_target_dump'] = get_prof_exp_target_dump(ind_pro_exp)
					ind_pro_exp['tech_skills_metrics'] = extract_technical_skills(
			required_skills_regex, optional_skills_regex, ind_pro_exp['professional_exp_target_dump'])
			else:
				pass
		else:
			pass
		
		resume_data['technical_skills_metrics_overall_resume'] = extract_technical_skills(
			required_skills_regex, optional_skills_regex, resume_data['complete_profile_data_cleaned'])

		# try:
		# 	del resume_data['complete_profile_data_cleaned']
		# except:
		# 	Logging.debug("COULD NOT REMOVE KEY: del resume_data['complete_profile_data_cleaned']")


	return candidates_data_for_extraction
