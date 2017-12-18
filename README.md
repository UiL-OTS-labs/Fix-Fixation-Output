# Fix Fixation Output

A python script to process the output from Fixation. This adds extra information not given by the Fixation output and combines the ouput.

## Overview
The output from Fixation does not contain total Fixation times for regions. This script adds this information by processing Fixation's ```.agc``` and ```.jnf``` files. For every ```.agc``` file, it outputs an ```.act``` file with five extra columns:

1. **totfixdur**: sum of all fixation durations in the region
2. **totfixcnt**: the number of fuxations in the region 
3. **NumFixQualNot0**: the number of fixations in the region that do not have Qual 0 (e.g. blinks or rejected fixations)
4. **totfixQual0dur**: The sum of all fixations durations in the region with Qual 0
5. **totfixQual0cnt**: The number of all fixation in the region with Qual 0

The script will also combine all the generated ```.act``` files into a single file: ```allACTFiles.txt```. It also splits up the ```planame``` field from your ```.act``` files into two seperate fields: ```condition``` and ```item```. 

Lastly, if the script finds any ```ags``` files, it will also combine these files into a single file: ```AllAGSFiles.txt```. The ```planame``` will also be split into the ```condition``` and ```item``` fields.

## Requirement
- Python 3

## Usage
The easiest way to use this script is to drop it in the same place as your fixation  ```.ini``` file. The script will autodetect the result folder for you in most cases. It will tell you which folder it detected, and ask you to confirm. Type ```n``` if you want to specify a different folder. Otherwise, press ```enter``` to run the script.

If the script didn't autodetect your result folder, or you want to specify a different one, the script will ask you to specify where the folder is located. This can ne a _full path_ like ```D:/eyetrack/data/\[projectname\]/result``` (Windows) or ```/home/\[Username\]/eyetrack/data/\[projectname\]/result``` (Linux). 

Alternatively, you can specify a _relative path_ like ```data/result```. Relative paths are paths from the script's location to the desired folder.

After you entered the correct path, the script will run. 