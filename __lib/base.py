from __future__ import print_function

import copy
from datetime import datetime
import json
import os
import pprint
import readline
import subprocess
import sys
import time
import traceback

HOME_ROOT = None
HOME = None


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    INFO = OKYELLOW
    WARNING = INFO
    FAIL = '\033[91m'
    ALERT = FAIL
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


IS_PY3 = sys.version_info >= (3, 0)
POST_PY_3_3 = sys.version_info[:2] >= (3, 3)


# ----------------------------------------------------------------------------#
# UTILS
# --------------------------------------------------------------------------- #

def env_error(msg, *args):
    raise EnvironmentError((msg % tuple(args)) if args else msg)


def exc_error(e, msg=None):
    fatal_error(msg, exc=e)


def assert_c(c, msg=None):
    if not c:
        fatal_error(msg if msg else 'False assert')


def is_py2():
    return sys.version_info < (3, 0)


def is_py3():
    return not is_py2()


def assert_py3():
    assert_c(is_py3(), 'python3 is required')


def get_env_var(name, default=None, required=False):
    assert default is None or not required  # don't set default and
    #                                         required at same time
    try:
        if os.environ[name] is not None:
            return os.environ[name]
        else:
            return default
    except KeyError:
        if not required:
            return default
        else:
            env_error('Please set %s. Aborting.', name)


def get_env_bool(name, default=False):
    return (str(get_env_var(name, default)).lower()
            in ['t', 'true', 'yes', 'y', '1'])


def debug_enabled():
    return bool(get_env_var('DEBUG'))


def is_unix():
    return '/usr/bin' in get_env_var('PATH')


def is_cygwin():
    return '/cygdrive/c/WINDOWS' in get_env_var('PATH')


def is_dos_windows():
    return 'C:\\WINDOWS' in get_env_var('PATH')


def is_windows():
    return is_cygwin() or is_dos_windows()


def get_home_root():
    global HOME_ROOT
    if not HOME_ROOT:
        if is_cygwin():
            HOME_ROOT = get_shell_command_output(['cygpath', '-H'])
            if not isinstance(HOME_ROOT, str):
                HOME_ROOT = ''.join(map(chr, HOME_ROOT))
            HOME_ROOT = HOME_ROOT[:-1]  # strip the newline
        else:
            HOME_ROOT = '/home'
    return HOME_ROOT


def get_home():
    global HOME
    if not HOME:
        user = os.getenv('USER')
        HOME = '{}/{}'.format(get_home_root(), user)
    return HOME


def u(x):
    if is_py2():
        try:
            return unicode(x)
        except UnicodeError as e:
            exc_error(e, 'Safer is to re-run as Py3')

    return str(x)


def assure_endswith(s, tail):
    return s if s.endswith(tail) else (s + tail)


def assure_not_endswith(s, tail):
    return s[:-len(tail)] if s.endswith(tail) else s


def get_shell_command_output(shell_cmd):
    out, _ = subprocess.Popen(shell_cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT).communicate()
    return out


def now(split_a='_', split_b=':'):
    return datetime.now().strftime('%Y' + split_b + '%m' + split_b + '%d' +
                                   split_a +
                                   '%H' + split_b + '%M' + split_b + '%S')


def a_else_b(a, b):
    return a if a else b


# ----------------------------------------------------------------------------#
# OUTPUT
# --------------------------------------------------------------------------- #

def stdout(*args, **kwargs):
    if POST_PY_3_3:
        kwargs['flush'] = True
    print(*args, **kwargs)
    if not POST_PY_3_3:
        sys.stdout.flush()


def f_stdout(msg=None, *args, **kwargs):
    stdout(msg.format(*args), **kwargs)


def start_green():
    stdout(ConsoleColors.OKGREEN, end='')


def start_yellow():
    stdout(ConsoleColors.OKYELLOW, end='')


def start_blue():
    stdout(ConsoleColors.OKBLUE, end='')


def start_cyan():
    stdout(ConsoleColors.OKCYAN, end='')


def start_red():
    stdout(ConsoleColors.ALERT, end='')


def start_bold():
    stdout(ConsoleColors.BOLD, end='')


def end_color():
    stdout(ConsoleColors.ENDC, end='')


def green(*args, **kwargs):
    start_green()
    stdout(*args, **kwargs)
    end_color()


def f_green(msg, *args, **kwargs):
    start_green()
    f_stdout(msg, *args, **kwargs)
    end_color()


def yellow(*args, **kwargs):
    start_yellow()
    stdout(*args, **kwargs)
    end_color()


def f_yellow(msg, *args, **kwargs):
    start_yellow()
    f_stdout(msg, *args, **kwargs)
    end_color()


def blue(*args, **kwargs):
    start_blue()
    stdout(*args, **kwargs)
    end_color()


def f_blue(msg, *args, **kwargs):
    start_blue()
    f_stdout(msg, *args, **kwargs)
    end_color()


def cyan(*args, **kwargs):
    start_cyan()
    stdout(*args, **kwargs)
    end_color()


def f_cyan(msg, *args, **kwargs):
    start_cyan()
    f_stdout(msg, *args, **kwargs)
    end_color()


def red(*args, **kwargs):
    start_red()
    stdout(*args, **kwargs)
    end_color()


def f_red(msg, *args, **kwargs):
    start_red()
    f_stdout(msg, *args, **kwargs)
    end_color()


def bold(*args, **kwargs):
    start_bold()
    stdout(*args, **kwargs)
    end_color()


def f_bold(msg, *args, **kwargs):
    start_bold()
    f_stdout(msg, *args, **kwargs)
    end_color()


def info(*args, **kwargs):
    yellow(*args, **kwargs)


def warn(*args, **kwargs):
    yellow('WARN:', *args, **kwargs)


def alert(*args, **kwargs):
    red('ALERT:', *args, **kwargs)


def end(exit_code=0, exc=None, silent=True, debug=False):
    if debug:
        if exc:
            raise exc
        else:
            assert False
    elif exc and not silent:
        stdout('Got', str(exc))
    sys.exit(exit_code)


def error(*args, **kwargs):
    fatal = kwargs.pop('fatal', False)
    exc = kwargs.pop('exc', None)
    debug = kwargs.pop('debug', False)
    if 'end' not in kwargs:
        kwargs['end'] = '. Exiting.\n' if fatal else '.\n'
    red('ERROR:', *args, **kwargs)
    if fatal:
        stdout()
        end(1, exc, debug=debug)


def fatal_error(*args, **kwargs):
    kwargs['fatal'] = True
    error(*args, **kwargs)


def f_traceback(f=stdout):
    f(traceback.format_exc())


# ----------------------------------------------------------------------------#
# INPUT
# --------------------------------------------------------------------------- #

def prefilled_input(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt) if IS_PY3 else raw_input(prompt)
    finally:
        readline.set_startup_hook()


def string_input(value_name, termination=':', default=None,
                 allow_empty=False, prefill=''):
    while True:
        if default is not None:
            prompt = '{}{} [{}] '.format(value_name, termination, default)
        else:
            prompt = '{}{} '.format(value_name, termination)

        value = prefilled_input(prompt, prefill=prefill)

        if default is not None and not value:
            value = default
        f_stdout('\r', end='')  # carriage return (CR)

        # empty check
        if allow_empty or value is not None:
            break
        else:
            stdout('Empty is now allowed.')

    return value


def numerical_input(value_name, min_value, max_value, default=True,
                    default_value=None):
    def_value = ((min_value if not default_value else default_value) if default
                 else None)
    while True:
        try:
            value = int(string_input(value_name, default=def_value))
            if min_value <= value <= max_value:
                break
        except (ValueError, NameError):
            pass
        stdout('Please pick a number between {} and {}'.format(
            min_value, max_value))
    return value


def shell_input(value_name, shell_var, default=None):
    value = os.environ.get(shell_var)
    return value if value else string_input(
        value_name + ' (' + shell_var + ' is undefined)', default=default)


def boolean_input(question, default=True):
    resp = string_input(question, '? (Y/n)' if default else '? (y/N)',
                        allow_empty=True).lower()
    return 'y' in resp if resp else default


def boolean_error(question, default=True):
    return boolean_input('ERROR: ' + question, default)


def choice_input_list(header=None, choices=None, add_none=False,
                      zero_based_display=False,
                      zero_based_return=False,
                      default=True, default_last=False, skip_line=True):
    input_list = choices
    if not input_list:
        return None

    display_offset = 0 if zero_based_display else 1
    return_offset = 0 if zero_based_display and zero_based_return \
        else 0 if not zero_based_display and not zero_based_return \
        else -1 if not zero_based_display and zero_based_return \
        else 1

    if add_none:
        input_list = copy.deepcopy(choices)
        input_list.append('None of the above.')

    if skip_line:
        stdout()
    if header:
        f_stdout('[ {} ]', header)
    for count, choice in enumerate(input_list):
        f_stdout('[{}] : {}', count + display_offset, choice)

    min_val = display_offset
    max_val = len(input_list) - 1 + display_offset

    return numerical_input(
        'Make a choice', min_val, max_val, default,
        max_val if default and default_last else None) + return_offset


def choice_input(*args):
    return choice_input_list(args)


# ----------------------------------------------------------------------------#
# DRY RUN
# --------------------------------------------------------------------------- #

def mark_dry_or_production_run(dryrun):
    if dryrun:
        green('*** DRY-RUN is ON ***')
    else:
        red('*** THIS IS A PRODUCTION RUN! ***')
        red('    !Abort NOW if unintended! ', end='')
        for i in range(3):
            red('.', end='')
            time.sleep(1)
        red()


def path(p):
    for c in ("'", '"', '(', ')', ' ', '&', '$', '*', ':', '?', '|'):
        p = p.replace(c, "\\" + c)
    return p


def path_exists(p):
    return os.path.exists(p)


def assert_path_exists(p):
    assert_c(os.path.exists(p), p + ' does not exist')


def is_file(p):
    return os.path.isfile(p)


def is_dir(p):
    return os.path.isdir(p)


def is_non_empty_dir(p):
    return is_dir(p) and len(os.listdir(p)) > 0


def assert_non_empty_dir(p):
    assert_c(is_non_empty_dir(p), p + ' is empty')


def split_file_extension(p):
    filename, file_extension = os.path.splitext(p)
    return filename, file_extension


def print_path(file_path, dos_format=False, windows_format=False,
               write_to_file=None, append_to_file=None):
    file_path = file_path.replace('$', '\\$')  # mind, no not use path()
    file_path = file_path.replace("'", "\'")

    if write_to_file:
        if dos_format or windows_format:
            os.system('rm -f ' + write_to_file)
            if dos_format:
                os.system('cygpath -d "' + file_path + '" >> ' + write_to_file)
            else:
                os.system('cygpath -w "' + file_path + '" >> ' + write_to_file)
        else:
            with open(write_to_file, 'w') as fh:
                fh.write('%s\n' % file_path)

    elif append_to_file:
        if dos_format:
            os.system('cygpath -d "' + file_path + '" >> ' + append_to_file)
        elif windows_format:
            os.system('cygpath -w "' + file_path + '" >> ' + append_to_file)
        else:
            with open(append_to_file, 'a') as fh:
                fh.write('%s\n' % file_path)

    else:
        if dos_format:
            os.system('cygpath -d "' + file_path + '"')
        elif windows_format:
            os.system('cygpath -w "' + file_path + '"')
        else:
            stdout(file_path)


def print_paths(file_paths, dos_format=False, windows_format=False,
                write_to_file=None):
    def _fix_up_f(_f):
        _f = _f.replace('$', '\\$')  # mind, no not use path()
        _f = _f.replace("'", "\'")
        return _f

    def _os_write(_f):
        _f = _fix_up_f(_f)
        if dos_format:
            os.system('cygpath -d "' + _f + '" >> ' + write_to_file)
        elif windows_format or write_to_file:
            os.system('cygpath -w "' + _f + '" >> ' + write_to_file)
        else:
            print(f)

    if write_to_file:
        if dos_format or windows_format:
            os.system('rm -f ' + write_to_file)
            for f in file_paths:
                _os_write(f)
        else:
            with open(write_to_file, 'w') as fh:
                for f in file_paths:
                    fh.write('%s\n' % f)
    else:
        for f in file_paths:
            _os_write(f)


def new_file(f, content=None):
    with open(f, 'w') as fh:
        fh.write(assure_endswith(content, '\n') if content else '')


def get_timestamp():
    return time.time()


def get_file_timestamp(f):  # comparable with get_timestamp defined above
    return os.path.getmtime(f)


def dump_json(j, pp=False, to_file=None):
    if pp:
        if to_file:
            raise NotImplementedError
        pprint.pprint(j)  # , indent=4
    else:
        if to_file:
            with open(to_file, 'w') as fp:
                json.dump(j, fp)
                fp.write("\n")
        else:
            json.dump(j, sys.stdout)
            stdout()


def read_json(f):
    with open(f) as fp:
        return json.load(fp)


def unsafe_delete_file(rooted_file_name,
                       dryrun=True, verbose=False, silent=False, debug=False):
    dry = '(dryrun) ' if dryrun else ''

    if debug:
        cyan('unsafe_delete_file', rooted_file_name, dryrun, verbose, silent)

    def remove(f):
        try:
            if not silent:
                stdout(dry + 'rm', f)
            if not dryrun:
                os.remove(f)
        except UnicodeEncodeError as e:
            exc_error(e, 'Safer is to re-run as Py3')

    if verbose:
        green(dry + 'Remove', rooted_file_name)
    remove(rooted_file_name)


def unsafe_delete_dir(rooted_dir_name,
                      dryrun=True, verbose=False, silent=False, debug=False):
    dry = '(dryrun) ' if dryrun else ''

    if debug:
        cyan('unsafe_delete_dir', rooted_dir_name, dryrun, verbose, silent)

    def rmdir(d):
        try:
            if not silent:
                stdout(dry + 'rmdir', d)
            if not dryrun:
                os.rmdir(d)
        except UnicodeEncodeError as e:
            exc_error(e, 'Safer is to re-run as Py3')

    if verbose:
        green(dry + 'Remove', rooted_dir_name)
    rmdir(rooted_dir_name)


def unsafe_delete(x, dryrun=True, verbose=False, silent=False, debug=False):
    if is_dir(x):
        unsafe_delete_dir(x, dryrun, verbose, silent, debug)
    else:
        unsafe_delete_file(x, dryrun, verbose, silent, debug)


def remove_file(root_dir, file_name, safe_remove=True,
                dryrun=True, verbose=False, silent=False, debug=False):
    if debug:
        cyan('remove_file', root_dir, file_name, safe_remove, dryrun, verbose,
             silent)
    if safe_remove:
        rename_file(root_dir, file_name, file_name + '.deleted',
                    safe_rename=True, dryrun=dryrun,
                    verbose=verbose, silent=silent, debug=debug)
    unsafe_delete_file(root_dir + '/' + file_name, dryrun, verbose, silent)


def remove_dir(rooted_dir, safe_remove=True,
               dryrun=True, verbose=False, silent=False, debug=False):
    if debug:
        cyan('remove_dir', rooted_dir, safe_remove, dryrun, verbose, silent)
    if safe_remove and not dryrun:
        if len(os.listdir(rooted_dir)) != 0:
            fatal_error('Can \'t delete dir', rooted_dir,
                        'as it is not empty', debug=debug)
    unsafe_delete_dir(rooted_dir, dryrun, verbose, silent)


def _manip(verb, cmd, x1, x2, dryrun=True, safe=True,
           fatal_if_exists=False, add_suffix_if_exists=False,
           delete_if_exists=False, verbose=False, silent=False, debug=False):
    dry = '(dryrun) ' if dryrun else ''

    if debug:
        cyan('_manip', verb, cmd, x1, x2, dryrun, safe,
             fatal_if_exists, add_suffix_if_exists, delete_if_exists,
             verbose, silent)

    def manip(_x1, _x2):
        try:
            exec_cmd = '{} {} {}'.format(cmd, path(_x1), path(_x2))
            if not silent:
                stdout(dry + exec_cmd)
            if not dryrun:
                os.system(exec_cmd)
        except UnicodeEncodeError as e:
            exc_error(e, 'Safer is to re-run as Py3')

    if is_windows() and x1.lower() == x2.lower():
        _manip(verb, cmd, x1, x2 + '.tmp',
               dryrun, safe,
               fatal_if_exists, add_suffix_if_exists, delete_if_exists,
               verbose, silent)
        _manip(verb, cmd, x2 + '.tmp', x2,
               dryrun, False if dryrun else safe,
               fatal_if_exists, add_suffix_if_exists, delete_if_exists,
               verbose, silent)

    elif safe and path_exists(x2):
        if add_suffix_if_exists:
            x2_base, x2_ext = split_file_extension(x2)
            for i in range(1, 99):
                n = x2_base + ' (' + str(i) + ')'
                if not path_exists(n + x2_ext):
                    x2 = n + x2_ext
                    if not silent:
                        warn('Move destination changed to', x2)
                    break
        elif fatal_if_exists and not dryrun:
            fatal_error('Can\'t', verb, x1, 'to', x2, ': path exists',
                        debug=debug)

        elif delete_if_exists:
            warn('Won\'t', verb, x1, 'to', x2, ': path exists: '
                                               'deleting original')
            unsafe_delete(x2, dryrun, verbose, silent, debug)
        else:
            error('Can\'t', verb, x1, 'to', x2, ': path exists')
            return

    elif verbose:
        green(dry + verb, x1, '->', x2)

    manip(x1, x2)


def _move(x1, x2, dryrun=True, safe=True, verb='mv',
          fatal_if_exists=False, add_suffix_if_exists=False,
          delete_if_exists=False, verbose=False, silent=False, debug=False):
    if debug:
        cyan('_move', x1, x2, dryrun, safe, verb,
             fatal_if_exists, add_suffix_if_exists, delete_if_exists,
             verbose, silent)
    _manip(verb, 'mv', x1, x2, dryrun, safe,
           fatal_if_exists, add_suffix_if_exists, delete_if_exists,
           verbose, silent)


def _copy(f1, f2, dryrun=True, safe=True, verb='cp',
          fatal_if_exists=False, add_suffix_if_exists=False,
          verbose=False, silent=False, debug=False):
    if debug:
        cyan('_copy', f1, f2, dryrun, safe, verb,
             fatal_if_exists, add_suffix_if_exists, verbose, silent)
    _manip(verb, 'cp', f1, f2, dryrun, safe,
           fatal_if_exists, add_suffix_if_exists, False,
           verbose, silent)


def duplicate_file(root_dir, old_file_name, new_file_name, safe_rename=True,
                   fatal_if_exists=False, add_suffix_if_exists=True,
                   dryrun=True, verbose=False, silent=False, debug=False):
    from_rooted = root_dir + '/' + old_file_name
    to_rooted = root_dir + '/' + new_file_name

    _copy(from_rooted, to_rooted, dryrun, safe_rename, 'duplicate',
          fatal_if_exists, add_suffix_if_exists,
          verbose=verbose, silent=silent, debug=debug)


def rename_file(root_dir, old_file_name, new_file_name, safe_rename=True,
                fatal_if_exists=False, add_suffix_if_exists=True,
                dryrun=True, verbose=False, silent=False, debug=False):
    from_rooted = root_dir + '/' + old_file_name
    to_rooted = root_dir + '/' + new_file_name

    if debug:
        cyan('rename_file', root_dir, old_file_name, new_file_name,
             safe_rename, fatal_if_exists, add_suffix_if_exists, dryrun,
             verbose, silent)

    _move(from_rooted, to_rooted, dryrun, safe_rename, 'rename',
          fatal_if_exists, add_suffix_if_exists, delete_if_exists=False,
          verbose=verbose, silent=silent, debug=debug)


def rename_dir(root, old_dir_name, new_dir_name, safe_rename=True,
               fatal_if_exists=False, add_suffix_if_exists=True,
               dryrun=True, verbose=False, silent=False, debug=False):
    from_rooted = root + '/' + old_dir_name
    to_rooted = root + '/' + new_dir_name

    if debug:
        cyan('rename_dir', root, old_dir_name, new_dir_name, safe_rename,
             fatal_if_exists, add_suffix_if_exists, dryrun,
             verbose, silent)

    _move(from_rooted, to_rooted, dryrun, safe_rename, 'rename',
          fatal_if_exists, add_suffix_if_exists, delete_if_exists=False,
          verbose=verbose, silent=silent)


def merge_dir(from_rooted, to_rooted, safe_merge=True,
              fatal_if_exists=False, add_suffix_if_exists=False,
              delete_if_exists=False, merge_subdirs=True,
              dryrun=True, verbose=False, silent=False, debug=False):
    if debug:
        cyan('merge_dir', from_rooted, to_rooted, safe_merge,
             fatal_if_exists, add_suffix_if_exists, merge_subdirs, dryrun,
             verbose, silent)

    for x in os.listdir(from_rooted):
        if is_dir(from_rooted + '/' + x):
            move_dir(from_rooted + '/' + x,
                     to_rooted + '/' + x,
                     safe_move=safe_merge,
                     fatal_if_exists=fatal_if_exists,
                     add_suffix_if_exists=add_suffix_if_exists,
                     delete_if_exists=delete_if_exists,
                     merge_if_exists=merge_subdirs,
                     dryrun=dryrun, verbose=verbose, silent=silent,
                     debug=debug)
        else:
            move_file(from_rooted + '/' + x,
                      to_rooted + '/' + x,
                      safe_move=safe_merge, fatal_if_exists=fatal_if_exists,
                      add_suffix_if_exists=add_suffix_if_exists,
                      delete_if_exists=delete_if_exists,
                      dryrun=dryrun, verbose=verbose, silent=silent,
                      debug=debug)
    remove_dir(from_rooted, safe_remove=True, dryrun=dryrun, verbose=verbose,
               silent=silent, debug=debug)


def make_dir(root, dir_name, conditionally=False, dryrun=True, verbose=False,
             silent=False, debug=False):
    dry = '(dryrun) ' if dryrun else ''

    if debug:
        cyan('make_dir', dir_name, conditionally, dryrun, verbose, silent)

    def mkdir(d):
        try:
            if not silent:
                stdout(dry + 'mkdir', d)
            if not dryrun:
                os.makedirs(d, exist_ok=True)
        except UnicodeEncodeError as e:
            exc_error(e, 'Safer is to re-run as Py3')

    to_dir = root + '/' + dir_name

    if not conditionally or not path_exists(to_dir):
        if verbose:
            green(dry + 'mkdir', to_dir)

        mkdir(to_dir)


def _prep_files(root, dir_name, file_name,
                to_dir_name=None, to_file_name=None):
    from_unrooted = (dir_name + '/' + file_name) if dir_name else file_name
    from_rooted = (root + '/' + from_unrooted) if root else from_unrooted

    if to_dir_name:
        if to_file_name:
            to_short = '.../' + to_dir_name + '/' + to_file_name
            to_unrooted = to_dir_name + '/' + to_file_name
        else:
            to_short = '.../' + to_dir_name
            to_unrooted = to_dir_name

        to_rooted = (root + '/' + to_unrooted) if root else to_unrooted

    elif to_file_name:
        to_short = to_file_name
        to_unrooted = ((dir_name + '/' + to_file_name) if dir_name
                       else to_file_name)
        to_rooted = (root + '/' + to_unrooted) if root else to_unrooted

    else:
        to_rooted = to_short = None  # keep pycharm happy
        fatal_error('Need to_dir_name or to_file_name')

    return from_unrooted, from_rooted, to_rooted, to_short


def move_dir(from_rooted,
             to_rooted,  # hold the target dir name as well!
             safe_move=True, add_suffix_if_exists=True,
             fatal_if_exists=False, merge_if_exists=False,
             delete_if_exists=False, dryrun=True,
             verbose=False, silent=False, debug=False):
    if debug:
        cyan('move_dir', from_rooted, to_rooted, safe_move,
             add_suffix_if_exists, fatal_if_exists, merge_if_exists,
             delete_if_exists, dryrun, verbose, silent)

    if safe_move and path_exists(to_rooted):
        if merge_if_exists:
            merge_dir(from_rooted, to_rooted, safe_merge=safe_move,
                      fatal_if_exists=fatal_if_exists,
                      add_suffix_if_exists=add_suffix_if_exists,
                      delete_if_exists=delete_if_exists,
                      dryrun=dryrun, verbose=verbose, silent=silent,
                      debug=debug)
        elif fatal_if_exists:
            fatal_error('Can\'t move', from_rooted, 'to', to_rooted,
                        ': path exists')
        else:
            error('Can\'t move', from_rooted, 'to', to_rooted,
                  ': path exists')
    else:
        _move(from_rooted, to_rooted, dryrun=dryrun, safe=False,
              verbose=verbose, silent=silent)


def move_file(from_rooted,
              to_rooted,  # hold the target file name as well!
              safe_move=True, add_suffix_if_exists=True,
              fatal_if_exists=False, delete_if_exists=False, dryrun=True,
              verbose=False, silent=False, debug=False):
    if debug:
        cyan('move_file', from_rooted, to_rooted, safe_move,
             add_suffix_if_exists, fatal_if_exists, delete_if_exists,
             dryrun, verbose, silent)

    _move(from_rooted, to_rooted, dryrun=dryrun, safe=safe_move,
          fatal_if_exists=fatal_if_exists,
          add_suffix_if_exists=add_suffix_if_exists,
          delete_if_exists=delete_if_exists,
          verbose=verbose, silent=silent)


def copy_file(from_rooted,
              to_rooted,  # hold the target file name as well!
              safe_copy=True, add_suffix_if_exists=True,
              fatal_if_exists=False, dryrun=True, verbose=False, silent=False,
              debug=False):
    if debug:
        cyan('copy_file', from_rooted, to_rooted, safe_copy,
             add_suffix_if_exists, fatal_if_exists, dryrun, verbose, silent)

    _copy(from_rooted, to_rooted, dryrun=dryrun, safe=safe_copy,
          fatal_if_exists=fatal_if_exists,
          add_suffix_if_exists=add_suffix_if_exists,
          verbose=verbose, silent=silent)


def filter_by(n, n_filter):
    n = n.lower()
    n_filter = n_filter.lower()

    if n_filter.endswith('*'):
        n_filter = n_filter[:-1]
        if n.startswith(n_filter):
            return True
    elif n_filter.endswith('-'):
        n_filter = n_filter[:-1]
        if n >= n_filter:
            return True
    elif n == n_filter:
        return True
    return False


silent_mode = False


def set_silent_mode(flag=True):
    global silent_mode
    silent_mode = flag


def is_silent_mode(thru_silent_mode=False):
    global silent_mode
    return silent_mode and not thru_silent_mode


def pop_first(a_list):
    return a_list[0] if len(a_list) > 0 else None


class Box:
    def __init__(self):
        pass


__m = Box()
__m.stack = []
__m.info = False
__m.debug = False
__m.trace = False


def enable_info():
    __m.info = True
    set_silent_mode(False)


def enable_debug():
    __m.info = True
    __m.debug = True
    set_silent_mode(False)


def enable_trace():
    __m.info = True
    __m.debug = True
    __m.trace = True
    set_silent_mode(False)


def info_enabled():
    return __m.info


# def debug_enabled():
#     return __m.debug


def trace_enabled():
    return __m.trace


def _(text, close=False, thru_silent_mode=False):
    if is_silent_mode(thru_silent_mode):
        return

    if info_enabled():
        f_stdout('{}INFO: {}', ' ' if debug_enabled() else '', text)
    else:
        __m.stack.append(text)  # push

        sys.stdout.write(text)
        sys.stdout.flush()

    if close:
        __(thru_silent_mode)


def __(closing_text=None, thru_silent_mode=False):
    if is_silent_mode(thru_silent_mode):
        return

    if closing_text:
        _(closing_text, thru_silent_mode)

    if not info_enabled():  # or any lower prio tracing
        text = __m.stack.pop()  # pop
        backspaces = '\b' * len(text)
        spaces = ' ' * len(text)

        sys.stdout.write(backspaces)
        sys.stdout.write(spaces)
        sys.stdout.write(backspaces)
        sys.stdout.flush()

    if closing_text:
        __(thru_silent_mode)
