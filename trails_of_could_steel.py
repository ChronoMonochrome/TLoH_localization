import translate
import os

def _main_tbl_split(s):
		if s.find("NONE") == -1:
			text_start = [m.end() for m in re.finditer('\x00+', s)][-2]
		else:
			text_start = [m.end() for m in re.finditer('\x00+', s)][-4]
		data = s[:text_start]
		text = s[text_start:]
		return data, text

_tbl_to_params = OrderedDict([('t_main.tbl',\
                             [["QSChapter", "QSTitle", "QSText"],\
							 [".?.?.?[\xe0-\xef].?.?", "\x00+", ".?\x01", "%[ds]", \
							  "#[0-9]*[CI]", "#[0-9a-f]*/*", "[\x01-\x09\x0b-\x1c]+"], \
							  _main_tbl_split]),\
						     ('t_text.tbl',\
							 [["TextTableData"],\
							 translate.common_entry_ptrns, \
							 None]) \
							])

def xml_to_tbl(in_file, out_file):
	header, l_groups = translate.read_xml(in_file)
	translate.write_tbl(out_file, header, l_groups)
	
def tbl_to_xml(in_file, out_file):
	name = os.path.split(in_file)[-1]
	params = _tbl_to_params.get(name)
	header, l_groups = translate.read_tbl(in_file, *params)
	write_xml(out_file, header, l_groups)