#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Shilin Victor (chrono.monochrome@gmail.com)

import os, sys
import re
import translate
from collections import OrderedDict

_main_tbl_ptrns = [".?.?.?[\xe0-\xef].?.?", "\x00+", ".?\x01", "%[ds]",    \
                   "#[0-9]*[CI]", "#[0-9a-f]*/*", "[\x01-\x09\x0b-\x1c]+"]
				   
_item_ptrns = ["\x00{1}[D-\xcb]{1}\x00{1}.{1}[\x00-\n]{1}[\x00-\xfd]{1}.{1}[0-T]{1}[\x00-V]{1}"          \
"[\x00-\xca]{1}[\x00-\xc3]{1}[\x00-P]{1}[\x00-\xca]{1}[\x00-\xc8]{1}[\x00-\xb8]{1}[\x00-\xe8]{1}"        \
".{1}.{1}.{1}.{1}.{1}.{1}.{1}[\x00-\xc8]{1}[\x00-\x97]{1}.{1}[\x00-\xc8]{1}.{1}[\x00-\x19]{1}"           \
"[\x00-P]{1}\x00{1}.{1}[\x00-\x14]{1}[\x00-d]{1}\x00{1}[\x00-\x0f]{1}\x00{1}[\x00-\x0f]{1}"              \
"[\x00-\x03]{1}[\x00-\x0f]{1}\x00{1}.{1}[\x00-\x07]{1}[\x00-\xb4]{1}[\x00-\xe0]{1}.{1}[\x00-\xc3]{1}"    \
"[\x00-\xf4]{1}[\x00-\xf4]{1}.{1}.{1}[\x00-u]{1}[\x00-k]{1}.{1}.{1}.{1}.{1}.{1}.{1}[ -\xff]{1}", "\x00+"]

def _main_tbl_split(s):
	if s.find("NONE") == -1:
		text_start = [m.end() for m in re.finditer('\x00+', s)][-2]
	else:
		text_start = [m.end() for m in re.finditer('\x00+', s)][-4]
	data = s[:text_start]
	text = s[text_start:]
	return data, text
		
def _item_tbl_split(s):
	return "", s

_tbl_to_params = OrderedDict([('t_main.tbl',                       \
                               [["QSChapter", "QSTitle", "QSText"],\
                                _main_tbl_ptrns,                   \
                                _main_tbl_split]                   \
                              ),                                   \
                              ('t_text.tbl',                       \
                               [["TextTableData"],                 \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_item.tbl',                       \
                               [["item"],                          \
                               _item_ptrns,                        \
                               _item_tbl_split]                    \
                              ),  
						    ])
							
def _read_xml(file):
	return translate.read_xml(file)
							
def _read_tbl(file):
	name = os.path.split(file)[-1]
	params = _tbl_to_params.get(name)
	return translate.read_tbl(file, *params)
	
def _read_file(file):
	ext = os.path.splitext(file)[-1]
	assert(ext in [".tbl", ".xml"])
	if ext == ".tbl":
		return _read_tbl(file)
	elif ext == ".xml":
		return _read_xml(file)

def xml_to_tbl(in_file, out_file = ""):
	header, l_groups = translate.read_xml(in_file)

	if not out_file:
		out_file = os.path.splitext(in_file)[0] + ".tbl"
	translate.write_tbl(out_file, header, l_groups)
	
def tbl_to_xml(in_file, out_file = ""):
	header, l_groups = _read_file(in_file)
	
	if not out_file:
		in_file = os.path.splitext(in_file)[0] + ".xml"
	translate.write_xml(out_file, header, l_groups)
	
def convert(in_file, out_file = ""):
	header, l_groups = _read_file(in_file)
	
	_in_file, _in_ext = os.path.splitext(in_file)
	if (_in_ext == ".tbl"):
		if not out_file:
			out_file = _in_file + ".xml"
			
		translate.write_xml(out_file, header, l_groups)
	elif (_in_ext == ".xml"):
		if not out_file:
			out_file = _in_file + ".tbl"
		translate.write_tbl(out_file, header, l_groups)
	
def merge_tbl(orig_file, data_file, out_file):
	out_format = os.path.splitext(out_file)[-1]
	assert(out_format in [".tbl", ".xml"])
	header1, res1 = _read_file(orig_file)
	header2, res2 = _read_file(data_file)
	
	n = min(len(res1), len(res2))
	for i in xrange(n):
		res1[i]["data"] = res2[i]["data"]

	if out_format == ".xml":
		translate.write_xml(out_file, header1, res1)
	elif out_format == ".tbl":
		translate.write_tbl(out_file, header1, res1)
		
def dump_text(in_file, out_file):
	header, l_groups = _read_file(in_file)
	return translate.dump_text(out_file, l_groups)
	
def dump_data(in_file, out_file):
	header, l_groups = _read_file(in_file)
	return translate.dump_data(out_file, l_groups)
	
def usage():
	print "fail"
	exit()
	
actions_tbl = {
	"xml_to_tbl": (xml_to_tbl, 1, 2),
	"tbl_to_xml": (tbl_to_xml, 1, 2),
	"merge":      (merge_tbl,  3, 3),
	"convert":    (convert,    1, 2),
	"dump_text":  (dump_text,  2, 2),
	"dump_data":  (dump_data,  2, 2)
}
	
if __name__ == "__main__":
	if sys.argv[1] not in actions_tbl.keys():
		usage()
	else:
		action_cb, min_args, max_args = actions_tbl[sys.argv[1]]
		if not (min_args <= len(sys.argv) - 2 <= max_args):
			usage()
		else:
			action_cb(*sys.argv[2:])