__author__ = 'sertansenturk'
import os
import csv

def extractMetadata(scorefile, useMusicBrainz = False):
	# get the metadata in the score name, works if the name of the 
	# file has not been changed
	metadata = dict()
	try:
		symbtrname = os.path.splitext(os.path.basename(scorefile))[0]
		[metadata['makam'], metadata['form'], metadata['usul'], metadata['name'], 
		metadata['composer']] = symbtrname.split('--')

		if isinstance(metadata['composer'], list):
			print 'The SymbTr name is not "makam--form--usul--name--composer"'
			metadata = dict()
	except ValueError:
		print 'The SymbTr name is not "makam--form--usul--name--composer"'
		
	# get the extension to determine the SymbTr-score format
	extension = os.path.splitext(scorefile)[1]

	if extension == ".txt":
		metadata['sections'] = extractSectionFromTxt(scorefile)
	elif extension == ".xml":
		metadata['sections'] = extractSectionFromXML(scorefile)
	elif extension == ".mu2":
		metadata['sections'] = extractSectionFromMu2(scorefile)
	else:
		print "Unknown format"
		return -1

	if useMusicBrainz:
		extractSectionFromMusicBrainz

def extractSectionFromTxt(scorefile):
	with open(scorefile, "rb") as f:
		reader = csv.reader(f, delimiter='\t')

		header = next(reader, None)
		lyrics_col = header.index('Soz1')
		offset_col = header.index('Offset')

		lyrics = []
		offset = []
		for row in reader:
			lyrics.append(row[lyrics_col])
			offset.append(row[offset_col])

	print lyrics

def extractSectionFromXML(scorefile):
	pass

def extractSectionFromMu2(scorefile):
	pass

def extractSectionFromMusicBrainz(scorefile):
	pass