# CCrafter 
a c build sys
made to be relatively easy
but still with a lot of control

## how to use
to start do this in a empty folder

```python CCrafter.py```

^this makes

```
./
CCrafter.py
settings.json
src/
    main/
        settings.json
```

to make a proj do

```python CCrafter.py new {proj_name}```

^this makes 

```
./
CCrafter.py
settings.json
src/
    {proj_name}/
        settings.json
```

all .c file in the folder {proj_name} are in Compilation

to rm out do
```python CCrafter.py clear```

to rebuild do
```python CCrafter.py rebuild```

to build do
```python CCrafter.py```

## settings explained
the ./settings.json file is simple

proj settings:

flags are added when all objs are combined

all .c files in the Src_paths folder are added in Compilation

Include_paths is just -I{folder}

deps just is so the out of the proj(the dep) is in the proj

libraries are folder with a precompiled lib(./lib{name}.a,.so no added)

Out_structure are the folders(in bin)

Out_Files out(in bin):in(in ./)

Post_script is a subprocess after a proj compiled

Out_type exec or static_lib

Out_File is in bin

file_flags is to add file specific flags

## a example
folder structure
```
./
CCrafter.py
settings.json
include/
	math.h
src/
	main/
		settings.json
		main.c
	mathlib/
		settings.json
		math.c
```
./settings.json:
```
{
    "Compiler": ["gcc"],

    "archiver": ["ar","rcs"],

    "Projects": [
        "./src/mainProj"
    ]
}
```
./src/main/settings.json:
```
{
    "flags":[],

    "Src_paths":[],

    "Include_paths":[
        "./include"
    ],

    "libraries": [],

    "file_flags":{},

    "deps":[
        "./src/sideProj"
    ],

    "Out_structure":[
        "./img"
    ],

    "Out_Files":{
        "./img/img_name":"./imgsrc/img.jpg"
    },

    "Post_script":"./out/bin/main",

    "Out_type":"exec",
    "Out_File":"main"
}
```
./src/mathlib/settings.json:
```
{
    "flags":[],

    "Src_paths":[],

    "Include_paths":[],

    "libraries": [],

    "file_flags":{
        "math.c":["-O1"]
    },

    "deps":[],

    "Out_structure":[],

    "Out_Files":{},

    "Post_script":"",

    "Out_type":"static_lib",
    "Out_File":"libmath.a"
}
```
./include/math.h:
```
int add(int,int);
int sub(int,int);
```
./src/mathlib/math.c:
```
int add(int x,int y){
	return x+y;
}
int sub(int x,int y){
	return x-y;
}
```
./src/main/main.c:
```
#include <stdio.h>
#include "math.h"

int main(){
	printf("10 + 5 = %d",add(10,5));
	printf("10 - 5 = %d",sub(10,5));
	return 0;
}
```

## to do

shared libs(so/dll)

auto downloading deps
