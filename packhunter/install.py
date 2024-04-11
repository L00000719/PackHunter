import os
import argparse
import sys
import json
import time
argparser = argparse.ArgumentParser(description="")
argparser.add_argument("--program", default="", type=str, help="The name of the program to install")

args = argparser.parse_args()


def install(programname):
    
    if programname in programs.keys():
        for package in programs[programname]:
            status = os.system(f"apt-get install -y --allow-downgrades {package}")
            exit_code = os.WEXITSTATUS(status)
            if exit_code == 0:
                break

if __name__ == "__main__":
    
    script_path = os.path.abspath(sys.argv[0])
    script_directory = os.path.dirname(script_path)
    jsonpath = script_directory.rsplit("/", 1)[0] + "/json"
    jsonfile = open(f"{jsonpath}/program_package.json", "r")
    programs = json.load(jsonfile)

    programname = args.program
    install(programname)

    #print(programname)
    