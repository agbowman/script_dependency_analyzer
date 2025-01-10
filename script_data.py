# scripts = [
#     {
#         "name": "ScriptA",
#         "da2_jobs": ["DA2_Job1", "DA2_Job1a", "DA2_Job1b"],
#         "ops_jobs": ["OBS_Job1", "OBS_Job1a"],
#         "calls": ["ScriptB", "ScriptC", "ScriptD"]
#     },
#     {
#         "name": "ScriptB",
#         "da2_jobs": ["DA2_Job2", "DA2_Job2a"],
#         "ops_jobs": ["OBS_Job2", "OBS_Job2a", "OBS_Job2b"],
#         "calls": ["ScriptC", "ScriptE"]
#     },
#     {
#         "name": "ScriptC",
#         "da2_jobs": ["DA2_Job3"],
#         "ops_jobs": ["OBS_Job3", "OBS_Job3a", "OBS_Job3b", "OBS_Job3c"],
#         "calls": ["ScriptF", "ScriptG"]
#     },
#     {
#         "name": "ScriptD",
#         "da2_jobs": ["DA2_Job4"],
#         "ops_jobs": ["OBS_Job4"],
#         "calls": ["ScriptE", "ScriptH"]
#     },
#     {
#         "name": "ScriptE",
#         "da2_jobs": ["DA2_Job4"],
#         "ops_jobs": ["OBS_Job4"],
#         "calls": ["ScriptF", "ScriptI"]
#     },
#     {
#         "name": "ScriptF",
#         "da2_jobs": ["DA2_Job6a", "DA2_Job6b", "DA2_Job6c", "DA2_Job6d"],
#         "ops_jobs": ["OBS_Job6"],
#         "calls": ["ScriptJ"]
#     },
#     {
#         "name": "ScriptG",
#         "da2_jobs": ["DA2_Job7"],
#         "ops_jobs": ["OBS_Job7"],
#         "calls": ["ScriptK", "ScriptL"]
#     },
#     {
#         "name": "ScriptH",
#         "da2_jobs": ["DA2_Job8"],
#         "ops_jobs": ["OBS_Job8"],
#         "calls": ["ScriptM"]
#     },
#     {
#         "name": "ScriptI",
#         "da2_jobs": ["DA2_Job9"],
#         "ops_jobs": ["OBS_Job9"],
#         "calls": ["ScriptJ", "ScriptK"]
#     },
#     {
#         "name": "ScriptJ",
#         "da2_jobs": ["DA2_Job10"],
#         "ops_jobs": ["OBS_Job10"],
#         "calls": ["ScriptN"]
#     },
#     {
#         "name": "ScriptK",
#         "da2_jobs": ["DA2_Job11"],
#         "ops_jobs": ["OBS_Job11"],
#         "calls": ["ScriptN", "ScriptO"]
#     },
#     {
#         "name": "ScriptL",
#         "da2_jobs": ["DA2_Job12"],
#         "ops_jobs": ["OBS_Job12"],
#         "calls": ["ScriptP"]
#     },
#     {
#         "name": "ScriptM",
#         "da2_jobs": ["DA2_Job13"],
#         "ops_jobs": ["OBS_Job13"],
#         "calls": ["ScriptN"]
#     },
#     {
#         "name": "ScriptN",
#         "da2_jobs": ["DA2_Job14"],
#         "ops_jobs": ["OBS_Job14"],
#         "calls": ["ScriptQ"]
#     },
#     {
#         "name": "ScriptO",
#         "da2_jobs": ["DA2_Job15"],
#         "ops_jobs": ["OBS_Job15"],
#         "calls": ["ScriptQ"]
#     },
#     {
#         "name": "ScriptP",
#         "da2_jobs": ["DA2_Job16"],
#         "ops_jobs": ["OBS_Job16"],
#         "calls": ["ScriptQ"]
#     },
#     {
#         "name": "ScriptQ",
#         "da2_jobs": ["DA2_Job17"],
#         "ops_jobs": ["OBS_Job17"],
#         "calls": []
#     },
#     # Isolated chain remains the same
#     {
#         "name": "IsolatedScript1",
#         "da2_jobs": ["DA2_JobX1"],
#         "ops_jobs": ["OBS_JobX1"],
#         "calls": ["IsolatedScript2"]
#     },
#     {
#         "name": "IsolatedScript2",
#         "da2_jobs": ["DA2_JobX2"],
#         "ops_jobs": ["OBS_JobX2"],
#         "calls": ["IsolatedScript3"]
#     },
#     {
#         "name": "IsolatedScript3",
#         "da2_jobs": ["DA2_JobX3"],
#         "ops_jobs": ["OBS_JobX3"],
#         "calls": []
#     },
#     {
#         "name": "StandaloneScript",
#         "da2_jobs": ["DA2_JobY1"],
#         "ops_jobs": ["OBS_JobY1"],
#         "calls": []
#     }
# ]



import re
from tkinter import filedialog
import tkinter as tk

def select_dat_file():
    """
    Opens a file dialog to select a .dat file
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select .dat file",
        filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
    )
    return file_path

def parse_dat_file(file_path):
    """
    Parses the .dat file and returns a list of script objects in the required format.
    """
    # Get the raw blocks from the file
    blocks = split_dat_file_to_blocks(file_path)
    scripts = []
    
    for block_name, block_content, compiled_by, source, da2, ops, last_run_by in blocks:
        # Create script object
        script = {
            "name": normalize_program_name(block_name),
            "da2_jobs": [],
            "ops_jobs": [],
            "calls": []
        }
        
        # Parse DA2 jobs
        if da2 and da2.upper() != 'N/A' and da2.upper() != 'UNKNOWN':
            script["da2_jobs"] = [job.strip() for job in da2.split(',')]
        
        # Parse OPS jobs
        if ops and ops.upper() != 'N/A' and ops.upper() != 'UNKNOWN':
            script["ops_jobs"] = [job.strip() for job in ops.split(',')]
        #
        # Parse EXECUTE statements from block content
        for line in block_content.split('\n'):
            if 'EXECUTE' in line.upper():
                called_script = line.split('EXECUTE')[-1].strip().split()[0].strip()
                called_script = called_script.replace("'", "").replace('"', '')
                if called_script:
                    script["calls"].append(normalize_program_name(called_script))
        
        scripts.append(script)
    
    return scripts

def get_scripts(dat_file_path=None):
    """
    Returns the scripts data from the .dat file.
    If no file path is provided, prompts user to select one.
    """

    if not dat_file_path:
        dat_file_path = select_dat_file()
        if not dat_file_path:  # User cancelled file selection
            return []
    
    try:
        scripts = parse_dat_file(dat_file_path)
        return clean_scripts(scripts)
    except Exception as e:
        print(f"Error processing .dat file: {e}")
        return []

def clean_scripts(scripts_list):
    """
    Cleans the scripts data by removing duplicates and invalid entries.
    """
    # Remove duplicates while preserving order
    seen = set()
    cleaned_scripts = []
    
    for script in scripts_list:
        if script["name"] and script["name"] not in seen:
            seen.add(script["name"])
            # Remove duplicates from calls list while preserving order
            script["calls"] = list(dict.fromkeys(script["calls"]))
            cleaned_scripts.append(script)
    
    return cleaned_scripts

def split_dat_file_to_blocks(input_file_path, skip_compiler_prefix=None, skip_source_prefix=None):
    """
    Reads a .dat file line by line and groups lines into blocks based on starting with
    'CREATE PROGRAM' or 'DROP PROGRAM' and ending with 'END GO'.
    Captures 'Compiled By' and 'Source' information for each block.
    Optionally skips blocks compiled by compilers or sourced from sources starting with specified prefixes.
    Returns a list of tuples, each containing a block's name, its content, compiled by, and source.
    """
    blocks = []
    current_block = []
    block_name = ""
    compiled_by = ""
    source = ""
    da2 = "" 
    ops = "" 
    last_run_by = ""
    in_block = False

    try:
        with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                # Capture compiled by and source information
                if '<<COMPILED_BY:' in line:
                    compiled_by_parts = line.strip().split('<<COMPILED_BY: ')
                    if len(compiled_by_parts) > 1:
                        compiled_by = compiled_by_parts[1].rstrip(' >>')
                    else:
                        compiled_by = "Unknown"
                if '<<SOURCE:' in line:
                    source_parts = line.strip().split('<<SOURCE: ')
                    if len(source_parts) > 1:
                        source = source_parts[1].rstrip(' >>')
                    else:
                        source = "Unknown"
                if '<<DA2:' in line:
                    da2_parts = line.strip().split('<<DA2: ')
                    da2 = da2_parts[1].rstrip(' >>') if len(da2_parts) > 1 else "Unknown"
                if '<<OPS:' in line:
                    ops_parts = line.strip().split('<<OPS: ')
                    ops = ops_parts[1].rstrip(' >>') if len(ops_parts) > 1 else "Unknown"
                if '<<LAST_RUN_BY:' in line:
                    last_run_by_parts = line.strip().split('<<LAST_RUN_BY: ')
                    last_run_by = last_run_by_parts[1].rstrip(' >>') if len(last_run_by_parts) > 1 else "Unknown"


                # Check if the line starts a block
                if 'CREATE PROGRAM' in line or 'DROP PROGRAM' in line:
                    in_block = True
                    block_name = line.split()[2]  # Assuming the name is the third word
                    current_block = [line]  # Start a new block with the current line
                elif 'END GO' in line and in_block:
                    current_block.append(line)
                    if not ((skip_compiler_prefix and compiled_by.lower().startswith(skip_compiler_prefix)) or
                            (skip_source_prefix and skip_source_prefix in source.lower())):
                        # Include da2 and ops in the saved block
                        blocks.append((block_name, '\n'.join(current_block), compiled_by, source, da2, ops, last_run_by))
                    in_block = False
                    compiled_by, source, da2, ops, last_run_by = "", "", "", "", ""  # Reset all for next block
                elif in_block:
                    current_block.append(line)


    except IOError as e:
        print(f"Error reading file {input_file_path}: {e}")

    return blocks

def normalize_program_name(program_name):
    """
    Normalize program names to ensure consistent comparison, 
    especially with regard to the ':dba' suffix.
    """
    return program_name.split(":")[0].strip()  # Strip off any suffix like ':dba' and any surrounding whitespace