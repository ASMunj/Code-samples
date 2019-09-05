import mapped_keywords as mapped_keywords
import re
import string
from collections import Counter
import json


def get_variations_technical_skills():
	all_variations_technical_skills = []
	for skill_key, skill_variations in mapped_keywords.m_dict_technical.items():
		skill_variations_stripped = [word.strip() for word in skill_variations]
		skill_variations_lowercases = [word.lower()
								 for word in skill_variations_stripped]
		all_variations_technical_skills.extend(skill_variations_lowercases)

	search_terms_variations_list_sorted = sorted(all_variations_technical_skills, key=len, reverse=True)
	return search_terms_variations_list_sorted

# Add word boundary and escape characters
def add_word_boundary_escape_chars(search_terms_variations_list, word_boundary_all_terms=False):
	if word_boundary_all_terms == True:
		transformed_words = []
		for word in search_terms_variations_list:
			# Add escape characters
			escaped_word = word.translate(str.maketrans({"-": r"\-",
												"]": r"\]",
												"\\": r"\\",
												"^": r"\^",
												"$": r"\$",
												"*": r"\*",
												".": r"\.",
												"+": r"\+",
												"*": r"\*"}))
			# Add word boundary
			escaped_word = r'\b'+escaped_word+r'\b'
			transformed_words.append(escaped_word)
		return transformed_words

	else:
		transformed_words = []
		punc_chars = set(string.punctuation)
		# Strip and check length of word
		# Redundancy check
		for word in search_terms_variations_list:
			word = word.strip()
			# Discard if length is 0
			if len(word) == 0:
				continue

			if len(word) <= 3:
				# Check if it has punctuations
				if any(char in punc_chars for char in word):
					# Add escape chars only
					escaped_word = word.translate(str.maketrans({"-": r"\-",
												  "]": r"\]",
												  "\\": r"\\",
												  "^": r"\^",
												  "$": r"\$",
												  "*": r"\*",
												  ".": r"\.",
												  "+": r"\+",
												  "*": r"\*"}))
					transformed_words.append(escaped_word)
				else:
					word = r'\b'+word+r'\b'
					transformed_words.append(word)
			else:
				if any(char in punc_chars for char in word):
					# Add escape chars only
					escaped_word = word.translate(str.maketrans({"-": r"\-",
												  "]": r"\]",
												  "\\": r"\\",
												  "^": r"\^",
												  "$": r"\$",
												  "*": r"\*",
												  ".": r"\.",
												  "+": r"\+",
												  "*": r"\*"}))
					transformed_words.append(escaped_word)
				else:
					transformed_words.append(word)
		# Return list
		return transformed_words


# Prepare regexes
def prepare_regex(variations_transformed_list):
	search_terms_regex = re.compile('|'.join(variations_transformed_list))
	return search_terms_regex

# Technical skills
all_variations_technical_skills = []
for main_key, key_variations in mapped_keywords.m_dict_technical.items():
    key_variations = [word.lower() for word in key_variations]
    key_variations = [word.strip() for word in key_variations]
    all_variations_technical_skills.extend(key_variations)

def remap_technical_skills(skills_list):
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



def extract_terms(skills_regex, complete_profile_data_cleaned):
	if len(complete_profile_data_cleaned) > 0:
		complete_profile_data_cleaned = ' '.join(complete_profile_data_cleaned)
		complete_profile_data_cleaned = complete_profile_data_cleaned.lower()

		tech_skills_match = re.findall(skills_regex, complete_profile_data_cleaned)
		if tech_skills_match:
			remapped_skills = remap_technical_skills(tech_skills_match)
			return remapped_skills
		else:
			return None

	else:
		return None


def remove_job_spec_skills(required_skills_mapped, optional_skills_mapped, tech_skills_unspecified_mapped):
	if required_skills_mapped == None:
		required_skills_mapped = []

	if optional_skills_mapped == None:
		optional_skills_mapped = []

	filtered_unspecified_skills = []
	if len(tech_skills_unspecified_mapped) == 0:
		return None
	else:
		tech_skills_unspecified_mapped = list(set(tech_skills_unspecified_mapped))
		for skill in tech_skills_unspecified_mapped:
			if skill in required_skills_mapped or skill in optional_skills_mapped:
				continue
			else:
				filtered_unspecified_skills.append(skill)
		
		if len(filtered_unspecified_skills) == 0:
			return None
		else:
			return filtered_unspecified_skills

def main_caller(required_skills_mapped, optional_skills_mapped, complete_profile_data_cleaned):
	tech_skills_variations = get_variations_technical_skills()
	tech_skills_prepared =  add_word_boundary_escape_chars(tech_skills_variations)
	skills_regex = prepare_regex(tech_skills_prepared) 
	extracted_terms = extract_terms(skills_regex, complete_profile_data_cleaned)
	remapped_extracted_terms = remap_technical_skills(extracted_terms)
	filtered_unspecified_skills = remove_job_spec_skills(required_skills_mapped, optional_skills_mapped, remapped_extracted_terms)
	return filtered_unspecified_skills