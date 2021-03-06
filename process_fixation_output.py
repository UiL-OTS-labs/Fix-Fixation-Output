#!/usr/bin/env python3
"""
A python script to process the output from Fixation. This adds extra information not given by the Fixation output
and combines the output.

See README.md in https://github.com/UiL-OTS-labs/Fix-Fixation-Output for more detailed info

Adapted from the original perl scripts developed at UiL OTS.
"""
from __future__ import print_function

import os
import re
import argparse
import inspect
import sys

"*** Variables ***"
_result_path = ''  # Fixation result files folder.
_output_path = ''  # The folder to which we should output, if none is supplied, the result folder will be used
_act_files = []  # This will contain all act data, used to generate the allACTFiles file
_agc_present = False  # If the folder contains agc files, used to check if we should do certain steps
_ags_present = False  # If the folder contains ags files, used to check if we should do certain steps
_safe_exit = True  # This is set to false in the tests cases, so that we don't need to press something to exit

"*** Python 2/3 cross compatibility ***"

try:
    # This will trigger an error in Python 3
    inspect.isfunction(raw_input)
except NameError:
    # We catch that error here, and define raw_input with the Python 3 input function
    raw_input = input

"*** General helper functions ***"


def exists_in_path(cmd):
    """This function checks if a given command is registered in the PATH of this computer

    Is used as a way to check for installed terminal emulators

    :param cmd:
    :return:
    """
    # can't search the path if a directory is specified
    assert not os.path.dirname(cmd)

    extensions = os.environ.get("PATHEXT", "").split(os.pathsep)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        base = os.path.join(directory, cmd)
        options = [base] + [(base + ext) for ext in extensions]
        for filename in options:
            if os.path.exists(filename):
                return True

    return False


def ask(message):
    """This function is a simple way to get a [Y/n] message on the screen.

    :param message: The question to be asked
    :return: If the person answered yes, a True will be returned
    """
    return raw_input(message + '[y/n] (y is default) ').lower() != 'n'


def ask_for_path():
    """This funtion is used to ask the user for the location of a folder.

    It will also verify that folder, and ask again if the folder doesn't exist.
    :return: folder location
    """
    global _result_path

    # Message to display asking for the folder location
    input_message = """Please fill in the location of the directory containing your .JNF, .agc and/or .ags files.
Either relative to this script or relative to the root of the drive.
For example: "D:/Users/123456/EXP/result" or "EXP/result"\n"""

    # Message to display if the entered folder is incorrect
    message_does_not_exists = 'We couldn\'t find Fixation files in the specified directory.'

    # Ask for the folder location
    folder = raw_input(input_message)

    # Check if the folder exits
    if not os.path.isdir(folder):
        print('We couldn\'t find the specified directory.')
        ask_for_path()
        return

    # Check if the folder contains JNF files if there are also no ags files
    if not does_folder_contain_files('.jnf', folder) and not does_folder_contain_files('.ags', folder):
        print(message_does_not_exists)
        ask_for_path()
        return

    # Check if the folder contains agc/ags files
    if not does_folder_contain_files('.agc', folder) and not does_folder_contain_files('.ags', folder):
        print(message_does_not_exists)
        ask_for_path()
        return

    _result_path = folder


def format_folder_name(folder):
    return "(Currect Directory)" + folder[1:]


def autodetect_result_path():
    """This function tries to autodetect Fixation result folders and ask the user which one they want to use.

    This function looks through the sub folders in the script's running directory. If it finds one, it asks
    the user to confirm if they want to use this folder. If not, it asks the user to specify the right folder.

    If it finds more, it suggests all of them to the user. The user can pick one, or specify a different one
    not listed.

    If there are no directories found, it will ask the user for the location of the directory.

    :return: None
    """
    global _result_path

    # Get all sub folders
    sub_folders = [(x[0], x[2]) for x in os.walk('.')]

    possible_paths = []

    # Loop over them
    for sub_folder, files in sub_folders:
        # Check if this folder contains jnf and agc/ags files. If so, return the name of that folder
        if does_folder_contain_files('.jnf', None, files) and does_folder_contain_files('.agc', None, files):
            possible_paths.append(sub_folder)
        elif does_folder_contain_files('.ags', None, files):
            possible_paths.append(sub_folder)

    # If there is one possible path
    if len(possible_paths) == 1:
        # Set it as the path
        _result_path = possible_paths[0]
        # Ask for confirmation
        if not ask('We\'ve detected a folder we think contains your Fixation result files: {} \n'
                   'Is this correct? '.format(format_folder_name(_result_path))):
            # If the user wants to use a different directory, ask for the location
            ask_for_path()

        return

    # If the possible paths is empty, ask for the directory location
    if not possible_paths:
        print('We couldn\'t find a folder containing your Fixation result files.')
        ask_for_path()
        return

    # There are multiple paths, so list them to the user and ask them which one they want to use
    print("We've detected multiple folders containing Fixation result files:")
    for i, item in enumerate(possible_paths):
        print("{}: {}".format(i + 1, format_folder_name(item)))

    print("Please enter the number of the folder you want to use, or press enter to enter a custom path")
    user_choice = raw_input()

    # If the response is a digit
    if user_choice.isdigit():
        # Cast it to an int
        user_choice = int(user_choice)
        # If the response is a valid index
        if len(possible_paths) >= user_choice > 0:
            # Use that index
            _result_path = possible_paths[user_choice - 1]
        else:
            # Otherwise, ask for the proper path
            print('Invalid or no option selected, please enter the location of the desired directory')
            ask_for_path()
    else:
        # Otherwise, just ask for the path
        ask_for_path()


def check_if_valid_path(path):
    """This function checks if a folder is a valid result directory

    :param path:
    :return: bool
    """
    if does_folder_contain_files('.jnf', path) and does_folder_contain_files('.agc', path):
        return True
    elif does_folder_contain_files('.ags', path):
        return True

    return False


def does_folder_contain_files(file_extension, folder, files=None):
    """This function is used to check if a folder contains files with a certain file extension

    :param file_extension: The required file extension
    :param folder: The to be checked folder
    :param files: You can give a list of files in this folder if you already have if (optional)
    :return: If the folder contains files with the specified file extension
    """
    # Get all the files if they weren't given
    if files is None:
        files = os.listdir(folder)

    # For every file in the specified directory
    for fname in files:
        # If the file ends with the specified extension, return true
        if fname.lower().endswith(file_extension.lower()):
            return True

    # Return false in the base case, as we should've already returned if there was a file with the right extension
    return False


def check_path_writable_executable(path):
    """This function checks if the result directory is both writable and executable.

    We don't need to check readable, as the previous commands to get the directory will fail if they can't read the
    folder.

    We need executable permissions on the folder so that we can use search functions in the folder.
    :return: A boolean indicating if the result directory is writable
    """
    return os.access(path, os.W_OK) and os.access(path, os.X_OK)


def safe_exit(status_code=0):
    """This function is used to exit from the program without closing the window.

    This function asks the user to press enter before actually closing the window. This is necessary as this script will
    probably be run on Windows mostly, and default behaviour is to open it's own prompt for the script.
    :return:
    """
    print()
    if _safe_exit:
        raw_input("Press Enter to exit...")
    sys.exit(status_code)


def check_number_columns_in_row(row, expected_number, hard_fail):
    """This function checks if there are just as many columns in a row as expected.

    Sometimes fixation derps, and doesn't provide proper output. This function checks for that and displays a warning
    to the user about this. If specified, it can also stop the function all together.

    :param row: A list representing a row
    :param expected_number: The expected number of columns in the row
    :param hard_fail: If the function should stop the script when it's found a misformed line
    :return: None
    """

    if len(row) != expected_number:
        print()
        print("Badly formatted line found in this file! Stopping.")
        print("Please check if Fixation hasn't written anything weird to this file")
        print("Misformatted line: {}".format(" ".join(row)))
        print("Detected {} colunns, expected {} columns".format(len(row), expected_number))
        if hard_fail:
            safe_exit(4)
        else:
            return False

    return True


"*** Processing functions ***"


def sort_jnf_file(file):
    """This function sorts the entries in a JNF file

    This function loads a JNF files, and sorts it's contents on the imgfile and code fields, in ascending order.
    It also ignores the column headers, so that we do not process it in any step.

    :param file: The file to be read
    :return: A list of lists. Every list in the list represents a line in the files, splitted into the file columns
    """
    # Open the specified file
    with open(file) as f:
        # Read all lines, remove any newline characters and split the line in columns. This also ignores the header line
        lines = [x.replace('\r', '').replace('\n', '').split(' ') for x in f.readlines() if not x.startswith('expname')]

        # Sort the line on the imgfile and code fields (columns 2 and 30)
        lines = sorted(
            lines,
            key=lambda x: (x[1], int(x[29]))
        )

        return lines


def make_trt(lines):
    """This function calculates the missing values from a JNF file.

    :param lines: A list of lists representing the JNF file
    :return: a dictionary with as key an combination of pla_name and last_code, with as value the TRT values in a list
    """
    # Programmer's note: This is all magic!

    # Define all used variables
    last_pla_name       = None
    last_code           = None
    last_fixation       = None
    last_sacc_in        = None
    last_sacc_out       = None
    last_ok_fixation    = None
    last_ok_sacc_in     = None
    last_ok_sacc_out    = None
    lastqualtotfix      = None
    lastnumbertotfixok  = None
    lastnumbertotfix    = None

    # This dict will contain the TRT entries using a key based upon the pla_name and code fields
    trt = {}

    # Loop over the lines
    for line in lines:
        # Check if the line is complete
        check_number_columns_in_row(line, 36, False)

        # Cast values to the right types and put them in more descriptive variable names.
        fixation        = int(line[10])
        pla_name        = line[1]
        code            = int(line[29])
        sacc_in         = int(line[11])
        sacc_out        = int(line[12])
        qual            = int(line[13])

        # Correct negative fixations to 0
        if fixation < 0:
            fixation    = 0

        # Default values
        ok_fixation     = 0
        ok_sacc_in      = 0
        ok_sacc_out     = 0
        qualtotfix      = 1
        numbertotfix    = 1
        numbertotfixok  = 0

        # If qual = 0, we need to change some of the values specified under 'default values'
        if qual == 0:
            ok_fixation         = fixation
            ok_sacc_in          = sacc_in
            ok_sacc_out         = sacc_out
            qualtotfix          = 0
            numbertotfixok      = 1

        # If this line belongs to the same group
        if pla_name == last_pla_name and code == last_code:
            # Add all values to the counters
            last_fixation       = fixation          + last_fixation
            last_sacc_in        = sacc_in           + last_sacc_in
            last_sacc_out       = sacc_out          + last_sacc_out

            last_ok_fixation    = ok_fixation       + last_ok_fixation
            last_ok_sacc_in     = ok_sacc_in        + last_ok_sacc_in
            last_ok_sacc_out    = ok_sacc_out       + last_ok_sacc_out

            last_pla_name       = pla_name
            last_code           = code

            lastqualtotfix      = qualtotfix        + lastqualtotfix
            lastnumbertotfixok  = numbertotfixok    + lastnumbertotfixok
            lastnumbertotfix    = numbertotfix      + lastnumbertotfix
        # Else it's a new group (or the first group)
        else:
            # If this is not the first group encountered
            if last_pla_name is not None:
                # Add the last group to the dict
                trt[last_pla_name + str(last_code)] = [
                        str(last_fixation),
                        str(lastnumbertotfix),
                        str(lastqualtotfix),
                        str(last_ok_fixation),
                        str(lastnumbertotfixok)
                    ]

            # Initialize all counters with this line's value
            last_pla_name       = pla_name
            last_code           = code
            last_fixation       = fixation
            last_sacc_in        = sacc_in
            last_sacc_out       = sacc_out

            if qual == 0:
                last_ok_fixation    = fixation
                last_ok_sacc_in     = sacc_in
                last_ok_sacc_out    = sacc_out
                lastqualtotfix      = 0
                lastnumbertotfix    = 1
                lastnumbertotfixok  = 1
            else:
                last_ok_fixation    = 0
                last_ok_sacc_in     = 0
                last_ok_sacc_out    = 0
                lastqualtotfix      = 1
                lastnumbertotfix    = 1
                lastnumbertotfixok  = 0

    # Add the last group to the dict
    trt[last_pla_name + str(last_code)] = [
            str(last_fixation),
            str(lastnumbertotfix),
            str(lastqualtotfix),
            str(last_ok_fixation),
            str(lastnumbertotfixok)
        ]

    return trt


def make_act(trt, agc):
    """This function generates a act file for a given agc file and a given TRT dict.

    :param trt: The TRT dict generated by make_trt(1).
    :param agc: The location of the agc file
    :return: A list of lists, containing strings. Which represents an act file.
    """
    # This var stores the output while it's being created
    act = []

    # Open the actual file
    with open(agc) as agc_file:
        # Parse the lines to a list of row lists of columns
        lines = [x.replace('\r', '').replace('\n', '').split(' ')
                 for x in agc_file.readlines() if not x.startswith('expname')]

        # For every line
        for line in lines:
            # Check if the line is complete
            check_number_columns_in_row(line, 28, True)

            # Generate the TRT dict key
            key = line[3] + line[5]

            # Check if the TRT has an entry for this line
            if key in trt:
                # If so, combine the agc line with the TRT line and store them in the output list
                act.append(line + trt[key])
            else:
                # If not, complement the agc line with 5 zero's and store that in the output list
                act.append(line + ['0', '0', '0', '0', '0'])

    # Return all lines in this new act file
    return act


def process_jnf_agc_files():
    """This function processes all JNF and agc files.

    This function opens an JNF file, sorts it and calculates a trt for it. It then uses this generated TRT to create a
    act file for the corresponding agc file.
    :return: nothing!
    """

    # If there are no agc files, display a nice message and stop
    if not _agc_present:
        print('No agc files found, skipping this step')
        print()
        return

    # Get a sorted list of all JNF files in the result dir
    files = sorted([x for x in os.listdir(_result_path) if x.lower().endswith('.jnf')])

    # For every JNF file
    for file in files:
        # Removed the .JNF extension to get the filename
        short_filename = file[:-4]

        # Sort the lines in the file
        print('Sorting {}'.format(short_filename))
        sorted_lines = sort_jnf_file(os.path.join(_result_path, file))

        # Calculate the TRT for this JNF using the sorted lines
        print('Calculating TRT for {}'.format(short_filename))
        trt = make_trt(sorted_lines)

        # Make the act file for the corresponding agc file
        print('Making act for {}'.format(short_filename))
        act = make_act(trt, os.path.join(_result_path, short_filename + '.agc'))

        # Add this act file to the list of all act files
        _act_files.append((short_filename, act))

        # Add the headers to the act file. This is done after adding the act to the global _act_files so that the
        # headers aren't in that variable. The script doesn't need them, but humans do in the written act file
        act = [["expname", "blocknr", "subjectnr", "imgfile", "pagenr", "code", "code2", "ffdur", "ffqual", "ffbck",
                "ffin", "ffout", "rpdur", "rpqual", "rpcnt", "rpsacc", "rpout", "tgdur", "tgqual", "tgcnt",
                "tgsacc", "tgout", "gdur", "gqual", "gcnt", "gsacc", "gbck", "gout", "totfixdur", "totfixcnt",
                "NumFixQualNot0", "totfixQual0dur", "totfixQual0cnt"]] + act

        # Write the act file to an actual file on the filesysten
        with open(os.path.join(_output_path, '{}.act'.format(short_filename)), 'w+') as f:
            f.writelines([' '.join(x) + "\n" for x in act])
            f.close()

        # Print a separator line for output readability
        print()


def process_combined_file_lines(lines, imgfile_index, file):
    """This function processes every supplied line and writes it to a supplied file

    This function is used by both combine functions to write their lines to the combined file.
    It also splits the imgfile column in two columns: cond and item. You need to specify the index
    this column.

    :param lines: A list of lines to process
    :param imgfile_index: The index on which the imgfile field lives
    :param file: A file IO object to write to
    :return: /dev/null
    """
    # For every line in this act
    for line in lines:
        # Create a list to hold the output in while processing
        output_line = []
        for i, value in enumerate(line):
            # If this is the imgfile field, process it to get the cond and item fields
            if i == imgfile_index:
                # An image file is named using a naming scheme: {cond+item}.BMP.
                # cond is a string of at least 1 characters
                # item is an integer of at least 3 digits
                # We use a regex to split these into a tuple
                cond_item = re.findall(r'([a-zA-Z]+)([0-9]+)', value)

                # Sanity check mostly to see if it's actually found something, should not error
                if cond_item is not None and len(cond_item) == 1:
                    # Get the cond and item out of the tuple
                    cond, item = cond_item[0]

                    # Add them to the output
                    output_line.append(cond)
                    output_line.append(item)
                else:
                    # But just in case, handle it
                    print("Badly formatted line found in this file! Stopping!")
                    print("Please check if Fixation hasn't written anything weird to this file")
                    print("Misformatted line: {}".format(" ".join(line)))
                    safe_exit(2)
            else:
                # Otherwise just straight add it to the output
                output_line.append(value)

        # Write this line to the output file
        file.write(" ".join(output_line))
        file.write("\n")


def combine_act_files():
    """This function combines all generated act files.

    This function takes all generated act files, and combines it into one master file.
    It also replaces the imgfile field of every act file with an cond and item field.

    These two fields are generated out of the imgfile field.

    :return: Nada
    """

    # If there are no agc files, display a nice message and stop
    if not _agc_present:
        print('No agc files found, skipping this step')
        print()
        return

    # open the output file
    with open(os.path.join(_output_path, 'allACTFiles.txt'), 'w+') as f:
        # Write the file headers, for clarity
        print('Writing headers')
        f.write('expname blocknr subjectnr cond item pagenr code code2 ffdur ffqual ffbck ffin ffout rpdur rpqual '
                'rpcnt rpsacc rpout tgdur tgqual tgcnt tgsacc tgout gdur gqual gcnt gsacc gbck gout totfixdur '
                'totfixcnt NumFixQualNot0 totfixQual0dur totfixQual0cnt\n')
        print()

        # Go over all the generated act files
        for k, v in _act_files:
            # Inform the user of what we are doing
            print('Adding {}.act'.format(k))

            # Process the lines of this file
            process_combined_file_lines(v, 3, f)

        # Inform the user that we are done creating the combined file
        print()
        print('Created allActFiles.txt')
        print()


def combine_ags_files():
    """This function combines all ags files

    This function takes all found ags files, and combines it into one master file.
    It also replaces the imgfile field of every act file with an cond and item field.

    These two fields are generated out of the imgfile field.
    :return:
    """
    # Newline in output for clarity
    print()

    # If there are no ags files, display a nice message and stop
    if not _ags_present:
        print('No ags files found, skipping this step')
        return

    # Get all files ending with ags, and sort them
    files = sorted([x for x in os.listdir(_result_path) if x.lower().endswith('.ags')])

    # Open the output file
    with open(os.path.join(_output_path, 'allAGSFiles.txt'), 'w+') as output_file:
        # Write the file headers, for clarity
        print('Writing headers')
        output_file.write('expname cond item timfile blocknr subjectnr pagenr samplenr samstart event fixnr fixdur '
                          'qual obtnr code code2 timcode timstart timname\n')

        # Loop over every file and open that file
        for file in files:
            with open(os.path.join(_result_path, file)) as f:
                # Inform the user of what we are doing
                print('Adding {}'.format(file))

                # Load all lines in this file except for the header and split them into columns
                lines = [x.replace('\r', '').replace('\n', '').split(' ')
                         for x in f.readlines() if not x.startswith('expname')]

                # Process the lines of this file
                process_combined_file_lines(lines, 1, output_file)

        # Inform the user that we are done creating the file
        print()
        print('Created allAGSFiles.txt')


def arg_parse():
    """This function sets up a basic argument parser.

    It can be used to supply the result folder directly from the command line

    :return:
    """
    parser = argparse.ArgumentParser(description='This script parses the standard output from Fixation. '
                                                 'This adds extra information not given by the Fixation output '
                                                 'and combines all act and all ags files in allACTFiles.txt and '
                                                 'AllAgsFiles.txt.')
    parser.add_argument('path', metavar='dir', nargs="?", type=str, help='The location of the folder containing the to '
                                                                         'be processed files. If the folder is invalid '
                                                                         'or omitted, it will be ignored.')

    parser.add_argument('output', metavar='out', nargs="?", type=str, help='The location of the folder where the output'
                                                                           ' should be stored. When not supplied, the '
                                                                           'input dir will be used.')

    return parser.parse_args()


"*** Main function ***"

# These parameters are used in the testcases
def main(result_path=None, output_path=None):
    """Main function that starts all the magic.

    It is called at the end of this file.
    :return:
    """
    # Use the global _result_path, so that all functions can use it
    global _result_path
    global _output_path
    global _agc_present
    global _ags_present

    # Check if the paths were supplied
    if result_path is None and output_path is None:
        # Setup the argument parser
        args = arg_parse()

        # If a path is supplied through the arguments and is valid
        if args.path is not None and check_if_valid_path(args.path):
            _result_path = args.path
        else:
            # Otherwise, resolve the result path we need to use
            print('-----  Trying to autodetect result folder(s) containing Fixation output files -----')
            print()
            autodetect_result_path()

        # If an output path is supplied through the arguments and is valid
        if args.output is not None and check_path_writable_executable(args.output):
            _output_path = args.output
        else:
            # Otherwise, default to the result path
            _output_path = _result_path
    else:
        _result_path = result_path
        _output_path = output_path

    # Check if we can write to the result directory
    if not check_path_writable_executable(_result_path):
        print()
        print("Could not write to the results directory. Please check the permissions for that folder or ask for help")
        safe_exit(3)

    # Check if there are agc files present. Put in a variable beforehand because of performance reasons
    if does_folder_contain_files('.agc', _result_path):
        _agc_present = True

    # Check if there are ags files present. Put in a variable beforehand because of consistency
    if does_folder_contain_files('.ags', _result_path):
        _ags_present = True

    # Start the processing
    print()
    print('----- Processing individual JNF and agc files -----')
    process_jnf_agc_files()

    print('----- Combining act files -----')
    combine_act_files()

    print('----- Combining ags files -----')
    combine_ags_files()

    print()
    print('----- Done! -----')

    safe_exit()


# Only run if this file is executed by itself
if __name__ == '__main__':

    # If this is Linux, and we are not running through a terminal, open a terminal and execute there.
    if (sys.platform == "linux2" or sys.platform == "linux") and not sys.stdout.isatty():
        # List of supported terminal emulators
        terminals = ['gnome-terminal', 'mate-terminal', 'xfce4-terminal', 'lxterminal', 'rxvt-unicode', 'rxvt', 'xterm']

        # Loop over the terminals
        for terminal in terminals:
            # If it is found, and installed
            if exists_in_path(terminal):
                # Execute a terminal and run Python in it
                os.system(terminal + " -e 'python process_fixation_output.py'")
                break

        # Stop this instance of the code
        sys.exit(0)

    main()
