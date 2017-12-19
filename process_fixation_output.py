#! /usr/bin/env python3

#  imports
import os
import re
from typing import List, Dict, IO

# variables
_result_path = ''  # Fixation result files folder.
_act_files = []  # This will contain all ACT data, used to generate the allACTFiles file


def ask(message: str) -> bool:
    """
    This function is a simple way to get a [Y/n] message on the screen.
    :param message: The question to be asked
    :return: If the person answered yes, a True will be returned
    """
    return input(message + '[Y/n] ') != 'n'


def ask_for_path() -> str:
    """
    This funtion is used to ask the user for the location of a folder. It will also verify that folder, and ask again
    if the folder doesn't exist.
    :return: folder location
    """
    # Message to display asking for the folder location
    input_message = """Please fill in the location of the directory. 
Either relative to this script or relative to the root of the drive.
e.g. "D:/eyetrack/exp/data/[project]/result" or "exp/[project]/result"\n"""

    # Message to display if the entered folder is incorrect
    message_does_not_exists = 'We couldn\'t find a fixation files in the specified directory.'

    # Ask for the folder location
    folder = input(input_message)

    # Check if the folder exits
    if not os.path.isdir(folder):
        print('We couldn\'t find the specified directory.')
        folder = ask_for_path()

    # Check if the folder contains JNF files
    if not does_folder_contain_files('.jnf', folder):
        print(message_does_not_exists)
        return ask_for_path()

    # Check if the folder contains AGC files
    if not does_folder_contain_files('.agc', folder):
        print(message_does_not_exists)
        return ask_for_path()

    return folder


def autodetect_result_path() -> str:
    """
    This function tries to autodetect the right folder to use by walking over all sub folders with a max depth of 1.
    This is accomplished by simply looping over sub folders till we find one with jnf and agc files.

    :return: The folder if found, otherwise current dir
    """
    # Get all sub folders
    sub_folders = [x[0] for x in os.walk('.')]

    # Loop over them
    for sub_folder in sub_folders:
        # Check if this folder contains jnf and agc files. If so, return the name of that folder
        if does_folder_contain_files('.jnf', sub_folder) and does_folder_contain_files('.agc', sub_folder):
            return sub_folder

    return '.'


def confirm_result_path() -> str:
    """
    This function checks if a the current result path exists and contains INF/AGC files

    If it exists, the user will be asked with a specified message to confirm that this is the folder to be used.
    If the user indicates that this is in fact not the folder that should be used, it will ask for
    the path to the correct folder.

    If the given folder does not exist, the user will be asked to supply the path to the
    folder.

    :return:
    """
    # Define a message for if the specified folder exists and contains the right files
    message_exists = 'We\'ve detected a folder we think contains your Fixation result files: {} \n' \
                     'Is this correct? '.format(_result_path)

    # Define a message for if the specified folder does not exist or doesn't contain the right files
    message_does_not_exists = 'We couldn\'t find a folder containing your Fixation result files.'

    # Check if the directory exists
    if os.path.isdir(_result_path):
        # If it exists, check if the directory contains any jnf files. If not, ask for the correct directory
        if not does_folder_contain_files('.jnf', _result_path):
            print(message_does_not_exists)
            return ask_for_path()

        # If it exists, check if the directory contains any agc files. If not, ask for the correct directory
        if not does_folder_contain_files('.agc', _result_path):
            print(message_does_not_exists)
            return ask_for_path()

        # If the directory exists and contains the right files, confirm with the user if this is the directory that
        # shoule be used. If not, ask for the right folder
        if not ask(message_exists):
            return ask_for_path()

        # Return this folder if the user confirmed it's the right one
        return _result_path
    else:
        # This directory does not exist, so ask for the right folder
        print(message_does_not_exists)
        return ask_for_path()


def does_folder_contain_files(file_extension: str, folder: str) -> bool:
    """
    This function is used to check if a folder contains files with a certain file extension

    :param file_extension: The required file extension
    :param folder: The to be checked folder
    :return: If the folder contains files with the specified file extension
    """
    # For every file in the specified directory
    for fname in os.listdir(folder):
        # If the file ends with the specified extension, return true
        if fname.lower().endswith(file_extension.lower()):
            return True

    # Return false in the base case, as we should've already returned if there was a file with the right extension
    return False


def safe_exit() -> None:
    print()
    input("Press Enter to continue...")
    exit()


def sort_jnf_file(file: str) -> List[List[str]]:
    """
    This function loads a JNF files, and sorts it's contents on the imgfile and code fields, in ascending order.
    It also ignores the column headers

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


def make_trt(lines: List[List[str]]) -> Dict[str, List[str]]:
    """
    This function calculates the missing values for a JNF file.
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


def make_act(trt: Dict[str, List[str]], agc: str) -> List[List[str]]:
    """
    This function generates a ACT file for a given AGC file and a given TRT dict.

    :param trt: The TRT dict generated by make_trt(1).
    :param agc: The location of the AGC file
    :return: A list of lists, containing strings. Which represents an ACT file.
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

            # Generate the TRT dict key
            key = line[3] + line[5]

            # Check if the TRT has an entry for this line
            if key in trt:
                # If so, combine the AGC line with the TRT line and store them in the output list
                act.append(line + trt[key])
            else:
                # If not, complement the AGC line with 5 zero's and store that in the output list
                act.append(line + ['0', '0', '0', '0', '0'])

    # Return all lines in this new ACT file
    return act


def process_jnf_agc_files() -> None:
    """
    This function opens an JNF file, sorts it and calculates a trt for it. It then uses this generated TRT to create a
    ACT file for every AGC file.
    :return: nothing!
    """
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

        # Make the ACT file for the corresponding AGC file
        print('Making ACT for {}'.format(short_filename))
        act = make_act(trt, os.path.join(_result_path, short_filename + '.agc'))

        # Add this ACT file to the list of all ACT files
        _act_files.append((short_filename, act))

        # Add the headers to the ACT file. This is done after adding the ACT to the global _act_files so that the
        # headers aren't in that variable. The script doesn't need them, but humans do in the written ACT file
        act = [["expname", "blocknr", "subjectnr", "imgfile", "pagenr", "code", "code2", "ffdur", "ffqual", "ffbck",
                "ffin", "ffout", "rpdur", "rpqual", "rpcnt", "rpsacc", "rpout", "tgdur", "tgqual", "tgcnt",
                "tgsacc", "tgout", "gdur", "gqual", "gcnt", "gsacc", "gbck", "gout", "totfixdur", "totfixcnt",
                "NumFixQualNot0", "totfixQual0dur", "totfixQual0cnt"]] + act

        # Write the ACT file to an actual file on the filesysten
        with open(os.path.join(_result_path, '{}.act'.format(short_filename)), 'w+') as f:
            f.writelines([' '.join(x) + "\r\n" for x in act])
            f.close()

        # Print a separator line for output readability
        print()


def process_combined_file_lines(lines: List[List[str]], imgfile_index: int, file: IO) -> None:
    """
    This function goes over every line in the supplied line list, processes it and writes the result to a specified
    file.


    :param lines: A list of lines to process
    :param imgfile_index: The index on which the imgfile field lives
    :param file: A file IO object to write to
    :return: /dev/null
    """
    # For every line in this ACT
    for line in lines:
        # Create a list to hold the output in while processing
        output_line = []
        for i in range(len(line)):
            # If this is the imgfile field, process it to get the cond and item fields
            if i == imgfile_index:
                # An image file is named using a naming scheme: {cond+item}.BMP.
                # cond is a string of at least 1 characters
                # item is an integer of at least 3 digits
                # We use a regex to split these into a tuple
                cond_item = re.findall(r'([a-zA-Z]+)([0-9]+)', line[i])

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
                    safe_exit()
            else:
                # Otherwise just straight add it to the output
                output_line.append(line[i])

        # Write this line to the output file
        file.write(" ".join(output_line))
        file.write("\r\n")


def combine_act_files() -> None:
    """
    This function takes all generated ACT files, and combines it into one master file.
    It also replaces the imgfile field of every ACT file with an cond and item field.

    These two fields are generated out of the imgfile field.

    :return: Nada
    """
    # open the output file
    with open(os.path.join(_result_path, 'allACTFiles.txt'), 'w+') as f:
        # Write the file headers, for clarity
        print('Writing headers')
        f.write('expname blocknr subjectnr cond item pagenr code code2 ffdur ffqual ffbck ffin ffout rpdur rpqual '
                'rpcnt rpsacc rpout tgdur tgqual tgcnt tgsacc tgout gdur gqual gcnt gsacc gbck gout totfixdur '
                'totfixcnt NumFixQualNot0 totfixQual0dur totfixQual0cnt\r\n')
        print()

        # Go over all the generated ACT files
        for k, v in _act_files:
            # Inform the user of what we are doing
            print('Adding {}'.format(k))

            # Process the lines of this file
            process_combined_file_lines(v, 3, f)

        # Inform the user that we are done creating the combined file
        print()
        print('Created allActFiles.txt')
        print()


def combine_ags_files() -> None:
    """
    This function takes all found AGS files, and combines it into one master file.
    It also replaces the imgfile field of every ACT file with an cond and item field.

    These two fields are generated out of the imgfile field.
    :return:
    """
    # Get all files ending with ags, and sort them
    files = sorted([x for x in os.listdir(_result_path) if x.lower().endswith('.ags')])

    # If there are no AGS files, display a nice message and stop
    if len(files) == 0:
        print('No AGS files found, skipping this step')
        return

    # Open the output file
    with open(os.path.join(_result_path, 'allAGSFiles.txt'), 'w+') as output_file:
        # Write the file headers, for clarity
        print('Writing headers')
        output_file.write('expname cond item timfile blocknr subjectnr pagenr samplenr samstart event fixnr fixdur '
                          'qual obtnr code code2 timcode timstart timname\r\n')

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


def main() -> None:
    """
    Main function that starts all the magic.

    It is called at the end of this file.
    :return:
    """
    # Use the global _result_path, so that all functions can use it
    global _result_path

    # Check if the folder exists and contains the required files
    _result_path = autodetect_result_path()
    _result_path = confirm_result_path()

    print()
    print('----- Processing individual JNF and AGC files -----')
    process_jnf_agc_files()

    print('----- Combining ACT files -----')
    combine_act_files()

    print('----- Combining AGS files -----')
    combine_ags_files()

    print()
    print('----- Done! -----')

    safe_exit()


# Only run if this file is executed by itself
if __name__ == '__main__':
    main()
