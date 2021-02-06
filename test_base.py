# coding: utf-8

from __lib.base import new_file, copy_file, move_file, duplicate_file,\
    rename_file, remove_file, fatal_error, is_windows,\
    stdout, red, green, blue, cyan, f_yellow, error, split_file_extension
from __lib.extd_base import to_camel_case

# TODO(change to unittest/pytest)


def assert_equal(a, b):
    if a != b:
        fatal_error(a, '!=', b)


def test_colours():
    stdout('USA is ', end='')
    red('stars ', end='')
    stdout('and ', end='')
    blue('stripes')
    cyan('test_colours OK')


def test_windows():
    f_yellow('You are on {}Windows', '' if is_windows() else 'non-')
    cyan('test_windows OK')


def test_error():
    error('wooo...bad (just kidding)')
    error('wooo...bad', end=' (just kidding!)\n')
    cyan('test_error OK')


def test_file_extension():
    f = 'grease/is/the.word'
    f_base, f_ext = split_file_extension(f)
    assert_equal('grease/is/the', f_base)
    assert_equal('.word', f_ext)
    cyan('test_file_extension OK')


def old_test_to_camel_case():
    assert_equal('Max Don\'t Have Sex With Your Ex',
                 to_camel_case("Max Don’t Have Sex With Your Ex"))
    assert_equal('Please Don\'t Go', to_camel_case('Please Don\'t Go'))
    assert_equal('An Angel \'s Love', to_camel_case('An angel \'s love'))
    assert_equal('The Cook and the Thief',
                 to_camel_case('The cook and the thief'))
    assert_equal('Kris\'s Book', to_camel_case('Kris\'s book'))
    assert_equal('I\'m Singin\' ABC', to_camel_case('I\'M singin\' ABC'))
    assert_equal('I Am the DJ', to_camel_case('I am the DJ'))
    assert_equal('I\'m from the 80ies', to_camel_case('I\'m from the 80ies'))
    assert_equal('You\'re from the 70s', to_camel_case('You\'re from the 70s'))
    assert_equal('DON\'T YOU', to_camel_case('DON\'T YOU'))
    assert_equal('L\'Envie des Etoilles',
                 to_camel_case('L\'Envie des Etoilles'))
    assert_equal('S\'Express', to_camel_case('S\'Express'))
    assert_equal('Charlotte de Witte', to_camel_case('Charlotte de Witte'))
    assert_equal('X (Extasy)', to_camel_case('x (Extasy)'))
    assert_equal('Annie x Billie', to_camel_case('Annie x Billie'))
    assert_equal('deadmau5 Preserved', to_camel_case('deadmau5 preserved',
                                                     ['deadmau5']))
    assert_equal('As Is feat.', to_camel_case('As is feat.'))
    assert_equal('Du Bist Hanz', to_camel_case('du bist hanz'))
    cyan('test_to_camel_case OK')


def test_to_camel_case():
    assert_equal('Max Don\'t Have Sex With Your Ex',
                 to_camel_case("Max Don’t Have Sex With Your Ex"))
    assert_equal('Please Don\'t Go', to_camel_case('Please Don\'t Go'))
    assert_equal('An Angel \'s Love', to_camel_case('An angel \'s love'))
    assert_equal('The Cook And The Thief',
                 to_camel_case('The cook and the thief'))
    assert_equal('Kris\'s Book', to_camel_case('Kris\'s book'))
    assert_equal('I\'m Singin\' ABC', to_camel_case('I\'M singin\' ABC'))
    assert_equal('I Am The DJ', to_camel_case('I am the DJ'))
    assert_equal('I\'m From The 80ies', to_camel_case('I\'m from the 80ies'))
    assert_equal('You\'re From The 70s', to_camel_case('You\'re from the 70s'))
    assert_equal('DON\'T YOU', to_camel_case('DON\'T YOU'))
    assert_equal('L\'Envie Des Etoilles',
                 to_camel_case('L\'Envie des Etoilles'))
    assert_equal('S\'Express', to_camel_case('S\'Express'))
    assert_equal('Charlotte De Witte', to_camel_case('Charlotte de Witte'))
    assert_equal('X (Extasy)', to_camel_case('x (Extasy)'))
    assert_equal('Annie x Billie', to_camel_case('Annie x Billie'))
    assert_equal('deadmau5 Preserved', to_camel_case('deadmau5 preserved',
                                                     ['deadmau5']))
    assert_equal('As Is feat.', to_camel_case('As is feat.'))
    assert_equal('Du Bist Hanz', to_camel_case('du bist hanz'))
    cyan('test_to_camel_case OK')


def test_file_manipulation_1():
    dryrun = False
    verbose = False
    silent = True
    safe_remove = False

    new_file('test1.txt', 'test1\n')
    duplicate_file('.', 'test1.txt', 'test2.txt',
                   dryrun=dryrun, verbose=verbose, silent=silent)
    rename_file('.', 'test1.txt', 'test3.txt',
                dryrun=dryrun, verbose=verbose, silent=silent)
    rename_file('.', 'test2.txt', 'test3.txt',  # will give test3 (1).txt
                dryrun=dryrun, verbose=verbose, silent=silent)
    remove_file('.', 'test3.txt', safe_remove=safe_remove,
                dryrun=dryrun, verbose=verbose, silent=silent)
    remove_file('.', 'test3 (1).txt', safe_remove=safe_remove,
                dryrun=dryrun, verbose=verbose, silent=silent)
    cyan('test_file_manipulation_1 OK')


def test_file_manipulation_2():
    dryrun = False
    verbose = False
    silent = True
    safe_remove = False

    new_file('test1.txt', 'test1\n')
    copy_file('test1.txt', 'test2.txt',
              dryrun=dryrun, verbose=verbose, silent=silent)
    move_file('test1.txt', 'test3.txt',
              dryrun=dryrun, verbose=verbose, silent=silent)
    move_file('test2.txt', 'test3.txt',  # will vive test3 (1).txt file
              dryrun=dryrun, verbose=verbose, silent=silent)
    remove_file('.', 'test3.txt', safe_remove=safe_remove,
                dryrun=dryrun, verbose=verbose, silent=silent)
    remove_file('.', 'test3 (1).txt', safe_remove=safe_remove,
                dryrun=dryrun, verbose=verbose, silent=silent)
    cyan('test_file_manipulation_2 OK')


if __name__ == "__main__":
    test_colours()
    test_windows()
    test_error()
    test_to_camel_case()
    test_file_extension()
    test_file_manipulation_1()
    test_file_manipulation_2()
    green('ALL TESTS PASS. Happy day :)')
    cyan('Final test is a fatal error:')
    fatal_error('The world exploded')
    error('SHOULD NOT HAVE COME HERE!')
