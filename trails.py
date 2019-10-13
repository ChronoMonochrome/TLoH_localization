#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Shilin Victor (chrono.monochrome@gmail.com)

import os, sys
import re
import shutil
import fnmatch

import translate
from collections import OrderedDict

_main_tbl_ptrns = ["\x00+", "\x1d", ".?\x01", "%[ds]",    \
                   "#[0-9]*[CI]", "#[0-9a-f]*/*", "[\x01-\x09\x0b-\x1c]+"]

_item_tbl_ptrns = [".*\xff\xff"]

def _main_tbl_split(s):
	if s.find("NONE") == -1:
		text_start = [m.end() for m in re.finditer('\x00+', s)][-2]
	else:
		text_start = [m.end() for m in re.finditer('\x00+', s)][-4]
	data = s[:text_start]
	text = s[text_start:]
	return data, text

def _item_tbl_split(s):
	#if len(s) >= 55:
	#	return s[:55], s[55:]
	#else:
	return "", s

_tbl_to_params = OrderedDict([('t_main',                           \
                               [["QSChapter", "QSTitle", "QSText"],\
                                _main_tbl_ptrns,                   \
                                _main_tbl_split]                   \
                              ),                                   \
                              ('t_text',                           \
                               [["TextTableData"],                 \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_item',                           \
                               [["item"],                          \
                               _item_tbl_ptrns,                    \
                               _item_tbl_split]                    \
                              ),                                   \
                              ('t_active',                         \
                               [["ActiveVoiceTableData"],          \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_book',                           \
                               [["QSBookScp",                      \
                                 "QSChapter", "QSBook"],           \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_btlsys',                         \
                               [["TacticalBonus"],                 \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_dlc',                            \
                               [["dlc"],                           \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_fish',                           \
                               [["fish_pnt"],                      \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_hikitugi',                       \
                               [["hkitugi_lst"],                   \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_jump',                           \
                               [["MapJumpData"],                   \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_linkab',                         \
                               [["LinkAbList"],                    \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_magic',                          \
                               [["magic"],                         \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_mg02',                           \
                               [["MG02Title", "MG02Text"],         \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_mons',                           \
                               [["status"],                        \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_mstqrt',                         \
                               [["MasterQuartzBase",               \
                                 "MasterQuartzData",               \
                                 "MasterQuartzMemo"],              \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_name',                           \
                               [["NameTableData"],                 \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_navi',                           \
                               [["NaviTextData"],                  \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_notechar',                       \
                               [["QSChapter", "QSChar"],           \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_notecook',                       \
                               [["QSCook"],                        \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_notefish',                       \
                               [["QSFish"],                        \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_notehelp',                       \
                               [["QSChapter", "QSHelp"],           \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_notemons',                       \
                               [["QSChapter", "QSMons"],           \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                              ('t_place',                          \
                               [["PlaceTableData"],                \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                             ('t_quest',                           \
                               [["QSRank", "QSTitle", "QSText"],   \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                             ('t_status',                          \
                               [["growth", "status"],              \
                               translate.common_entry_ptrns,       \
                               translate._split]                   \
                              ),                                   \
                             ])

def _read_xml(file):
	return translate.read_xml(file)

def _read_dat(file):
	return translate.read_dat(file)

def _read_tbl(file):
	name = os.path.split(file)[-1]

	found = False
	for key, params in _tbl_to_params.items():
		if file.find(key) != -1:
			found = True
			break

	assert(found)
	return translate.read_tbl(file, *params)

def _read_file(file):
	ext = os.path.splitext(file)[-1]
	assert(ext in [".tbl", ".xml", ".dat"])
	if ext == ".tbl":
		return _read_dat(file)
	elif ext == ".xml":
		return _read_xml(file)
	elif ext == ".dat":
		return _read_dat(file)

def xml_to_tbl(in_file, out_file = "", encoding = ""):
	header, l_groups = translate.read_xml(in_file)

	if not out_file:
		out_file = os.path.splitext(in_file)[0] + ".tbl"
	translate.write_tbl(out_file, header, l_groups, encoding = encoding)

def tbl_to_xml(in_file, out_file = ""):
	header, l_groups = _read_file(in_file)

	if not out_file:
		out_file = os.path.splitext(in_file)[0] + ".xml"
	translate.write_xml(out_file, header, l_groups)

def dat_to_xml(in_file, out_file = ""):
	header, l_groups = _read_file(in_file)
	if not out_file:
		out_file = os.path.splitext(in_file)[0] + ".xml"
	translate.write_xml(out_file, header, l_groups)

def xml_to_dat(in_file, out_file = "", encoding = "u8"):
	header, l_groups = translate.read_xml(in_file)

	if not out_file:
		out_file = os.path.splitext(in_file)[0] + ".dat"
	translate.write_tbl(out_file, header, l_groups, encoding = encoding)

def _get_out_filename(in_filename, in_ext):
	if (in_ext == ".tbl"):
		return in_filename + ".xml"
	elif (in_ext == ".xml"):
		return in_filename + ".tbl"

def convert(in_file, out_file, encoding = ""):
	header, l_groups = _read_file(in_file)

	_in_file, _in_ext = os.path.splitext(in_file)

	if (_in_ext in [".tbl", ".dat"]):
		translate.write_xml(out_file, header, l_groups)
	elif (_in_ext == ".xml"):
		translate.write_tbl(out_file, header, l_groups, encoding = encoding)

def wrap_text(in_file, out_file, encoding = ""):
	header, l_groups = _read_file(in_file)

	l_groups = translate.wrap_text(l_groups)

	_out_file, _out_ext = os.path.splitext(out_file)

	if (_out_ext == ".xml"):
		translate.write_xml(out_file, header, l_groups)
	elif (_out_ext == ".tbl"):
		translate.write_tbl(out_file, header, l_groups, encoding = encoding)

def merge_tbl(orig_file, data_file, out_file, encoding = ""):
	out_format = os.path.splitext(out_file)[-1]
	assert(out_format in [".tbl", ".xml"])
	header1, res1 = _read_file(orig_file)
	header2, res2 = _read_file(data_file)

	n = min(len(res1), len(res2))
	for i in xrange(n):
		res1[i]["data"] = res2[i]["data"]

	if out_format == ".xml":
		translate.write_xml(out_file, header1, res1)
	elif out_format in [".tbl", ".dat"]:
		translate.write_tbl(out_file, header1, res1, encoding = encoding)

def dump_text(in_file, out_file, encoding = "u8"):
	header, l_groups = _read_file(in_file)
	return translate.dump_text(out_file, l_groups, encoding = encoding)

def dump_data(in_file, out_file, encoding = "u8"):
	header, l_groups = _read_file(in_file)
	return translate.dump_data(out_file, l_groups, encoding = encoding)

def encode(in_file, out_file, out_enc):
	header, l_groups = _read_file(in_file)
	translate.write_tbl(out_file, header, l_groups, out_enc)
	
COPY = "copy"
CONVERT = "convert"

OPERATIONS = [COPY, CONVERT]

def bulk_files_operation(src_dir, dest_dir, patterns, operation):
	"""
	Perform bulk operations on files.
	@src_dir: source directory to perform operations on.
	@dest_dir: destination directory
	@patterns: list of filename patterns to match in source directory.
	@operation: either copy or convert."""
	src_dir = os.path.realpath(src_dir)
	dest_dir = os.path.realpath(dest_dir)
	for root, dirs, files in os.walk(src_dir):
		for basename in files:
			for pattern in patterns:
				if fnmatch.fnmatch(basename, pattern):
					src_filename = os.path.join(root, basename)
					root_abs = os.path.abspath(root)
					root_rel = root_abs.split(src_dir)[-1]
					if root_rel[0] in ["/", "\\"]:
						root_rel = root_rel[1:]
					out_dir = os.path.join(dest_dir, root_rel)
					if not os.path.exists(out_dir):
						#print("create %s" % out_dir)
						os.makedirs(out_dir)

					if operation == COPY:
						dest_filename = os.path.join(dest_dir, os.path.join(root_rel, basename))
						#print("copy %s to %s" % (src_filename, dest_filename))
						shutil.copy(src_filename, dest_filename)
					elif operation == CONVERT:
						filename_no_ext, ext = os.path.splitext(basename)
						if ext == ".xml":
							dest_filename = os.path.join(dest_dir, os.path.join(root_rel, filename_no_ext))
						else:
							dest_filename = os.path.join(dest_dir, os.path.join(root_rel, filename_no_ext + ".xml"))
						convert(src_filename, dest_filename)
						
def bulk_copy(src_dir, dest_dir):
	bulk_files_operation(src_dir, dest_dir, ["*.tbl", "*.dat"], COPY)

def usage(commands_tbl, error = ""):
	buf =  ["The Legend of Heroes: Trails of Cold Steel localization scripts\n"]
	commands = commands_tbl.items()
	max_com_len = max([len(i[0]) for i in commands])
	max_args_len = max([sum(len(arg) for arg in i[1][-2]) + len(i[1]) for i in commands])
	com_list = []
        for k, v in commands:
		com = ("  %s %s" % (k.ljust(max_com_len), " ".join(v[-2]))) \
                                     .ljust(max_com_len + max_args_len)
		com_list.append("%s - %s" % (com, v[-1]))

        if error: buf.append(error + "\n")
	buf.append("Usage: trails.py command args\n")
	buf.append("Commands:")
	buf += com_list
	print("\n".join(buf))
	exit()

def main():
	commands_tbl = {
	        # command       function   min_arg max_arg            args                        desc
		"xml_to_tbl" : [xml_to_tbl,   1,      3,    ["src.xml", "[dest.tbl]", "[encoding]"],  ""],
		"tbl_to_xml" : [tbl_to_xml,   1,      2,    ["src.tbl", "[dest.xml]"],                ""],
		"dat_to_xml" : [dat_to_xml,   1,      2,    ["src.dat", "[dest.xml]"],                ""],
		"xml_to_dat" : [xml_to_dat,   1,      3,    ["src.xml", "[dest.dat]", "[encoding]"],  ""],
		"merge"      : [merge_tbl,    3,      4,    ["src1.{tbl,xml}", "src2.{tbl,xml}",
	                                                     "dest.{tbl,xml}", "[encoding]"],     ""],
		"convert"    : [convert,      2,      3,    ["src.{tbl,dat,xml}",
	                                                     "dest.{tbl,dat,xml}", "[encoding]"], ""],
		"dump_text"  : [dump_text,    2,      3,    ["src.tbl",   "dest.txt", "[encoding]"],  ""],
		"dump_data"  : [dump_data,    2,      3,    ["src.tbl",   "dest.txt", "[encoding]"],  ""],
		"wrap"       : [wrap_text,    2,      3,    ["src.{tbl,dat,xml}",
	                                                     "dest.{tbl,dat,xml}", "[encoding]"], ""],
		"encode"     : [encode,       3,      3,    ["src1.{tbl,xml}", "dest.{tbl,xml}",
	                                                     "encoding"],                         ""],
		"bulk_copy"  : [bulk_copy,    2,      2,    ["source_dir", "dest_dir"],               ""]
	}

	commands_tbl["xml_to_tbl"][-1] = "convert *.xml file to *.tbl."
	commands_tbl["tbl_to_xml"][-1] = "convert *.tbl file to *.xml."
	commands_tbl["dat_to_xml"][-1] = "convert *.dat file to *.xml."
	commands_tbl["xml_to_dat"][-1] = "convert *.xml file to *.dat."
	commands_tbl["merge"][-1]      = "use a text entries of src1 and a data entries of src2 and write result to destination file."
	commands_tbl["convert"][-1]    = "convert *.{tbl,dat,xml} file to dest.{tbl,dat,xml}."
	commands_tbl["dump_text"][-1]  = "extract text entries from src.tbl and write to dest.txt."
	commands_tbl["dump_data"][-1]  = "extract data entries from src.tbl and write to dest.txt."
	commands_tbl["wrap"][-1]       = "wrap text entries in a source file so that they fit on the display."
	commands_tbl["encode"][-1]     = "change encoding of a source file."
	commands_tbl["bulk_copy"][-1]  = "bulk copy *.tbl and *.dat files from source_dir to dest_dir."
 	if len(sys.argv) < 2:
		usage(commands_tbl)

        command = sys.argv[1]

	if command not in commands_tbl.keys():
		usage(commands_tbl, error = "%s: command not found" % command)
	else:
		command_cb, min_args, max_args, args, desc = commands_tbl[command]
		if not (min_args <= len(sys.argv) - 2 <= max_args):
			usage(commands_tbl, error = "%s: from %d to %d arguments are required, but %d provided" \
                                                            % (command, min_args, max_args, len(sys.argv) - 2))
		else:
			command_cb(*sys.argv[2:])


if __name__ == "__main__":
	main()
