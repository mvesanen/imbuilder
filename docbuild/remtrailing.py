import os
import sys
import re


columntrailingspaces = r"([^ ]+)[ ]{2,}\|"
singlecolumntrailingspace = r"([^ ]+)(\|)"
singlecolumnleadingspace = r"(\|)([^ ]+)"



def handletablerow(line):
    # discard "old version" of table formatting
    result=line
    result=re.sub(columntrailingspaces,"\\1|",result)
    for i in range(5): 
        result=re.sub(singlecolumntrailingspace,"\\1 \\2",result)
        result=re.sub(singlecolumnleadingspace,"\\1 \\2",result)
    return result

with open(sys.argv[2], "w", encoding="utf-8") as outfile:
    sys.stdout = outfile
    with open(sys.argv[1], encoding="utf-8") as infile:
        for line in infile:
            if line.count("|")>1:
                sys.stdout.write(handletablerow(line))
            else:
                sys.stdout.write(line)
            