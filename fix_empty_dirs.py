import argparse
import os

from __lib.base import stdout, mark_dry_or_production_run, warn, remove_dir, \
    get_env_var, yellow, assert_non_empty_dir
from __lib.functions import get_default_root


def main():
    program = 'fix_empty_dirs'
    description = '''
    Deletes empty dirs'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-p', '--production', help='Enable production run',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable verbosity',
                        action='store_true')
    parser.add_argument('-x', '--path', type=str, help='Root path')
    args = parser.parse_args()
    dryrun = not args.production or get_env_var('DRYRUN')
    verbose = args.verbose or get_env_var('VERBOSE')
    root = args.path or get_default_root()

    assert_non_empty_dir(root)
    mark_dry_or_production_run(dryrun)
    if dryrun:
        warn('Dryrun does not check nested empty dirs!')

    cnt = 0
    done = False
    dryrun_deleted_dirs = []
    while not done:
        cnt_start = cnt
        for dir_name, sub_dirs, file_names in os.walk(root):
            if verbose:
                yellow('Checking', dir_name)
            if not sub_dirs and not file_names:
                if dryrun:
                    if dir_name in dryrun_deleted_dirs:
                        continue
                    else:
                        dryrun_deleted_dirs.append(dir_name)
                remove_dir(dir_name, dryrun=dryrun, verbose=verbose)
                cnt += 1
        done = cnt == cnt_start

    if cnt:
        stdout()
    stdout(cnt, 'dirs deleted')


if __name__ == "__main__":
    main()
