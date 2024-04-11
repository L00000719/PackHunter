import os
import argparse
import sys
import json
import time
argparser = argparse.ArgumentParser(description="")
argparser.add_argument("--program", default="", type=str, help="The name of the program to install")

args = argparser.parse_args()


def install(programname):
    
    if programname in pc_only_one_package.keys():
        status = os.system(f"apt-get install -y --allow-downgrades {pc_only_one_package[programname]}")
    elif programname in pc_package.keys():
        for package in pc_package[programname]:
            status = os.system(f"apt-get install -y --allow-downgrades {package}")
            exit_code = os.WEXITSTATUS(status)
            if exit_code == 0:
                break

if __name__ == "__main__":
    
    script_path = os.path.abspath(sys.argv[0])
    script_directory = os.path.dirname(script_path)
    jsonpath = script_directory.rsplit("/", 1)[0] + "/json"
    jsonfile = open(f"{jsonpath}/pc_package_2.json", "r")
    pc_package = json.load(jsonfile)
    jsonfile2 = open(f"{jsonpath}/pc_only_one_package_2.json", "r")
    pc_only_one_package = json.load(jsonfile2)
    programname = args.program
    install(programname)

    #print(programname)
    