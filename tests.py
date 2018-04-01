import sys, os, tempfile
import time
import unittest
import trails_of_could_steel as tloh

DEBUG = False
GAME_DATA_PATH = "/media/chrono/AMV/Games/_The Legend of Heroes Trails of Cold Steel/data"
DIRS_IGNORE_LIST = ["fonts"]
FILES_IGNORE_LIST = []

def dprint(s):
	if DEBUG:
		print(s)

def catch(debug_info = ""):
	__func__ = sys._getframe().f_back.f_code.co_name
	exc_type, exc_obj, exc_tb = sys.exc_info()
	dbg_msg = "%s: %s on line %d: %s" %(__func__, exc_type, exc_tb.tb_lineno, exc_obj)
	if debug_info:
		dbg_msg += debug_info
	return (dbg_msg)

class GameTests(unittest.TestCase):
	def setUp(self):
		self.verificationErrors = []

	def tearDown(self):
		pass #self.assertEqual([], self.verificationErrors)

	def _test_convert_integrity(self, tbl_in_filename):
		tmp_dir = tempfile._get_default_tempdir()
		tmp_prefix = next(tempfile._get_candidate_names())
		xml_out_filename = os.path.join(tmp_dir, "%s.xml" % tmp_prefix)
		tbl_out_filename = os.path.join(tmp_dir, "%s.tbl" % tmp_prefix)
		#time.sleep(1)
		try:
			#rd = open(xml_out_filename, "rb").read()
			#print("%s: read %d bytes" % (xml_out_filename, len(rd)))
			dprint("tloh.convert('%s', '%s')" % (tbl_in_filename, xml_out_filename))
			tloh.convert(tbl_in_filename, xml_out_filename)
			dprint("tloh.convert('%s', '%s')" % (xml_out_filename, tbl_out_filename))
			tloh.convert(xml_out_filename, tbl_out_filename)
		except:
			raise
		tbl_in = open(tbl_in_filename, "rb").read()
		tbl_out = open(tbl_out_filename, "rb").read()
		os.remove(xml_out_filename)
		os.remove(tbl_out_filename)

		return tbl_in, tbl_out

	def test_convert_integrity(self):
		self.assertTrue(os.path.isdir(GAME_DATA_PATH))
		for (path, dirs, files) in os.walk(GAME_DATA_PATH):
			if os.path.split(path)[-1] in DIRS_IGNORE_LIST:
				continue
			files = [i for i in files if (os.path.splitext(i)[-1] in [".tbl", ".dat"])]
			#print(path)
			for file in files:
				tbl_in_filename = os.path.join(path, file)
				skip = False
				for ignore_file in FILES_IGNORE_LIST:
					if tbl_in_filename.endswith(ignore_file):
						print("%s - skipped" % tbl_in_filename)
						skip = True
						break
				if skip:
					continue

				print(tbl_in_filename)

				try:
					tbl_in, tbl_out = self._test_convert_integrity(tbl_in_filename)
				except:
					self.verificationErrors.append(catch())
					#raise

				try:
					self.assertEqual(tbl_in, tbl_out, msg='%s - ERROR' % tbl_in_filename)
				except AssertionError, e:
					#print(str(e))
					self.verificationErrors.append(str(e))

		for e in self.verificationErrors:
			print(e)
					

if __name__ == '__main__':
    unittest.main()
