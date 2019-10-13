<h1>The Legend of Heroes: Trails of Cold Steel localization scripts</h1>

<h2><b>Usage: trails.py command args</b></h2>

<h2><b>Commands: </b></h2>
<pre>
  <b>dat_to_xml</b>   src.dat [dest.xml]                                      - convert *.dat file to *.xml.
  <b>convert</b>      src.{tbl,dat,xml} dest.{tbl,dat,xml} [encoding]         - convert *.{tbl,dat,xml} file
                                                                             to dest.{tbl,dat,xml}.
  <b>xml_to_tbl</b>   src.xml [dest.tbl]                                      - convert *.xml file to *.tbl.
  <b>tbl_to_xml</b>   src.tbl [dest.xml] [encoding]                           - convert *.tbl file to *.xml.
  <b>xml_to_dat</b>   src.xml [dest.dat] [encoding]                           - convert *.xml file to *.dat.
  <b>dump_data</b>    src.tbl dest.txt                                        - extract data entries from src.tbl
                                                                                          and write to dest.txt.
  <b>merge</b>        src1.{tbl,xml} src2.{tbl,xml} dest.{tbl,xml} [encoding] - use a text entries of src1 and a data
                                                               entries of src2 and write result to destination file.
  <b>dump_text</b>    src.tbl dest.txt                                        - extract text entries from src.tbl and 
                                                                                                write to dest.txt.
  <b>wrap</b>         src.{tbl,dat,xml} dest.{tbl,dat,xml} [encoding]         - wrap text entries in a source file
                                                                                  so that they fit on the display.
  <b>encode</b>       src1.{tbl,xml} dest.{tbl,xml} encoding                  - change encoding of a source file.

  <b>bulk_copy</b>    source_dir dest_dir                                     - bulk copy *.tbl and *.dat files from
                                                                                               source_dir to dest_dir.
  <b>bulk_convert</b> source_dir dest_dir                                     - bulk convert files in source_dir and
                                                                                                save them in dest_dir.

</pre>
