#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Shilin Victor (chrono.monochrome@gmail.com)

import xml.etree.ElementTree as ET
import os
import re
import chardet

from base64 import b64encode, b64decode
from collections import OrderedDict
from textwrap import *

TBL_SIGNATURE_LEN = 2
HEADER_TAG = "header"
ENTRY_TAG = "Entry"
GROUP_TAG = "Group"

common_entry_ptrns = ["\xe3\x8a\xa5", "\xe3\x8d\xbb", "\xe2\x98\x85", \
			"\xe3\x83\xbb", "\xef\xbc\x9f", "\xe2\x80\xbb", \
			"\xef\xbc\x8d", "\xe2\x97\x86", "\xef\xbd\xab", \
			"\x00+", ".?\x01", "%[ds]", "#[0-9]*[CI]",      \
			"#[0-9a-f]*"]

_match = lambda s, ptrns: any([re.match(i, s) for i in ptrns])
_build_or_ptrn = lambda ptrns: "(%s)" % "|".join(ptrns)

wrapper = TextWrapper()
wrapper.width = 30

# Another yet hack for some files
def is_text(s):
	# map(chr, range(0x80, 0x90))
	non_text_chars = frozenset(['\x80', '\x81', '\x82', '\x83', '\x84', '\x85', '\x86', 
			'\x87', '\x88', '\x89', '\x8a', '\x8b', '\x8c', '\x8d', '\x8e', '\x8f'])
	return not bool(set(s) & non_text_chars)

def u_test(s):
	"""Try converting string to unicode. 
	If that fails, will return base64-encoded string instead."""
	b64_encoded = False
	if type(s) == unicode:
		return s, b64_encoded

	try:
		try:
			res = s.decode("u8")
		except:
			res = s.decode("shift_jis")
	except:
		b64_encoded = True
		res = b64encode(s)

	if not is_text(s):
		b64_encoded = True
		res = b64encode(s)
		
	return res, b64_encoded
	
# FIXME: BELOW FUNCTION IS A HACK
# Replace it with a something better.
def _split(s):
	tmp = [m.end() for m in re.finditer('\x00+', s)]
	
	if len(tmp) == 1:
		text_start = tmp[0]
	else:
		try:
			text_start = tmp[-2]
		except:
			print len(tmp), tmp
			raise

	data = s[:text_start]
	text = s[text_start:]
	return data, text

# OBSOLETED. Use read_dat instead
def read_tbl(in_file, l_tbl_tags, entry_ptrns = common_entry_ptrns, split_cb = None):
	"""Read binary *.tbl file.
	Returns *.tbl header and list of OrderedDict's representing each text or binary data entry."""
		
	if not split_cb:
		split_cb = _split

	res = []
	data = open(in_file, "rb").read()
	
	entry_ptrn = _build_or_ptrn(entry_ptrns)
	tag_ptrn = _build_or_ptrn(l_tbl_tags)
	raw_strings = re.split(tag_ptrn, data)

	header = OrderedDict()
	header["data"] = b64encode(raw_strings[0])
	header["extension"] = os.path.splitext(in_file)[-1]

	tag_type = ""
	for raw_string in raw_strings[1:]:
		entry_group = OrderedDict()
		# If raw_string doesn't match with any tag, 
		# just proceed it as an entry text. Otherwise,
		# remember a tag type and proceed the next raw_string.
		if not raw_string in l_tbl_tags:
			data, raw_text = split_cb(raw_string)
		else:
			tag_type = raw_string
			continue
	
		entry_group["data"] = b64encode(data)
		entry_group["entries"] = []
		assert(tag_type)
		entry_group["type"] = tag_type
		tag_type = ""

		for entry_text in re.split(entry_ptrn, raw_text):
			if not entry_text:
				continue

			entry = OrderedDict()

			if not _match(entry_text, entry_ptrns):
				entry_text, b64 = u_test(entry_text)
				entry["text"] = entry_text
				if b64:
					entry["b64_encoded"] = b64
			else:
				entry["data"] = b64encode(entry_text)

			entry_group["entries"].append(entry)


		res.append(entry_group)

	return header, res
	
def _indent(elem, level = 0):
	i = "\n" + level * "  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			_indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def write_xml(out_file, header, l_groups):
	"""Write *.tbl file data to XML file.
	Params:
	@header - *.tbl file header
	@l_groups - list of OrderedDict's representing each text or binary data entry."""

	root = ET.Element("root")
	doc = ET.SubElement(root, "doc")
	ET.SubElement(doc, HEADER_TAG, encoding = header["encoding"], extension = header["extension"]).text = header["data"]
	
	idx = 0
	for l_group in l_groups:
		el_group = ET.SubElement(doc, GROUP_TAG, type = l_group["type"], data = l_group["data"], idx = "%d" % idx)
		for l_entry in l_group["entries"]:
			if "data" in l_entry:
				ET.SubElement(el_group, ENTRY_TAG, data = l_entry["data"]).text = ""
			elif "text" in l_entry:
				if l_entry.get("b64_encoded"):
					ET.SubElement(el_group, ENTRY_TAG, b64_encoded = "%s" %\
					        l_entry["b64_encoded"]).text = l_entry["text"]
				else:
					text, b64_encoded = u_test(l_entry["text"])
					if b64_encoded:
						ET.SubElement(el_group, ENTRY_TAG, b64_encoded = "True").text = text
					else:
						ET.SubElement(el_group, ENTRY_TAG).text = text
		
		idx += 1
		
	_indent(root)
	open(out_file, "wb").write(ET.tostring(root, encoding='utf8', method='xml'))
	
def read_xml(in_file):
	"""Read XML file containing parsed *.tbl file data.
	Returns *.tbl header and list of OrderedDict's representing each text or binary data entry."""

	res = []
	tree = ET.parse(in_file, parser = ET.XMLParser(encoding="utf-8"))
	root = tree.getroot()
	doc = root.find("doc")
	el_header = doc.find(HEADER_TAG)	
	el_groups = doc.findall(GROUP_TAG)
	for el_group in el_groups:
		entry_group = OrderedDict()
		entry_group["entries"] = []
		entry_group["data"] = el_group.get("data")
		entry_group["type"] = el_group.get("type")
		el_entries = el_group.findall(ENTRY_TAG)
		for el_entry in el_entries:
			entry = OrderedDict()
			data = el_entry.get("data")
			text = el_entry.text
			if data:
				entry["data"] = data
			elif text:
				entry["text"] = text
				b64 = el_entry.get("b64_encoded")
				if b64:
					entry["b64_encoded"] = eval(b64)
			entry_group["entries"].append(entry)
		res.append(entry_group)

	header = OrderedDict()
	header["data"] = el_header.text
	header["encoding"] = el_header.get("encoding")
	header["extension"] = el_header.get("extension")
	return header, res
	
def write_tbl(out_file, header, l_groups, encoding = ""):
	"""Write *.tbl data to file.
	Params:
	@header - *.tbl file header
	@l_groups - list of OrderedDict's representing each text or binary data entry."""
	
	res = []
	res.append(b64decode(header["data"]))
	if (not encoding and header["encoding"]):
		encoding = header["encoding"]

	if not encoding:
		raise(BaseException("no encoding defined"))
	
	for l_group in l_groups:
		res.append(l_group["type"])
		res.append(b64decode(l_group["data"]))
		for l_entry in l_group["entries"]:
			if "data" in l_entry:
				res.append(b64decode(l_entry["data"]))
			elif "text" in l_entry:
				if l_entry.get("b64_encoded"):
					text = b64decode(l_entry["text"])
				else:
					try:
						text = l_entry["text"].encode(encoding)
					except:
						print l_entry
						text = l_entry["text"]
						#raise
				
				res.append(text)
	open(out_file, "wb").write(b"".join(res))
	
def dump_text(out_file, l_groups, encoding = "u8"):
	"""Dump text entries of *.tbl file"""
	
	res = []
	idx = 0
	for l_group in l_groups:
		res.append("%d)\n" % idx)
		for entry in l_group["entries"]:
			if not "text" in entry:
				continue
			try:
				entry["text"].encode("u8")
			except UnicodeDecodeError, e:
				#print("entry: %s" % entry["text"])
				#print(str(e))
				#raise
				continue
			res.append(entry["text"] + "\n")
		idx += 1
	return open(out_file, "wb")\
	       .write("".join(res).encode("u8"))
		   
def dump_data(out_file, l_groups, encoding = "u8"):
	"""Dump data entries of *.tbl file"""
	res = []

	for l_group in l_groups:
		res.append(b64decode(l_group["data"]))
	return open(out_file, "wb").write(repr(res))
	
def wrap_text(l_groups):
	res = []
	
	for l_group in l_groups:
		entries = []
		for entry in l_group["entries"]:
			if "text" in entry:
				if entry["text"][-1] == "\n":
					entry["text"] = "\n".join(wrapper.wrap(entry["text"])) + "\n"
				else:
					entry["text"] = "\n".join(wrapper.wrap(entry["text"]))
			entries.append(entry)
		l_group["entries"] = entries
		res.append(l_group)
	return res
	
DAT_HEADER_END_SIGNATURE = "\x00\x05\x1e"

def dat_read_header(raw_data):
	h_start = 0
	h_end = raw_data.find(DAT_HEADER_END_SIGNATURE) + len(DAT_HEADER_END_SIGNATURE)
	header = raw_data[h_start: h_end]
	return header, raw_data[h_end:]

def _detect_shift_jis(s):
	# HACK: assume if entry contains at least one of shift_jis_bytes, then it's shift-jis encoded
	# shift_jis_bytes = map(chr, range(0x80, 0x90))
	shift_jis_bytes = ['\x80', '\x81', '\x82', '\x83', '\x84', '\x85', '\x86', '\x87', '\x88', '\x89', '\x8a', '\x8b', '\x8c', '\x8d', '\x8e', '\x8f'] 
	for b in shift_jis_bytes:
		for i in s:
			if b == i: return True
	return False

glob_matches, last_idx = [], 0

def read_dat(in_file):
	global glob_matches, last_idx
	def append_entry(list_, entry_content, entry_type):
		entry = OrderedDict()
		entry[entry_type] = entry_content
		list_.append(entry)

	res = []
	data = open(in_file, "rb").read()
	header = OrderedDict()
	header_raw, data = dat_read_header(data)
	header["data"] = b64encode(header_raw)

	# default to utf-8
	header["encoding"] = "utf-8"
	is_encoding_detected = False

	header["extension"] = os.path.splitext(in_file)[-1]
	
	entry_group = OrderedDict()
	entry_group["data"] = ""
	entry_group["entries"] = []
	entry_group["type"] = ""

	matches = [i for i in re.finditer("[^\x00-\x1F\x7F-\xFF]{4,}|[^\x00-\x3f\x61-\x6f\x92-\xff]{8,}", data)]

	if not matches:
		append_entry(entry_group["entries"], b64encode(data), "data")
		res.append(entry_group)
		return header, res

	glob_matches = matches

	first_match = matches[0]
	append_entry(entry_group["entries"], b64encode(data[: first_match.start()]), "data")
	
	buf = ""

	for i, match in enumerate(matches):
		s_curr, e_curr = match.start(), match.end()

		# Prepare data entry
		try:
			next_match = matches[i + 1]
			s_next, e_next = next_match.start(), next_match.end()
			data_entry = b64encode(data[e_curr: s_next])
			last_idx = s_next
		except IndexError:
			data_entry = b64encode(data[e_curr:])
			last_idx = len(data)
		
		# In the case there are several neighboring text entries, join
		# them into one. As only data entry appears, flush the buffer.
		buf += match.group()
		
		if data_entry or buf:
			append_entry(entry_group["entries"], buf, "text")
			if not is_encoding_detected:
				entry_encoding = chardet.detect(buf)
				if entry_encoding["confidence"] >= 0.99 and entry_encoding["encoding"] == "SHIFT_JIS":
					header["encoding"] = "shift-jis"
					is_encoding_detected = True

				if entry_encoding["confidence"] == .0:
					#print(repr(buf))
					if _detect_shift_jis(buf):
						header["encoding"] = "shift-jis"
						is_encoding_detected = True
					
			buf = ""
			if data_entry:
				append_entry(entry_group["entries"], data_entry, "data")
	#print(len(buf))
	res.append(entry_group)
	return header, res
