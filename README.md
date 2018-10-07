# pyembroidery-CLI


Requires pyembroidery

`pip install pyembroidery`

pyemb.py - Full pyembroidery CLI

Command Flags
---
    * -i [<input>]*, matches wildcards
    * -o [<output>]*, matches wildcard, formatted
    * -f [<string>], print string, formatted
    * -c conditional, filters embroidery patterns, formatted
    * -s <scale> [<scale_y> [<x> <y>]], scale pattern
    * -r <theta> [<x> <y>], rotate pattern
    * -t <x> <y>, translate
    * -e [<setting> <value>]*, set encoder settings
    * -q, quiet mode
    * -v, verbose mode
    * -h, display this message

String Formatting:
---
    * %f, filename
    * %F, filename without directory
    * %e, extension
    * %d, directory
    * %n, name of file, without extension
    * %S, total commands in stitches
    * %s, STITCH command count
    * %j, JUMP command count
    * %c, COLOR_CHANGE & NEEDLE_SET count
    * %t, TRIM command count
    * %l, internal label, if it exists
    * %w, width
    * %h, height
    * %x, min x
    * %y, min y
    * %X, max x
    * %Y, max y

* So for example to do the same thing as mass_convert we execute:
`pyemb.py -i convert\* -o results\*`

* To do the same as pyembroidery-convert
`pyemb.py -i <source-file> -o <destination-file>`

* To do the same as pyembroidery-exporter
`pyemb.py -i <source-file> -o %f.u01 %f.exp %f.dst %f.jef %f.pes %f.vp3`
or
`pyemb.py -i <source-file> -o %f.*`

* To create an image for every readable embroidery in a directory:
`pyemb.py -i * -o %f.png`

* To create an image for only the ones with fewer than 15000 stitches.
`pyemb.py -i * -c "%S < 15000" -o %f.png`

* To flip `my_embroidery.exp` horizontally
`pyemb.py -i my_embroidery.exp -s -1 1 -o flipped.exp`

---
* mass_convert.py	CLI - Converts every file in directory `./convert` to `./results` for every acceptable filetype and into every acceptable result.
* pyembroidery-convert.py	CLI - (Source File) (Destination File) convert an embroidery file from one type to another. By default makes .csv files.
* pyembroidery-exporter.py  CLI - (Source File) - Converts an embroidery file from some type to `.u01, .exp, .dst, .jef, .pes, .vp3`
* stitch_entry_pmv.py CLI - Text interface - Allows creating stitch files from a purely text base interface expecting values between [0,14] and [-30,30]

The stitch_entry_pmv script works but the MaKe-stitch program is a fully realized GUI.
