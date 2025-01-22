import os
import sys
import re
import datetime
from utils import get_doc_version_oneline

latexparam=0
gotbacklash=False
yamlheader=False
invalidchars=["$","%","&","~","_","^","\\","{","}","#"] 
latexfunc="\\\\(.[^<>*{]+){([^}]+)}"
tablevalue="(?:([^\\|]+))"
remadd="(\\|\\\\removed{[^\\\\\\|]+})\\|(\\\\added{[^\\\\\\|]+})"
trailingspaces = r"(\\.+{)([^ }|]+)[ ]+([|}])"
trailingspaces2 = r"([^ ]+)[ ]{2,}"


def handletablerow(line):
    # discard table formatting
    result=line
    if line.find("{:-")!=-1:
        for match in re.finditer(latexfunc,line):
            if match[2].startswith(":-"):
                if (match[1]=="removed"): #old one has to disappear completety
                    result = result.replace(match[0],"")
                else:
                    result = result.replace(match[0],match[2])
        return result
    # discard "old version" of column titles
    #if line.find("|**")!=-1:
    #    for match in re.finditer(latexfunc,line):
    #        if match[1]=="removed" and match[2].startswith("|**"):
    #            result = result.replace(match[0]+"\n","")
    #            result = result.replace(match[0],"")
    #    return result
    # move the changes inside of the columns delimited py pipe
    for match in re.finditer(latexfunc,result):
        #sys.stderr.write("Found match:%s::%s{%s}\n" % (result[result.find(match[0]):],match[1],match[2]))
        tmp=re.sub(tablevalue,"\\\\"+match[1]+"{"+"\\1"+"}",match[2])
        #sys.stderr.write("newsub:%s\n" % (tmp))
        result = result.replace(match[0],tmp) 
        #sys.stderr.write("result:%s\n" % (result))
    #remove trailing spaces
    result=re.sub(trailingspaces,"\\1\\2\\3",result)
    result=re.sub(trailingspaces2,"\\1",result)
    #fix removed-added sequences
    #for match in re.finditer(trailingspaces, result):
    #    sys.stderr.write(match[1]+match[2]+match[3]+"\n")
    result=re.sub(remadd,"\\1\\2",result)
    
    #sys.stderr.write("result:%s\n" % (result))
    return result

with open(sys.argv[2], "w", encoding="utf-8") as outfile:
    sys.stdout = outfile
    fullline=""
    add=False
    with open(sys.argv[1], encoding="utf-8") as infile:
        for line in infile:
            if line.startswith("---"):
                if yamlheader==False:
                    yamlheader=True
                else:
                    yamlheader=False
                    sys.stdout.write("---\n")
                    sys.stdout.write("title: \"Document comparison\"\n")
                    sys.stdout.write("subtitle: \"Between versions:\n" + get_doc_version_oneline(sys.argv[3]) + "\nand\n" + get_doc_version_oneline(sys.argv[4]) + "\"\n")
                    sys.stdout.write("geometry: \"left=2cm,right=2cm,top=2cm,bottom=2cm\"\n")
                    sys.stdout.write("xnos-warning-level: 1\n")
                    sys.stdout.write("xnos-number-by-section: true\n")
                    sys.stdout.write("titlepage: true\n")
                    sys.stdout.write("---\n")
                    continue
            if yamlheader==True:
                continue
            emptycommand = re.match("^\\\\(.+){}",line)
            if emptycommand:
                if(emptycommand[1]=="added"):
                    sys.stdout.write("\n");
                elif(emptycommand[1]=="removed"):
                    sys.stdout.write("\n");
                continue
            gotbacklash=False
            if(line.count("|")==1): #looks like an table...wonder if it continues
                #sys.stderr.write("needsmore: %d,%s\n" % (line.count("|"),line));
                fullline=line[:-1]
                add=True
                continue
            else:
                if(add):
                    add=False
                    fullline=fullline+line
                    #sys.stderr.write("extend: %d,%s\n" % (fullline.count("|"),fullline));
                    #sys.stderr.write(fullline+"\n");
                else:
                    fullline=line
            if fullline.count("|")>1:
                fullline=handletablerow(fullline)
            for char in fullline:
                if char == "\\":
                    gotbacklash=True
                if char == " " or char == "\n":
                    gotbacklash=False
                if char == "}":
                    if latexparam>0 :
                        latexparam=latexparam-1
                if latexparam > 0:
                    if char in invalidchars:
                        if (char=="<"):
                            sys.stdout.write("\\textless")
                        elif (char==">"):
                            sys.stdout.write("\\textgreater")
                        elif (char=="\\"):
                            sys.stdout.write("\\textbackslash ")
                        else:
                            sys.stdout.write("\\")
                            sys.stdout.write(char)
                    else:
                        sys.stdout.write(char)
                else:
                    sys.stdout.write(char)
                if char == "{" and gotbacklash:
                    latexparam=latexparam+1
