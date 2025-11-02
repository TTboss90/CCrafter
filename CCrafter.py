import json
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

    "libraries": [],

    "deps":[],

    "Out_structure":[],

    "Out_Files":{},

    "Post_script":"",

    "Out_type":"exec",
    "Out_File":"main.exe"
}'''
}

def all_file_in_a_folder(path,extension):
    Ofiles = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(extension):
                Ofiles.append(os.path.join(root, file))

    return Ofiles

def get_json(path):
    assert os.path.exists(path)
    with open(path, "r") as file:
        Fjson = json.load(file)
    return Fjson

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
    os.makedirs(obj_dir, exist_ok=True)
    os.makedirs(os.path.join(obj_dir,proj_name), exist_ok=True)

    out_name = os.path.splitext(os.path.basename(file))[0] + ".o"
    out_path = os.path.join('.',obj_dir,proj_name, out_name)
    compile_obj = False

    if not os.path.exists(out_path):
        compile_obj = True
    elif not os.path.getmtime(file) == os.path.getmtime(out_path) or os.path.getatime(file) == os.path.getatime(out_path):
        compile_obj = True

    if compile_obj:
        compile = True

        cmd = Msettings.get("Compiler")+["-c", "-o",out_path,file] + incudeFolders
        print(" ".join(cmd))
        subprocess.run(cmd)
        mod_time = os.path.getmtime(file)
        acc_time = os.path.getatime(file)
        os.utime(out_path, (acc_time, mod_time))
    
    return out_path

def build_proj(path):
    global compile
    compile = False
    settings = get_json(os.path.join(path,"settings.json"))
    if settings.get("Out_type") == "exec":
        out_file = os.path.join(".","out","bin",settings.get("Out_File"))
        compiler = Msettings.get("Compiler")
    elif settings.get("Out_type") == "static_lib":
        out_file = os.path.join(".","out","obj",settings.get("Out_File"))
        compiler = Msettings.get("archiver")
    else:
        print(f"proj {path} Out_type not vaild")
        exit(1)
    out_folder = os.path.dirname(out_file)
    os.makedirs(out_folder, exist_ok=True)

    make_structe(settings.get("Out_structure"),settings.get("Out_Files"),out_folder,file_copy=True)

    src_files = []
    for Folder in settings.get("Src_paths",[]) + [path]:
        src_files.extend(all_file_in_a_folder(os.path.join(Folder), ".c"))

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

    cmd = compiler+[ "-o",out_file] + settings.get("flags") + obj_files + deps_folders + lib_files

    if compile == True:
        print(" ".join(cmd) + "\n")
        subprocess.run(cmd)

    if not settings.get("Post_script") == "":
        print(settings.get("Post_script"))
        subprocess.run(settings.get("Post_script"))
    return out_file

def build():
    global Msettings
    Msettings = get_json("settings.json")
    assert Msettings.get("Projects") != []
    for Proj in Msettings.get("Projects"):
        build_proj(Proj)

def main():
    print("\n")
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
                newP = os.path.join("src",sys.argv[2])
                os.makedirs(os.path.join(newP), exist_ok=True)
                open(os.path.join(newP,"settings.json"),"w").write(PSettings.get("settings.json"))
        else:
            build()
    else:
        make_structe(Bstruct,BSettings,".")

if __name__ == "__main__":
    main()
