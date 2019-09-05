"""

	Prepare regex to extract technical skills 
	from extracted data from resumes

	Needs mapped_keywords.py

"""


import mapped_keywords as mapped_keywords
import re
import string


def get_variations_technical_skills(technical_skills_unmapped):
	"""Get variations of technicall skills using mapped_keywords"""
	search_terms_variations_list = []
	# Get all possible variations
	all_variations_technical_skills = []
	for skill_key, skill_variations in mapped_keywords.m_dict_technical.items():
		skill_variations_stripped = [word.strip() for word in skill_variations]
		skill_variations_lowercases = [word.lower()
								 for word in skill_variations_stripped]
		all_variations_technical_skills.extend(skill_variations_lowercases)

	for unmapped_skill in technical_skills_unmapped:
		unmapped_skill = unmapped_skill.lower()
		unmapped_skill = unmapped_skill.strip()
		if unmapped_skill in all_variations_technical_skills:
			for skill_key, skill_variations in mapped_keywords.m_dict_technical.items():
				skill_variations = [word.strip() for word in skill_variations]
				skill_variations = [word.lower() for word in skill_variations]
				if unmapped_skill in skill_variations:
					search_terms_variations_list.extend(skill_variations)
					break
				else:
					continue
		else:
			search_terms_variations_list.append(unmapped_skill)

	search_terms_variations_list_sorted = sorted(
		search_terms_variations_list, key=len, reverse=True)
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


def prepare_search_terms(search_terms_unmapped):
	# Raw search terms from form
	required_skills_unmapped = search_terms_unmapped['required_skills_unmapped']
	optional_skills_unmapped = search_terms_unmapped['optional_skills_unmapped']

	# Get all variations
	# IMPORTANT: Sort in descending order based on length
	required_skills_mapped = get_variations_technical_skills(required_skills_unmapped)
	optional_skills_mapped = get_variations_technical_skills(optional_skills_unmapped)

	# Add word boundary and escape characters
	required_skills_variations_for_regex = add_word_boundary_escape_chars(
		required_skills_mapped)
	optional_skills_variations_for_regex = add_word_boundary_escape_chars(
		optional_skills_mapped)
	# Prepare regex
	required_skills_regex = prepare_regex(required_skills_variations_for_regex)
	optional_skills_regex = prepare_regex(optional_skills_variations_for_regex)

	return required_skills_regex, optional_skills_regex


