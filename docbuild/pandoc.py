import os
import platform
import subprocess
import sys

def make_file(suffix, *args):
    sys.stderr.write("generating %s file ...\n" % (suffix))
    args = ['pandoc', '--output=./artefact/Inframodel_DRAFT.' + suffix] + list(args)
    # sys.stderr.write(" \\\n    ".join(args) + "\n")
    subprocess.call(args)

respath = '--resource-path=' + os.path.dirname(os.path.abspath(sys.argv[1]))
# respath = '--resource-path=staging'
print(respath)
# print(os.listdir(os.path.dirname(os.path.abspath(sys.argv[1]))+'/figures'))
common_args = ['--from=markdown+escaped_line_breaks+hard_line_breaks', '--filter=pandoc-xnos', '--number-sections', '--table-of-contents', respath]

latex_args = ['--variable=block-headings']
for latex_file in ["default", "disable_float", "fignos"]:
    latex_args.append("--include-in-header=./%s.latex" % (latex_file))

latex_args.append("--template=/git/templates/pdf-template.latex")

make_file("pdf" , *common_args, *latex_args, sys.argv[1])

