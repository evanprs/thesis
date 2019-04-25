"""
Serves to translate collections of Note objects into lilypond (to pdf).

!TODO:
- Account for quarter/eighth flats/sharps
"""



def extract_notes_in_range(all_notes, low_range=20, high_range=20000):
	"""
	Retrieves notes within range and discards those out of range.

	:param all_notes: List of Notes
	:param low_range: Frequency lower bound (in Hz)
	:param high_range: Frequency upper bound (in Hz)
	"""

	notes = []
	ii = 0

	for n in all_notes:
		if low_range < n.freq < high_range:
			notes.append(n)
		else:
			ii += 1
	
	# print(ii + " notes have been discarded.")

	return notes

def generate_lily_content(
	file_name, all_notes, 
	scale_harms, value_harms, reltv_harms
	):
	"""
	Generates the contents for a .ly file (for making pdf)
	"""

	ly_contents = ""
	
	ly_contents += generate_lily_version()
	ly_contents += generate_lily_header()
	ly_contents += generate_lily_all_notes(all_notes)
	ly_contents += generate_lily_harmonics(scale_harms, 1)
	ly_contents += generate_lily_harmonics(value_harms, 2)
	# ly_contents += generate_lily_harmonics(reltv_harms, 3)

	return ly_contents



def generate_lily_version(version="2.18.2"):
	"""
	Generates string of Lilypond version.

	:param version: Lilypond document version
	:return: String used in Lilypond file header
	"""

	o = "\\version \"" + version + "\"\n"
	o += "\\pointAndClickOff\n"

	return o

def generate_lily_header(title="Results"):
	"""
	Generates string of document title.

	:param title: Docment/Sheet music title
	:return: String used in Lilypond file header
	"""

	o = "\\header {\n  title = " + title + "\n}\n"

	return o

def separate_notes_by_clefs(all_notes):
	"""
	Separates notes into upper and lower halves (with respect to middle c).

	:param all_notes: List of Notes
	:return treble: String of lily version of notes that belong above middle c
	:return bass: String of lily version of notes that belong below middle c
	"""

	treble = ""
	bass = ""

	for n in all_notes:
		if n.octv < 4:
			treble += "s4 "
			bass += n.get_lily() + " "
		else:
			treble += n.get_lily() + " "
			bass += "s4 "
	
	return treble, bass

def separate_harms_by_clefs(harms):
	"""
	Separates harmonic notes into upper and lower halves (with respect to middle c). Primary note is made into a whole note, while harmonizing notes are made into quarter notes.

	:param all_notes: Hash of Harmonizing Notes
	:return treble: String of lily version of notes that belong above middle c
	:return bass: String of lily version of notes that belong below middle c
	"""

	treble = ""
	bass = ""

	for k,v in harms.items():
		if k.octv < 4:
			treble += "s1 "
			bass += k.get_lily(1) + " "
		else:
			treble += k.get_lily(1) + " "
			bass += "s1 "

		for n in v:
			if n.octv < 4:
				treble += "s4 "
				bass += n.get_lily(4) + " "
			else:
				treble += n.get_lily(4) + " "
				bass += "s4 "
		
		treble += "\\bar \"|.\"\n"
		bass += "\\bar \"|.\"\n"

	return treble, bass

def generate_lily_all_notes(all_notes):
	"""
	Separates notes into upper and lower halves (with respect to middle c).

	:param all_notes: List of Notes
	:return: String of lily version of notes representing all the audible notes
	"""

	o = "\\score\n  {\n  <<\n  \\new Staff = \"up\" {\n    "
	
	top, bot = separate_notes_by_clefs(all_notes)

	o += top

	o += "\n  }\n  \\new Staff = \"down\" {\n    \\clef bass {\n      "

	o += bot

	o += "\n    }\n  }\n  >>"

	o += "\n  \\header {\n    piece = \"All Notes\"\n  }\n}\n"
	
	return o

def generate_lily_harmonics(harms, mode=0):
	"""
	Separates harmonizing notes into upper and lower halves (with respect to middle c).

	:param all_notes: Hash of Harmonizing Notes
	:param mode: Type of harmonics
	:return: String of lily version of notes representing all the harmonics present
	"""

	o = "\\score\n  {\n  <<\n  \\new Staff = \"up\" {\n    "

	top, bot = separate_harms_by_clefs(harms)	

	o += top

	o += "\n  }\n  \\new Staff = \"down\" {\n    \\clef bass {\n      "

	o += bot

	o += "\n    }\n  }\n  >>"

	o += "\n  \\header {\n    piece = \"Harmonics"
	
	if (mode):
		o += " by "
		if (mode == 1):
			o += "Octave"
		elif (mode == 2):
			o += "Common Multiple"
		elif (mode == 3):
			o += "Strict Multiple"
	
	o += "\"\n  }\n}\n"
	
	return o



if __name__ == '__main__':
	# main()
# def main():
	"""
	The main function (used in development).
	Don't import this!
	"""
	print(generate_lily_version())
	print(generate_lily_header())