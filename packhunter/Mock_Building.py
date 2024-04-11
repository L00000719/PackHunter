import os
import argparse
import sys
import shutil
import json
import threading
import subprocess
import time
import multiprocessing
from lxml import etree
from pylibsrcml import srcml
import re


ns = {'src': 'http://www.srcML.org/srcML/src',
      'cpp': 'http://www.srcML.org/srcML/cpp'}


argparser = argparse.ArgumentParser(description="")
argparser.add_argument("--path", default="", type=str, help="Project path")
argparser.add_argument("--mode", default=1, type=int, help="Only log file analysis")
argparser.add_argument("--function", default=1, type=int, help="Function-level analysis")
argparser.add_argument("--Astudy", default=1, type=int, help="ablation study")
argparser.add_argument("--new", default=1, type=int, help="new")
args = argparser.parse_args()


def execute_cmd(cmd, output_file):
    try:
        # 使用subprocess运行命令
        with open(output_file, "w") as file:
            subprocess.run(cmd, check=True, shell=True, stdout=file, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

def select_package_by_file_coverage(h_deps, lib_deps):
    package_count = {}
    for h_file in h_deps: 
        for package in h_deps[h_file]:
            if package not in package_count:
                package_count[package] = {}
                package_count[package]["count"] = 0
                package_count[package]["files"] = []
            package_count[package]["count"] += 1
            package_count[package]["files"].append(h_file)

    for lib_file in lib_deps:
        for package in lib_deps[lib_file]:
            if package not in package_count:
                package_count[package] = {}
                package_count[package]["count"] = 0
                package_count[package]["files"] = []
            package_count[package]["count"] += 1
            package_count[package]["files"].append(lib_file)


    
    selected_packages = repeatedly_update_packages(package_count)
    return selected_packages

def get_all_deps(package, seen=None):
        if seen is None:
            seen = set()
        if package in seen:
            return set()
        seen.add(package)
        deps = set(package_deps.get(package, []))
        for dep in list(deps):
            deps.update(get_all_deps(dep, seen))
        return deps

def determine_packages(h_deps, package_h_unique_func, h_src, src_func, package_deps):
    confirmed_packages = set()  # 用于存储顶层包
    pending_headers = set(h_deps.keys())  # 存储尚未确定的头文件
    all_all_deps = set()
    # 递归地获取一个包的所有依赖包

    # 检查并移除已确定的头文件
    def check_and_remove_confirmed_headers(package):
        all_deps = get_all_deps(package)
        #all_all_deps.add(package)
        all_all_deps.update(all_deps)
        for h in list(pending_headers):
            if package in h_deps[h] or any(dep in h_deps[h] for dep in all_deps):
                pending_headers.remove(h)

    # 遍历每个头文件
    for h in h_deps.keys():
        if h not in pending_headers:
            continue

    
        possible_packages = set(h_deps[h])
        src_files = h_src.get(h, [])
        packages_with_func = {}
        # 遍历每个源文件
        for src in src_files:
                for func in src_func.get(src, []):
                    for package in possible_packages:
                        if func in package_h_unique_func.get(package, {}).get(h, []):                  
                            if package not in packages_with_func :
                                packages_with_func[package] = 0
                            packages_with_func[package] += 1
                            print(h)
                            print(func)
                            print(src)
                            print(package)
                         
                    
        if len(packages_with_func) != 0:

            """ print(h)
            print(packages_with_func.keys()) """
            for package in packages_with_func :
                #print(packages_with_func[package])
                confirmed_packages.add(package)
                check_and_remove_confirmed_headers(package)




    reduced_h_deps = {h: h_deps[h] for h in pending_headers}

    return confirmed_packages, all_all_deps, reduced_h_deps


def find_functions(tree):
    functions = []
    calls = tree.xpath("//src:call/src:name", namespaces=ns)
    for call in calls:
        # 获取当前 call 元素下的所有子元素
        if call.text:
            functions.append(call.text)
        else :
            names = call.xpath(".//src:name|.//src:operator", namespaces=ns)
            callname = ""
            for name in names:
                if name.text:
                    #callname = callname + name.text
                    callname = name.text
            functions.append(callname)

    return functions

def select_best_package(same_count_packages):
    versioned_packages = []
    for package in same_count_packages:
        package_name, package_info = package
        # 检查包名结构是否符合 "package-version" 格式
        match = re.search(r'^([a-zA-Z0-9]+)-([0-9]+)-dev$', package_name)
        if match:
            version = int(match.group(2))
            versioned_packages.append((version, package_name, package_info))

    # 如果找到了符合条件的包
    if versioned_packages:
        # 按版本号降序排序，返回版本号最高的包
        versioned_packages.sort(key=lambda x: -x[0])
        return (versioned_packages[0][1], versioned_packages[0][2])

    # 如果没有符合条件的包，选择名字最短的包
    return min(same_count_packages, key=lambda x: len(x[0]))


def get_and_update_highest_count(package_count):

    # 按count降序排列，如果count相同，则按照包名升序排列
    sorted_packages = sorted(package_count.items(), key=lambda x: (-x[1]['count']))
    print(sorted_packages)
    # 获取count最高的package
    highest_package = sorted_packages[0]

    # 如果顶端有多个count一样的package
    same_count_packages = [pkg for pkg in sorted_packages if pkg[1]['count'] == highest_package[1]['count']]

    if len(same_count_packages) > 1:
        # 检查files是否相同
        """ if all(same_count_packages[0][1]['files'] == pkg[1]['files'] for pkg in same_count_packages[1:]):
            # 如果files相同，比较版本号

            highest_package = max(same_count_packages, key=lambda x: (len(x[0]), x[0]))

        else:
            highest_package = same_count_packages[0]  # 直接取第一个 """
        highest_package = select_best_package(same_count_packages)
    # 更新其他package的files和count
    highest_package_files = set(highest_package[1]['files'])

    for pkg_name, pkg_info in package_count.items():
        # 删除与highest_package相同的files
        pkg_info['files'] = [file for file in pkg_info['files'] if file not in highest_package_files]
        # 更新count
        pkg_info['count'] = len(pkg_info['files'])

    return highest_package[0]

def remove_zero_count_packages(package_count):

    packages_to_remove = [pkg for pkg, info in package_count.items() if info['count'] == 0]
    for pkg in packages_to_remove:
        del package_count[pkg]

def repeatedly_update_packages(package_count):
    selected_packages = []
    while any(info['count'] > 0 for info in package_count.values()):

        highest_package = get_and_update_highest_count(package_count)
        selected_packages.append(highest_package)
        remove_zero_count_packages(package_count)
    return selected_packages

def commands_separated(dir):
    with open(dir, 'r') as file:
        lines = file.readlines()

    commands = []
    current_command = ''
    for line in lines:
        line = line.strip()
        if line.endswith('\\'):
            current_command += line[:-1].strip()
        else:
            current_command += line
            commands.extend(current_command.split('&&'))
            current_command = ''

    commands = [cmd.strip() for cmd in commands if cmd.strip()]
    return commands

def command_processor(commands):

    if not os.path.exists(f"{directory}/command_log"):
        os.mkdir(f"{directory}/command_log")
    processes = []
    count = 0
    for command in commands:
        
        count += 1
        print(count)
        
        cmd = f"{script_directory}/mytrace {count} {command}"
        print(cmd)
        #execute_cmd(cmd)
        output_file = f"{directory}/command_log/process_{count}"
        p = multiprocessing.Process(target=execute_cmd, args=(cmd, output_file))
        processes.append(p)
        p.start()

    for p in processes:
        p.join(timeout=1)
        if p.is_alive():
            p.terminate()


def remove_log_files(directory):
    for filename in os.listdir(f"{directory}/log_files"):
        if filename.endswith("log"):  # 检查文件名是否以.log结尾
            file_path = os.path.join(f"{directory}/log_files", filename)
            os.remove(file_path)  # 删除文件

def remove_virtual_files(directory):
    for item in os.listdir(f"{directory}/log_files"):
        if "missing_files" in item:
            full_path = os.path.join(f"{directory}/log_files", item)
            missing_files = open(full_path, "r")
            for line in missing_files:
                virtual_file_path = line[:-1].split(" ")[-1]
                if os.path.exists(virtual_file_path):
                    if os.path.getsize(virtual_file_path) == 0:
                        os.remove(virtual_file_path)


def list_executable_files(directory):
    executable_files = []
    executable_files = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if os.access(filepath, os.X_OK):
                executable_files.add(file)
    
    return executable_files


def list_files_in_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            #file_list.append(os.path.join(root, file))
            if "prune_file" not in root:
                file_list.append(file)
    return file_list

def filter_libraries_and_headers(directory):
    
    file_list = list_files_in_directory(directory)
    extensions = ["so", "a"]
    h_extensions = ["hpp", "h", "hxx"]
    all_files = set()

    for file in file_list:
        # 获取文件的扩展名
        file_extension = file.rsplit(".", 1)[-1]
        if file_extension in h_extensions:
            all_files.add(file)


    return all_files

def filter_libraries(directory):
    
    file_list = list_files_in_directory(directory)
    extensions = ["so", "a"]

    all_files = set()

    for file in file_list:
        # 获取文件的扩展名
        file_extension = file.rsplit(".", 1)[-1]
        if file_extension in extensions:
            all_files.add(file)




    return all_files

def filter_headers(directory):
    
    file_list = list_files_in_directory(directory)

    h_extensions = ["hpp", "h", "hxx"]
    all_files = set()

    for file in file_list:
        # 获取文件的扩展名
        file_extension = file.rsplit(".", 1)[-1]
        if file_extension in h_extensions:
            all_files.add(file)


    return all_files

# 获取系统路径下的库文件和头文件
def get_existing_file(directory):
    all_files = set()
    executable_files = set()
    system_library_directorys = ["/usr/lib", "/lib", "/lib64"]
    #system_include_directorys = ["/usr/include", "/usr/local/include"]
    executable_files_directorys = ['/usr/bin',"/usr/local/bin"]
    system_include_directorys = ["/usr/include/linux", "/usr/lib/gcc"]
    """ for system_library_directory in system_library_directorys:
        all_files.update(filter_libraries(system_library_directory)) """

    for system_include_directory in system_include_directorys:
        all_files.update(filter_headers(system_include_directory))
    # 获取指定路径下的库文件和头文件

    if "/build" in directory :
        directory2 = directory.rsplit("/", 1)[0]
    else :
        directory2 = directory
    
    print(directory2)
    all_files.update(filter_libraries_and_headers(directory2))

    for executable_files_directory in executable_files_directorys:
        executable_files.update(list_executable_files(executable_files_directory))

    # 定义文件路径用于输出结果
    output_file = f"{directory}/library_and_header_files.txt"
    output_file2 = f"{directory}/executable_files.txt"

    # 打开文件以写入结果
    with open(output_file, "w") as file:
        for file_name in all_files:
            file.write(file_name + "\n")

    with open(output_file2, "w") as file:
        for file_name in executable_files:
            file.write(file_name + "\n")

    return all_files

def identify_build_tool(directory):
    """ for item in os.listdir(directory):
        if item.lower() == ("configure"):
            return "auto" """

    for item in os.listdir(directory):
        if item.lower() == ("cmakelists.txt"):
            return "cmake"
    
    for item in os.listdir(directory):
        if item.lower() == ("makefile"):
            return "make"

   
    return 0

def process_auto():
    if mode:
        if not os.path.exists(f"{directory}/prune_file"):
            os.mkdir(f"{directory}/prune_file")
        else :
            shutil.rmtree(f"{directory}/prune_file")
            os.mkdir(f"{directory}/prune_file")

        if (os.system(f"{script_directory}/mytrace auto ./configure")) != 0:
            remove_virtual_files(directory)
        
        #os.system(f"{script_directory}/mytrace make make -n > make_n")
        os.system("make -n > make_n")
        make_n_dir = f"{directory}/make_n"

        commands = commands_separated(make_n_dir)
        command_processor(commands)

    mock_build_end_time = time.time()

    mock_build_time = mock_build_end_time - mock_build_start_time
    f.write(f"mock build: {mock_build_time}")
    f.write("\n")
    analysis_start_time = time.time()
    get_dep_make()

    analysis_end_time = time.time()
    analysis_time = analysis_end_time - analysis_start_time
    f.write(f"analysis time: {analysis_time}")
    f.write("\n")
def process_cmake():
    if mode:
        os.environ['cmake_make_n'] = "/build"

        if not os.path.exists(f"{directory}/prune_file"):
            os.mkdir(f"{directory}/prune_file")
        else :
            shutil.rmtree(f"{directory}/prune_file")
            os.mkdir(f"{directory}/prune_file")
            
        if not os.path.exists(f"{directory}/find_cmake_file"):
            os.mkdir(f"{directory}/find_cmake_file")
        else :
            shutil.rmtree(f"{directory}/find_cmake_file")
            os.mkdir(f"{directory}/find_cmake_file")


        if not os.path.exists(f"{directory}/build"):
            os.mkdir(f"{directory}/build")
        else :
            shutil.rmtree(f"{directory}/build")
            os.mkdir(f"{directory}/build")

        os.chdir(f"{directory}/build")
        if (os.system(f"{script_directory}/mytrace cmake cmake -DCMAKE_PREFIX_PATH=/home/hzl/Mock_Building/mock_libs ..")) != 0:
            remove_virtual_files(directory)
        
        os.system(f"{script_directory}/mytrace make make -n -B > ../make_n")
        make_n_dir = f"{directory}/make_n"
        del os.environ['cmake_make_n']


        commands = commands_separated(make_n_dir)
        command_processor(commands)

    mock_build_end_time = time.time()

    mock_build_time = mock_build_end_time - mock_build_start_time
    f.write(f"mock build: {mock_build_time}")
    f.write("\n")
    analysis_start_time = time.time()
    get_dep_make()

    analysis_end_time = time.time()
    analysis_time = analysis_end_time - analysis_start_time
    f.write(f"analysis time: {analysis_time}")
    f.write("\n")

def process_make():
    if not os.path.exists(f"{directory}/prune_file"):
        os.mkdir(f"{directory}/prune_file")
    else :
        shutil.rmtree(f"{directory}/prune_file")
        os.mkdir(f"{directory}/prune_file")

    os.system(f"{script_directory}/mytrace make make -n -B> make_n") #-B
    make_n_dir = f"{directory}/make_n"

    commands = commands_separated(make_n_dir)
    command_processor(commands)

    mock_build_end_time = time.time()

    mock_build_time = mock_build_end_time - mock_build_start_time
    f.write(f"mock build: {mock_build_time}")
    f.write("\n")
    analysis_start_time = time.time()
    get_dep_make()

    analysis_end_time = time.time()
    analysis_time = analysis_end_time - analysis_start_time
    f.write(f"analysis time: {analysis_time}")
    f.write("\n")

def get_dep_make():
    analysis_result = {}
    

    notfind = {}
    notfind["pc"] = []
    notfind["lib"] = []
    notfind["h"] = []

    exes = set()
    src_func = {}
    lib_src = {}
    h_src = {}
    create_files = set()
    lib_obj = {}
    obj_src = {}

    dep = set()
    h_files = set()
    pc_files = set()
    lib_files = set()
    all_dependencies = set()
    h_dep = {}
    pc_dep = {}
    lib_dep = {}
    dep_package_files = {}
    exe_dep = set()

    
    for item in os.listdir(f"{directory}/log_files"):
        if "files.log" in item and "missing" not in item:
            if "cmake" not in item and "auto" not in item:
                full_path = os.path.join(f"{directory}/log_files", item)
                files_log = open(full_path, "r")
                for line in files_log:
                    file = line[:-1].split(" ")[0].rsplit("/", 1)[-1]
                    if file.endswith(".so"):
                        lib_files.add(file)
                    elif file.endswith(".pc"):
                        pc_files.add(file)
                    elif file.endswith(".h") or file.endswith(".hpp") or file.endswith(".hxx"):
                        h_files.add(file)

        elif ".tlog" in item:
            full_path = os.path.join(f"{directory}/log_files", item)
            open_files = open(full_path, "r")
            srcs = []
            hs = []
            libs = []
            objs = []

            for line in open_files:
                if "/tmp" in line :
                    continue
                file = line[:-1].split(" ")[0].rsplit("/", 1)[-1]
                create = line[:-1].split(" ")[-1]
                if file.endswith(".h") or file.endswith(".hpp") or file.endswith(".hxx"):
                    h_files.add(file)
                    hs.append(file)
                elif file.endswith(".o") and directory in line:
                    objs.append(file)
                elif file.endswith(".c") or file.endswith(".cpp") or file.endswith(".cxx") or file.endswith(".C") or file.endswith(".cc"):
                    src_name = file.rsplit(".", 1)[0]
                    srcname = line[:-1].split(" ")[0]
                    srcs.append(src_name)
 
                    if src_name not in src_func:
                        src_func[src_name] = set()
                    xml = srcname.rsplit(".", 1)[0] + ".xml"
                    try:
                        if not os.path.exists(xml):
                            srcml.srcml(srcname, xml)
                        tree = etree.parse(xml)
                        src_func[src_name].update(find_functions(tree))
                    except:
                        print(srcname)
                elif file.endswith(".so"):
                    lib_files.add(file)
                    libs.append(file)
                elif file.endswith(".a"):
                    file = file.rsplit(".", 1)[0] + ".so"
                    lib_files.add(file)
                    libs.append(file)
                if create == "create":
                    create_files.add(file)
                    project_files.add(file)

            if srcs and hs :
                for file in hs :
                    if file not in h_src:
                        h_src[file] = set()
                    h_src[file].update(set(srcs))

            if objs and srcs :
                obj_src[objs[0]] = srcs[0]

            if libs and objs :
                for lib in libs :
                    for obj in objs :
                        if lib not in lib_obj:
                            lib_obj[lib] = set()
                        lib_obj[lib].add(obj)

        elif "execve.log" in item:
            full_path = os.path.join(f"{directory}/log_files", item)
            files_log = open(full_path, "r")
            for line in files_log:
                file = line[:-1].split(" ")[0]
                if file.startswith("/usr/bin") or file.startswith("/usr/local/bin"):
                    exes.add(file.rsplit("/", 1)[-1])


    for lib in lib_obj:
        lib_src[lib] = set()
        for obj in lib_obj[lib]:
            if obj in obj_src:
                lib_src[lib].add(obj_src[obj])


    #print(src_func)
    #print(lib_src)
    #print(h_src)
    #print(create_files)
    #print(lib_obj)
    #print(obj_src)


    project_files.update(set(package_files["libc6-dev"]["lib"]))
    project_files.update(set(package_files["libc6-dev"]["h"]))
    project_files.update(set(package_files["libgcc-12-dev"]["lib"]))
    project_files.update(set(package_files["libgcc-12-dev"]["h"]))
    project_files.update(set(package_files["linux-libc-dev"]["lib"]))
    project_files.update(set(package_files["linux-libc-dev"]["h"]))
    project_files.update(set(package_files["libstdc++-11-dev"]["h"]))
    project_files.update(set(package_files["libstdc++-11-dev"]["lib"]))
    project_files.update(set(package_files["libtbb-dev"]["h"]))
    project_files.update(set(package_files["libtbb-dev"]["lib"]))
    h_files.difference_update(project_files)
    lib_files.difference_update(project_files)

    h_files = list(h_files)
    pc_files = list(pc_files)
    lib_files = list(lib_files)
    exes = list(exes)


    """ print(h_files)
    print(pc_files)
    print(lib_files) """

    all_files = set()
    p_0 = set()
    analysis_result["files0_h"] = h_files
    analysis_result["files0_l"] = lib_files
    analysis_result["files0_pc"] = pc_files
    analysis_result["exe"] = exes
    



    for exe in exes:
        if exe in program_package:
            exe_dep.add(next(iter(program_package[exe])))

    analysis_result["exe_dep"] = list(exe_dep)

    for h_file in h_files:
        all_files.add(h_file)
        if h_file in h_only_one_package:
            print(h_file)
            print(h_only_one_package[h_file])
            dep.add(h_only_one_package[h_file])
        elif h_file in h_package:
            h_dep[h_file] = h_package[h_file]
        else :
            notfind["h"].append(h_file)

    for lib_file in lib_files:
        all_files.add(lib_file)
        if lib_file in lib_only_one_package:
            print(lib_file)
            print(lib_only_one_package[lib_file])
            dep.add(lib_only_one_package[lib_file])
        elif lib_file in lib_package:
            lib_dep[lib_file] = lib_package[lib_file]
        else :
            notfind["lib"].append(lib_file)

    for pc_file in pc_files:
        all_files.add(pc_file)
        if pc_file in pc_only_one_package:
            #print(pc_file)
            #print(pc_only_one_package[pc_file])
            dep.add(pc_only_one_package[pc_file])
        elif pc_file in pc_package:
            pc_dep[pc_file] = pc_package[pc_file]
        else :
            notfind["pc"].append(pc_file)

    f.write(f"all_file : {str(len(all_files))}")


    for package in dep:
        p_0.add(package)

    print(dep)
    actual_dependencies = dep.copy()
    
    all_dependencies = set()

    for package in dep:
        all_dependencies.update(get_all_deps(package))


    for package in all_dependencies:
        if package in actual_dependencies:
            actual_dependencies.remove(package)

    all_dependencies.update(actual_dependencies)
    all_dependencies.update(exe_dep)
    all_dependencies = list(all_dependencies)



    h_deps = h_dep.copy()
    pc_deps = pc_dep.copy()
    lib_deps = lib_dep.copy()

    select_package_by_file_coverage(h_deps,lib_deps)

    if new:
        for h_file in h_dep:
            for package in h_dep[h_file]:
                p_0.add(package)
                if package in all_dependencies:
                    del h_deps[h_file]
                    break

        for lib_file in lib_dep:
            for package in lib_dep[lib_file]:
                p_0.add(package)
                if package in all_dependencies:
                    del lib_deps[lib_file]
                    break

        for pc_file in pc_dep:
            for package in pc_dep[pc_file]:
                p_0.add(package)
                if package in all_dependencies:
                    del pc_deps[pc_file]
                    break
    
    f.write("\n")
    f.write(f"p_0 : {str(len(p_0))}")


    p_1 = set()

    all_files1 = set()

    for h_file in h_deps:
        all_files1.add(h_file)
        for package in h_deps[h_file]:
            p_1.add(package)

    for lib_file in lib_deps:
        all_files1.add(lib_file)
        for package in lib_deps[lib_file]:
            p_1.add(package)


    


    

    

    f.write("\n")
    f.write(f"all_file1 : {str(len(all_files1))}")

    f.write("\n")
    f.write(f"p_1 : {str(len(p_1))}")




    analysis_result["stage1"] = list(actual_dependencies)
    analysis_result["files1_h"] = h_deps
    analysis_result["files1_l"] = lib_deps

    if function:

        #package_l_unique_func
        #package_h_unique_func
        #src_func
        #h_src
        #package_deps
        
        #print(lib_deps.keys())

        h_confirmed_packages, h_all_all_deps, reduced_h_deps = determine_packages(h_deps, package_h_unique_func, h_src, src_func, package_deps)
        l_confirmed_packages, l_all_all_deps, reduced_l_deps = determine_packages(lib_deps, package_l_unique_func, lib_src, src_func, package_deps)


        
        print(h_confirmed_packages)
        print(l_confirmed_packages)
        analysis_result["stage2"] = list(h_confirmed_packages)
        analysis_result["stage3"] = list(l_confirmed_packages)





        actual_dependencies.update(h_confirmed_packages)
        actual_dependencies.update(l_confirmed_packages)


        if h_all_all_deps or l_all_all_deps:
            h_all_all_deps.update(l_all_all_deps)
            for package in list(h_all_all_deps):
                if package in actual_dependencies:
                    actual_dependencies.remove(package)



        all_dependencies = set()

        actual_dependencies.update(dep)
        for package in actual_dependencies:
            all_dependencies.update(get_all_deps(package))

        all_dependencies.update(actual_dependencies)
        all_dependencies.update(exe_dep)
        reduced_h_dep = reduced_h_deps.copy()
        reduced_l_dep = reduced_l_deps.copy()

        for h_file in reduced_h_dep:
            for package in reduced_h_dep[h_file]:
                p_0.add(package)
                if package in all_dependencies:
                    del reduced_h_deps[h_file]
                    break

        for lib_file in reduced_l_dep:
            for package in reduced_l_dep[lib_file]:
                p_0.add(package)
                if package in all_dependencies:
                    del reduced_l_deps[lib_file]
                    break

        
        analysis_result["files23_h"] = reduced_h_deps
        analysis_result["files23_l"] = reduced_l_deps
        p_2 = set()
        all_files3 = set()

        for h_file in reduced_h_deps:
            all_files3.add(h_file)
            for package in reduced_h_deps[h_file]:
                p_2.add(package)

        for lib_file in reduced_l_deps:
            all_files3.add(lib_file)
            for package in reduced_l_deps[lib_file]:
                p_2.add(package)

        f.write("\n")
        f.write(f"all_file2 : {str(len(all_files3))}")

        f.write("\n")
        f.write(f"p_2 : {str(len(p_2))}")
        f.write("\n")


        """ package_by_file_coverage = select_package_by_file_coverage(reduced_h_deps, reduced_l_deps)
        analysis_result["stage4"] = package_by_file_coverage
        actual_dependencies.update(package_by_file_coverage) """




        """ for package in all_dependencies:
            if package in actual_dependencies:
                actual_dependencies.remove(package) """
        print(all_dependencies)
        print(len(all_dependencies))

        analysis_result["all_dependencies"] = list(all_dependencies)
        f.write(f"all_dep : {str(len(all_dependencies))}")
        f.write("\n")
        
        print(actual_dependencies)

 

        print(exe_dep)

        jsonfile_analysis_result = open(f"{directory}/analysis_result{new}.json", "w")
        json.dump(analysis_result, jsonfile_analysis_result, indent = 4)

    else :
        package_by_file_coverage = select_package_by_file_coverage(h_deps, lib_deps)
        actual_dependencies.update(package_by_file_coverage)

        all_dependencies = set()

        for package in actual_dependencies:
            all_dependencies.update(get_all_deps(package))


        for package in all_dependencies:
            if package in actual_dependencies:
                actual_dependencies.remove(package)
        print(len(all_dependencies))
        print(actual_dependencies)
        print(exe_dep)

    #print(notfind)
    #print(actual_dependencies)
        


if __name__ == "__main__":
    directory = args.path.rstrip('/ ')
    mode = args.mode
    Astudy = args.Astudy
    function = args.function
    new = args.new
    if (directory):
        if not os.path.exists(directory):
            print("The project path does not exist")
            sys.exit(0)

        build = identify_build_tool(directory)
 
        if build == 0 :
            print("The project path does not contain a build script")
            sys.exit(0)
        project_files = get_existing_file(directory)
        #project_files = set()

        script_path = os.path.abspath(sys.argv[0])
        script_directory = os.path.dirname(script_path)
        
        if not os.path.exists(f"{directory}/log_files"):
            os.mkdir(f"{directory}/log_files")

        f = open(f'{directory}/mockbuild_result{new}', 'a')

        jsonpath = script_directory.rsplit("/", 1)[0] + "/json" 
        
        jsonfile = open(f"{jsonpath}/lib_only_one_package.json")
        lib_only_one_package = json.load(jsonfile)

        jsonfile2 = open(f"{jsonpath}/hh_only_one_package.json")
        h_only_one_package = json.load(jsonfile2)

        jsonfile3 = open(f"{jsonpath}/pc_only_one_package.json")
        pc_only_one_package = json.load(jsonfile3)

        jsonfile4 = open(f"{jsonpath}/lib_package.json")
        lib_package = json.load(jsonfile4)

        jsonfile5 = open(f"{jsonpath}/hh_package.json")
        h_package = json.load(jsonfile5)

        jsonfile6 = open(f"{jsonpath}/pc_package.json")
        pc_package = json.load(jsonfile6)

        jsonfile7 = open(f"{jsonpath}/package_files.json")
        package_files = json.load(jsonfile7)

        jsonfile8 = open(f"{jsonpath}/package_deps_new.json")
        package_deps = json.load(jsonfile8)
        
        jsonfile11 = open(f"{jsonpath}/program_package.json", "r")
        program_package = json.load(jsonfile11)

        if function:
            jsonfile9 = open(f"{jsonpath}/package_h_unique_func8.json")
            package_h_unique_func = json.load(jsonfile9)

            jsonfile10 = open(f"{jsonpath}/package_l_unique_func2.json")
            package_l_unique_func = json.load(jsonfile10)

        os.environ['antlrpath'] = f"{script_directory}/antlr4-demo"
        os.environ['rootpath'] = script_directory
        os.environ['projectpath'] = directory

        if mode:
            remove_log_files(directory)
        os.chdir(directory)

        mock_build_start_time = time.time()
        if build == "cmake":
            process_cmake()
        elif build == "auto":
            process_auto()
        elif build == "make":
            process_make()

        del os.environ['antlrpath']
        del os.environ['rootpath']
        del os.environ['projectpath']

        remove_virtual_files(directory)

    else :
        print("Please enter the project path like --path=/home/project")