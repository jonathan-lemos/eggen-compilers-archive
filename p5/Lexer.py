import sys
import re

regexes = [
    ("ID", r"[a-zA-Z]+"),
    ("NUM", r"[0-9]+"),
    ("TYPE", r"int|void"),
    ("KEYWORD", r"if|else|while|return"),
    ("DELIM", r"[,()\[\]{};]"),
    ("ADDOP", r"[+\-]"),
    ("MULOP", r"[*/]"),
    ("=", "="),
    ("RELOP", r">=|<=|==|!=|>|<"),
]

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " [filename]")

comment = False
for line in open(sys.argv[1], "r"):
    if line.strip() == "":
        continue
    print("Input: '" + line.strip() + "'")
    line = line.strip()
    while line != "":
        if not comment:
            if line.startswith("//"):
                break
            if line.startswith("/*"):
                line = line[2:]
                comment = True
                continue
            longest = ("ERROR", line[0])
            for token, pattern in regexes:
                mat = re.match(pattern, line)
                if mat:
                    longest = longest if len(longest[1]) > mat.end() else (token, line[:mat.end()])
            print(longest[0] + ": " + longest[1])
            line = line[len(longest[1]):]
            line = line.strip()
        else:
            mat = re.match(r".*?\*/", line)
            if not mat:
                line = ""
            else:
                line = line[mat.end():].strip()
                comment = False
if comment:
    print("ERROR: Block comment not closed")
