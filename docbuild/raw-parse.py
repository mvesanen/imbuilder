from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
from io import StringIO

import re
import sys
import os
import collections
import os.path
import platform
import glob
import shutil
import subprocess
from xsdtabulator import xsd_tabulate
from utils import get_doc_version

"""
  Moustache commands:
      {{ command [args]}}
  Currently:
  {{refsec section-id}}          - insert a reference to a (sub)section
  {{include FILE}}               - recursively include a file (or, if FILE=="annexes", all the annexes in letter order)
  {{schemafile FILE}}            - set a default schema file
  {{xtabulate TYPE SCHEMAFILE}}  - produce a table from a xml schema with leading statement.
  {{xtabulate2 TYPE SCHEMAFILE}} - same as xtabulate, without leading statement
  {{xtabulate3 TYPE SCHEMAFILE}} - same as xtabulate, but more chatty
  {{xtabulate4 TYPE SCHEMAFILE}} - same as xtabulate, but with xml code example
  {{xmlsnippet TYPE SCHEMAFILE}} - produce example code from xml schema
  {{figure IMAGE}}               - path to IMAGE, where IMAGE is a path relative to ./figures
  {{figst ID}}                   - apply default figure styles and set optional id (alphanum-_)+ for figure number referencing
  {{figref ID}}                  - insert a reference to a figure
"""

def demoustache_file(infile, ROOT):
    for l in infile:
        demoustache_line(l, ROOT)

def predemoustache_file(infile, ROOT):
    for l in infile:
        predemoustache_line(l, ROOT)

def demoustache_line(line, ROOT):
    start = line.find("{{")
    while start > -1:
        sys.stdout.write(line[0:start])
        end = line.index("}}", start)
        cmd = line[start+2:end].strip().split()
        moustache(ROOT, cmd[0], *cmd[1:])
        line = line[end+2:]
        start = line.find("{{")
    if line.endswith("\\\n"): line=line[:-2]
    sys.stdout.write(line)
    
def predemoustache_line(line, ROOT):
    start = line.find("{{")
    while start > -1:
        sys.stdout.write(line[0:start])
        end = line.index("}}", start)
        cmd = line[start+2:end].strip().split()
        premoustache(ROOT, cmd[0], *cmd[1:])
        line = line[end+2:]
        start = line.find("{{")
    if line.endswith("\\\n"): line=line[:-2]
    sys.stdout.write(line)

def include_file(ROOT, key):
    if key.endswith(".xml") or key.endswith(".xsd"):
        sys.stdout.write("```xml\n")
    with open(key, encoding="utf-8") as dfile: demoustache_file(dfile, ROOT)
    if key.endswith(".json") or key.endswith(".xml") or key.endswith(".xsd"): sys.stdout.write("\n```\n\n")

def preinclude_file(ROOT, key):
    if key.endswith(".xml") or key.endswith(".xsd"):
        sys.stdout.write("```xml\n")
    with open(key, encoding="utf-8") as dfile: predemoustache_file(dfile, ROOT)
    if key.endswith(".json") or key.endswith(".xml") or key.endswith(".xsd"): sys.stdout.write("\n```\n\n")

def premoustache(ROOT, command, *args):
    key=args[0] if 0 < len(args) else None
    if command == "include":
        preinclude_file(ROOT, key)
    
figure = "figures/"
diagrampath = "../diagrams/"
os.makedirs("./staging", exist_ok=True)
os.makedirs("./artefact", exist_ok=True)
#if(os.path.exists("./staging/figures")):
#    os.remove("./staging/figures")
#os.symlink("./figures/", "./staging/figures")

if(os.path.exists("./staging/figures")):
    shutil.rmtree("./staging/figures")
shutil.copytree("/git/figures", "./staging/figures")

default_schema_file=None
title_for_section = {}
def moustache(ROOT, command, *args):
    global default_schema_file
    key=args[0] if 0 < len(args) else None
    if command == "typeref":
        sys.stdout.write("""*%s*""" % (key))
    elif command == "refsec" or command == "refto":
        section = "subsection"
        s_level, s_title = title_for_section.get(key, (3, ""))
        if s_level <= 2: section = "section"
        sys.stdout.write("""%s **{@sec:%s}**""" % (section, key))
        if s_title:
            sys.stdout.write(""" *%s*""" % (s_title.replace('*','')))
    elif command == "include":
            include_file(ROOT, key)
    elif command == "draft-version":
        sys.stdout.write(get_doc_version())
    elif command == "date":
        sys.stdout.write(get_doc_version())
    elif command in ["xtabulate", "xtabulate2", "xtabulate3", "xtabulate4", "xtabulate5", "xtabulatef"]:
        if len(args) > 1: schema_file = args[1]
        elif default_schema_file is not None: schema_file = default_schema_file
        else: raise ValueError("no schema file given!")
        chatty = (command in ["xtabulate3"])
        leadingStatement = (command in ["xtabulate", "xtabulate3", "xtabulate4","xtabulatef"])
        codesnippet = (command in ["xtabulate4", "xtabulate5"])
        if(command =="xtabulate5"):
            xsd_tabulate(schema_file,key, chatty, leadingStatement,codesnippet,True,5)
        elif (command == "xtabulatef"):
            xsd_tabulate(schema_file,key, chatty, leadingStatement,codesnippet,True,0,True)
        else:
            xsd_tabulate(schema_file,key, chatty, leadingStatement,codesnippet)
    elif command == "xmlsnippet":
        if len(args) > 1: schema_file = args[1]
        elif default_schema_file is not None: schema_file = default_schema_file
        else: raise ValueError("no schema file given!")
        xsd_tabulate(schema_file,key, False, False, True, False)
    elif command == "xmlsnippet2":
        if len(args) > 1: schema_file = args[1]
        elif default_schema_file is not None: schema_file = default_schema_file
        else: raise ValueError("no schema file given!")
        xsd_tabulate(schema_file,key, False, False, True,True,5)
    elif command == "figure":
        sys.stdout.write(figure + key)
    elif command == "diagram":
        cmdres=subprocess.run(["java", "-jar", "/docbuild/plantuml.jar" ,"-o" , "/docbuild/staging/figures/", diagrampath+key, "-tpng"],capture_output=True)
        if (cmdres.returncode!=0):
            raise RuntimeError(cmdres.stdout+cmdres.stderr)
        basename = os.path.splitext(key)[0]
        sys.stdout.write(figure + basename+'.png')
    elif command == "figst":
        if len(args) > 0:
            figure_id = args[0]
            sys.stdout.write('{#fig:%s width="90%%"}' % (figure_id))
        else:
            sys.stdout.write('{width="90%"}')
    elif command == "figref":
        figure_id = args[0]
        sys.stdout.write('Figure {@fig:%s}' %(figure_id))
    elif command == "schemafile":
        default_schema_file = key
    else:
        raise ValueError("what to do with command %s?" % (command))

cwd = os.path.dirname(os.path.abspath(__file__))
def demoustache_to_text(line, ROOT=cwd):
    output, oldout = StringIO(), sys.stdout
    sys.stdout = output
    try:
        demoustache_line(line, ROOT)
        return output.getvalue()
    finally:
        output.close()
        sys.stdout = oldout

def extract_section_name(line, prune = lambda x:x.strip()):
    line = line.strip()
    match = section_pattern.fullmatch(line)
    if match:
        key, val = match[3], [len(match[1]), demoustache_to_text(prune(match[2]))]
        title_for_section[key] = val

if __name__ == "__main__":
    
    #preprocess the file
    with open("./staging/tmp_" + os.path.basename(sys.argv[1]), "w", encoding="utf-8") as outfile:
        sys.stdout = outfile
        with open(sys.argv[1], encoding="utf-8") as infile:
            dirname = os.path.dirname(sys.argv[1])
            os.chdir(dirname)
            predemoustache_file(infile, cwd)
            os.chdir(cwd)
    sys.stdout = sys.__stdout__
    
    # code to range over our files and extract the section names for the benefit of the refsec macro:
    section_pattern = re.compile("(#+) *(.+) *{#sec:([^}]+)}")
    section_pruner = lambda s:s.replace("*","").strip()
    #for from_name, to_name in interp.items():
    with open("./staging/tmp_" + os.path.basename(sys.argv[1]), encoding="utf-8") as infile:
        for line in infile:
            extract_section_name(line, section_pruner)
    
    #for from_name, to_name in interp.items():
    with open("./staging/" + os.path.basename(sys.argv[1]), "w", encoding="utf-8") as outfile:
        sys.stdout = outfile
        with open(sys.argv[1], encoding="utf-8") as infile:
            dirname = os.path.dirname(sys.argv[1])
            os.chdir(dirname)
            demoustache_file(infile, cwd)
            os.chdir(cwd)
