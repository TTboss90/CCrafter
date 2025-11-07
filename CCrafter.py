import json5
import os
import sys
from pathlib import Path
import subprocess
import shutil

Bstruct = {
    "src"
}
BSettings ={
    "settings.json":
'''{
    "Compiler":["gcc"],
    "archiver":["ar","rcs"],

    "Projects":[]
}'''
}
PSettings ={
    "settings.json":
'''{
    "flags":[],

    "Src_paths":[],

    "Include_paths":[],

    "file_flags":{},

    "libraries": [],

    "deps":[],

    "Out_structure":[],

    "Out_Files":{},

    "Post_script":"",

    "Out_type":"exec",
    "Out_File":"main.exe"
}'''
}

def test_case(iserror,message):
    if not iserror:
        print(message)
        exit(1)

def all_file_in_a_folder(path,extension):
    Ofiles = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(extension):
                Ofiles.append(os.path.join(root, file))

    return Ofiles

def get_json(path):
    test_case(os.path.exists(path),f"{path} does not exists")
    with open(path, "r") as file:
        Fjson = json5.load(file)
    return Fjson

def make_proj(name):
    newP = os.path.join("src",name)
    os.makedirs(os.path.join(newP), exist_ok=True)
    open(os.path.join(newP,"settings.json"),"w").write(PSettings.get("settings.json"))

def get_settings(path):
    json = get_json(path)
    test_case('flags' in json,f"no flags item in {path}")
    test_case('Src_paths' in json,f"no Src_paths item in {path}")
    test_case('Include_paths' in json,f"no Include_paths item in {path}")
    test_case('file_flags' in json,f"no file_flags item in {path}")
    test_case('libraries' in json,f"no libraries item in {path}")
    test_case('deps' in json,f"no deps item in {path}")
    test_case('Out_structure' in json,f"no Out_structure item in {path}")
    test_case('Out_Files' in json,f"no Out_Files item in {path}")
    test_case('Post_script' in json,f"no Post_script item in {path}")
    test_case('Out_type' in json,f"no Out_type item in {path}")
    test_case('Out_File' in json,f"no Out_File item in {path}")
    return json


def make_structe(folders,files,path,file_copy=False):
    for folder in folders:
        os.makedirs(os.path.join(path,folder), exist_ok=True)
    for file in files:
        if not file_copy: 
            open(os.path.join(path,file),"w").write(files[file])
        else:
            open(os.path.join(path,file),"w").write(open(os.path.join(files[file]),"r").read())

def build_obj(settings,file,incudeFolders):
    global compile
    proj_folder = os.path.dirname(file)
    proj_name = Path(file).parent.name
    obj_dir = os.path.join("out", "obj")
    file_name = os.path.basename(file)
    out_name = os.path.splitext(os.path.basename(file))[0] + ".o"
    out_path = os.path.join('.',obj_dir,proj_name, out_name)
    file_flags = settings.get("file_flags",{}).get(file_name,[])
    compile_obj = False

    os.makedirs(obj_dir, exist_ok=True)
    os.makedirs(os.path.join(obj_dir,proj_name), exist_ok=True)

    if not os.path.exists(out_path):
        compile_obj = True
    elif not os.path.getmtime(file) == os.path.getmtime(out_path) or os.path.getatime(file) == os.path.getatime(out_path):
        compile_obj = True

    if compile_obj:
        compile = True

        cmd = Msettings.get("Compiler")+["-c", "-o",out_path,file] + file_flags + incudeFolders
        print(" ".join(cmd))
        subprocess.run(cmd)
        test_case(os.path.exists(out_path),f"failed to make {out_path}")
        mod_time = os.path.getmtime(file)
        acc_time = os.path.getatime(file)
        os.utime(out_path, (acc_time, mod_time))
    
    return out_path

def build_proj(path):
    global compile
    compile = False
    test_case(os.path.exists(os.path.join(path,"settings.json")),f"{os.path.join(path,"settings.json")} does not exists")
    settings = get_settings(os.path.join(path,"settings.json"))
    if settings.get("Out_type") == "exec":
        out_file = os.path.join(".","out","bin",settings.get("Out_File"))
        compiler = Msettings.get("Compiler")
    elif settings.get("Out_type") == "static_lib":
        out_file = os.path.join(".","out","obj",settings.get("Out_File"))
        compiler = Msettings.get("archiver")
    else:
        test_case(False,f"{settings.get("Out_type")} is not a vaild Out_type for {path}")
    
    out_folder = os.path.dirname(out_file)
    os.makedirs(out_folder, exist_ok=True)

    make_structe(settings.get("Out_structure"),settings.get("Out_Files"),out_folder,file_copy=True)

    src_files = []
    for Folder in settings.get("Src_paths",[]) + [path]:
        src_files.extend(all_file_in_a_folder(os.path.join(Folder), ".c"))

    test_case(src_files != [],f"no Src files in {path}")

    lib_files = []
    for Folder in settings.get("libraries",[]):
        lib_files.extend(all_file_in_a_folder(Folder, ".a"))

    incude_folders = []
    for Folder in settings.get("Include_paths",[]):
        incude_folders.append("-I"+Folder)

    deps_folders = []
    for Proj in settings.get("deps",[]):
        deps_folders.append(build_proj(Proj))

    obj_files = []
    for file in src_files:
        obj_files.append(build_obj(settings,"."+os.path.join(path,file[1:]),incude_folders))
    
    test_case(obj_files != [],f"no obj files for proj {path}")

    cmd = compiler+[ "-o",out_file] + settings.get("flags") + obj_files + deps_folders + lib_files

    if compile == True:
        print(" ".join(cmd))
        subprocess.run(cmd)

    test_case(os.path.exists(out_file),f"failed to make {out_file}")

    if not settings.get("Post_script") == "":
        print(settings.get("Post_script"))
        subprocess.run(settings.get("Post_script"))
    
    return out_file

def build():
    global Msettings
    Msettings = get_json("settings.json")
    test_case(Msettings.get("Projects") != [],"Projects emtpy")
    test_case(Msettings.get("archiver") != [],"no archiver")
    test_case(Msettings.get("Compiler") != [],"no Compiler")
    for Proj in Msettings.get("Projects"):
        build_proj(Proj)

def main():
    if os.path.exists("settings.json"):
        if len(sys.argv) > 1:
            if sys.argv[1] == "clear":
                if os.path.exists("out"):
                    shutil.rmtree("out")
            elif sys.argv[1] == "rebuild":
                if os.path.exists("out"):
                    shutil.rmtree("out")
                build()
            elif sys.argv[1] == "new" and len(sys.argv) == 3:
                make_proj(sys.argv[2])
            else:
                test_case(False,f"not a flag '{sys.argv[1]}'")
        else:
            build()
    else:
        make_structe(Bstruct,BSettings,".")
        make_proj("main")



if __name__ == "__main__":
    main()
