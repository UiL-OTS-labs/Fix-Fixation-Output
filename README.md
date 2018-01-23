# Fix Fixation Output
[![Build Status](https://travis-ci.org/UiL-OTS-labs/Fix-Fixation-Output.svg?branch=master)](https://travis-ci.org/UiL-OTS-labs/Fix-Fixation-Output)

A python script to process the output from Fixation. This adds extra information not given by the Fixation output and 
combines the output.

## Overview
The output from Fixation does not contain total Fixation times for regions. This script adds this information by 
processing Fixation's ```.agc``` and ```.jnf``` files. For every ```.agc``` file, it outputs an ```.act``` file with five extra columns:

1. **totfixdur**: sum of all fixation durations in the region
2. **totfixcnt**: the number of fuxations in the region 
3. **NumFixQualNot0**: the number of fixations in the region that do not have Qual 0 (e.g. blinks or rejected fixations)
4. **totfixQual0dur**: The sum of all fixations durations in the region with Qual 0
5. **totfixQual0cnt**: The number of all fixation in the region with Qual 0

The script will also combine all the generated ```.act``` files into a single file: ```allACTFiles.txt```. It also
 splits up the ```planame``` field from your ```.act``` files into two seperate fields: ```condition``` and ```item```. 

Lastly, if the script finds any ```ags``` files, it will also combine these files into a single file: 
```AllAGSFiles.txt```. The ```planame``` will also be split into the ```condition``` and ```item``` fields.

## Requirement
- Python 2 or Python 3

## Usage
The easiest way to use this script is to drop it in your fixation results folder.
However, the script will autodetect any result folder located in any subfolder from where you run the script. 

If there is only one folder, it will tell you which folder it detected and ask you to confirm. Type ```n``` if you
 want to specify a different folder. Otherwise, press ```enter``` to run the script.

If there are multiple folders found, it will ask you to choose one. Alternatively you can specify one on your own.

If the script didn't autodetect your result folder, or you want to specify a different one, type in the location of 
the folder. This can be a _full path_ like ```D:/eyetrack/data/[projectname]/result``` (Windows) 
or ```/home/[Username]/eyetrack/data/[projectname]/result``` (Linux). 

Alternatively, you can specify a _relative path_ like ```data/result```. Relative paths are paths from the script's 
location to the desired folder.

After you entered the correct path, the script will run. 

## Note on macOS

Due to limitations in macOS, running the script from Finder is not always possible. 
You need to have a separate installation of python installed, the version that comes with macOS is not capable of 
running the script from Finder. You can however run it from the commandline, or follow the steps below

Install the newest version of Python from [here](https://www.python.org/downloads/). 
After you installed it, you can run the script by right clicking on the file, Open As and select 'Python Launcher'.
You can select it as your default to enable double clicking the file.

## Advanced usage (Commandline Linux/Mac)

You can also run this script on the commandline. Place the file where you want to run it. 
Then, open a terminal window, and navigate to the location of the script.
Type ```python process_fixation_output.py```, and te script will run.

You can also supply the location of your fixation files to this command, by simply appending the filepath to the command.
For example: ```python process_fixation_output.py /home/user/fixation/data``` (absolute path) 
or ```python process_fixation_output.py fixation/data``` (relative path)