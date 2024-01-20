import argparse
import hashlib
import os
import pickle
import subprocess
import threading

from itertools import permutations, product

import ipdb

# =====================
# Default config values
# =====================
NB_THREADS = 10

# Global variables
g_stop_all_threads = False
g_passwords_tested_by_threads = {}


def compute_md5(file_path):
    md5_hash = hashlib.md5()

    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


# Thread function
def process_password_sublist(filename, thread_id, password_sublist):
    # TODO: necessary to put global?
    global g_stop_threads, g_passwords_tested
    
    for i, password in enumerate(password_sublist):
        print(f"[thread_{thread_id}] Processing password='{password}' "
              f"[{i}/{len(password_sublist)}]")
        result_code = test_7z_archive(filename, password)
        if result_code == 0:
            pass
        else:
            # print('Error occurred')
            pass
        g_passwords_tested_by_threads[thread_id].append(password)
        if g_stop_all_threads:
            break
    return 0


def setup_argparser():
    width = os.get_terminal_size().columns - 5
    name_input = 'input_7z_file'
    usage_msg = f'%(prog)s [OPTIONS] {{{name_input}}}'
    desc_msg = 'Script that generates combinations of passwords according to ' \
               'a predefined pattern and tests them for a 7z file.\n\n' \
               'For more info, see https://github.com/raul23/7z-Password-Tester'
    parser = argparse.ArgumentParser(
        description="",
        usage=f'{usage_msg}\n\n{desc_msg}',
        add_help=False,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=50, width=width))

    parser_opt_group = parser.add_argument_group(title='Optional arguments')
    parser_opt_group.add_argument('-h', '--help', action='help',
                                  help='Show this help message and exit.')
    parser_opt_group.add_argument(
        '-t', '--threads', dest='nb_threads', metavar='THREADS', default=NB_THREADS,
        help='')

    input_file_group = parser.add_argument_group(title='Input file')
    input_file_group.add_argument(
        'input', dest='input_filename',
        help='Path of the 7z file for which password combinations will be '
             'tested.')

    return parser


def split_list(input_list, num_sublists):
    avg = len(input_list) // num_sublists
    remainder = len(input_list) % num_sublists
    start = 0
    end = 0

    for i in range(num_sublists):
        start = end
        end = start + avg + (1 if i < remainder else 0)
        yield input_list[start:end]


def test_7z_archive(filename, password):
    command = f'7z t {filename} -p"{password}"'

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        output = result.stdout.strip()
        error_output = result.stderr.strip()

        # print(f'output={output}')
        # print(f'error_output={error_output}')

        # Check the exit code
        if result.returncode == 0:
            # Check if the output contains the "Everything is Ok" message
            if 'Everything is Ok' in output:
                return 0  # Success
            else:
                return 1  # Error (unexpected output)
        elif 'Wrong password?' in error_output:
            return 1  # Error (wrong password)
        else:
            return 1  # Other error

    except subprocess.CalledProcessError as e:
        # Command execution failed
        return 1  # Error


def generate_combinations():
    numbers = ['123', '456', '789']
    letters1 = ['abc', 'Abc']
    letters2 = ['def', 'Def']
    letters3 = ['ghi', 'Ghi']
    letters = list(product(letters1, letters2, letters3)) + list(product(letters1, letters3, letters2)) + \
              list(product(letters2, letters1, letters3)) + list(product(letters2, letters3, letters1)) + \
              list(product(letters3, letters1, letters2)) + list(product(letters3, letters2, letters1))
    all_combinations = []

    for num_perm in permutations(numbers):
        for letter_perm in letters:
            for underscore in ['', '_']:
                combined = []
                for num, letter in zip(num_perm, letter_perm):
                    combined.append(num + underscore + letter)
                all_combinations.append(''.join(combined))
                all_combinations.append('_'.join(combined))
    return all_combinations


def main():
    global g_stop_threads
    
    threads = []
    exit_code = 0
    md5_hash = None

    try:
        parser = setup_argparser()
        args = parser.parse_args()
        
        ipdb.set_trace()
        
        md5_hash = compute_md5(args.input_filename)
        with open(f'{md5_hash}.pkl', 'rb') as f:
            combined_passwords = pickle.load(f)

        # Get all combinations
        all_combinations = generate_combinations() + combined_passwords

        passwords_to_test = list(set(all_combinations))
        password_sublists = list(split_list(passwords_to_test, args.nb_threads))
        print(f'Number of passwords = {len(passwords)}')
        for i in range(args.nb_threads):
            g_passwords_tested.setdefault(i, [])
            thread = threading.Thread(target=process_password_sublist, args=(args.input_filename, i, password_sublists[i],))
            threads.append(thread)
            thread.start()
    except KeyboardInterrupt:
        print('\nProgram stopped!')
        exit_code = 2
    except Exception as e:
        print('Program interrupted!')
        print(e)
        exit_code = 1
    else:
        g_stop_all_threads = True
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        ipdb.set_trace()
        
        combined_passwords = []
        for password_list in g_passwords_tested.values():
            combined_passwords.extend(password_list)

        # TODO: test that `md5_hash` is not None
        with open(f'{md5_hash}.pkl', 'wb') as f:
            pickle.dump(list(set(combined_passwords)), f)

    return exit_code


if __name__ == '__main__':
    retcode = main()
    print(f'Program exited with {retcode}')
