import argparse
import hashlib
import os
import pickle
import subprocess
import sys
import threading

from itertools import product

# import ipdb

# =====================
# Default config values
# =====================
NB_THREADS = 10

# Global variables
g_stop_all_threads = False
g_passwords_tested_by_threads = {}
g_password_found = ''


def compute_md5(file_path):
    md5_hash = hashlib.md5()

    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


# Thread function
def process_password_sublist(filename, thread_id, password_sublist):
    # TODO: necessary to put global?
    global g_stop_all_threads, g_passwords_tested_by_threads, g_password_found

    for i, password in enumerate(password_sublist):
        print(f"[thread_{thread_id}] Processing password='{password}' "
              f"[{i}/{len(password_sublist)}]")
        result_code = test_7z_archive(filename, password)
        g_passwords_tested_by_threads[thread_id].append(password)
        if result_code == 0:
            g_stop_all_threads = True
            print(f'Found the password: {password}')
            g_password_found = password
        else:
            # print('Error occurred')
            pass
        if g_stop_all_threads:
            break
    return 0


def setup_argparser():
    width = os.get_terminal_size().columns - 5
    name_input = '7z_filepath'
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
        '-t', '--threads', dest='nb_threads', metavar='NB_THREADS',
        default=NB_THREADS, type=int,
        help='Number of threads to use for processing the whole list of '
             'password combinations.')

    input_file_group = parser.add_argument_group(title='Input file')
    input_file_group.add_argument(
        'input_filename', metavar=name_input,
        help='Path of the 7z file upon which password combinations will be '
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
    numbers123_1 = ['123']
    numbers123_2 = ['123', '_123']
    numbers456_1 = ['456']
    numbers456_2 = ['456', '_456']
    numbers789_1 = ['789']
    numbers789_2 = ['789', '_789']
    numbers = list(product(numbers123_1, numbers456_2, numbers789_2)) + \
              list(product(numbers123_1, numbers789_2, numbers456_2)) + \
              list(product(numbers456_1, numbers123_2, numbers789_2)) + \
              list(product(numbers456_1, numbers789_2, numbers123_2)) + \
              list(product(numbers789_1, numbers123_2, numbers456_2)) + \
              list(product(numbers789_1, numbers456_2, numbers123_2))

    letters1 = ['abc', 'Abc', '_abc', '_Abc']
    letters2 = ['def', 'Def', '_def', '_Def']
    letters3 = ['ghi', 'Ghi', '_ghi', '_Ghi']
    letters = list(product(letters1, letters2, letters3)) + \
              list(product(letters1, letters3, letters2)) + \
              list(product(letters2, letters1, letters3)) + \
              list(product(letters2, letters3, letters1)) + \
              list(product(letters3, letters1, letters2)) + \
              list(product(letters3, letters2, letters1))
    all_combinations = []

    for num_perm in numbers:
        for letter_perm in letters:
            combined = [num+letter for num, letter in zip(num_perm, letter_perm)]
            all_combinations.append(''.join(combined))
    return all_combinations


def main():
    global g_stop_all_threads, g_passwords_tested_by_threads, g_password_found

    threads = []
    exit_code = 0
    md5_hash = None
    passwords_tested = []

    try:
        parser = setup_argparser()
        args = parser.parse_args()

        md5_hash = compute_md5(args.input_filename)
        try:
            with open(f'{md5_hash}.pkl', 'rb') as f:
                data = pickle.load(f)
                g_password_found = data['password_found']
                passwords_tested = data['passwords_tested']
        except FileNotFoundError:
            pass

        if g_password_found:
            print(f'Password was already found: {g_password_found}')
            return exit_code
        else:
            # Get all combinations minus those already tested in previous runs
            all_combinations = generate_combinations()
            nb_before = len(all_combinations)
            all_combinations = set(all_combinations) - set(passwords_tested)
            nb_after = len(all_combinations)
            if nb_before - nb_after > 0:
                print(f'{nb_before - nb_after} combinations were rejected '
                      'because they were already processed in previous runs')

            passwords_to_test = sorted(all_combinations)
            password_sublists = list(split_list(passwords_to_test, args.nb_threads))
            print(f'Number of passwords to test: {len(passwords_to_test)}')
            for i in range(args.nb_threads):
                g_passwords_tested_by_threads.setdefault(i, [])
                thread = threading.Thread(target=process_password_sublist,
                                          args=(args.input_filename, i,
                                                password_sublists[i],))
                threads.append(thread)
                thread.start()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()
    except KeyboardInterrupt:
        print('\nWarning: Program stopped!')
        exit_code = 2
    except Exception as e:
        print('Program interrupted!')
        if e:
            print(f'Error: {e}')
        exit_code = 1
    finally:
        if exit_code != 0:
            g_stop_all_threads = True
            # Wait for all threads to finish
            for thread in threads:
                thread.join()

        if md5_hash is None and exit_code == 0:
            # e.g. python script -h
            sys.exit(0)
        elif md5_hash is None:
            print('Warning: md5 hash for the given file is None!')
            return 1

        combined_passwords = passwords_tested
        nb_before = len(passwords_tested)
        for password_list in g_passwords_tested_by_threads.values():
            combined_passwords.extend(password_list)
        nb_after = len(combined_passwords)

        if combined_passwords:
            print(f'{nb_after - nb_before} passwords were tested')
            with open(f'{md5_hash}.pkl', 'wb') as f:
                data = {'password_found': g_password_found,
                        'passwords_tested': list(set(combined_passwords))}
                print('Saving file')
                pickle.dump(data, f)

    return exit_code


if __name__ == '__main__':
    # password used for testing: 123Abc456Def789Ghi
    retcode = main()
    print(f'Program exited with {retcode}')
