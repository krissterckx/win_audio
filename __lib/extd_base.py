# coding: utf-8

from __future__ import print_function

from string import ascii_lowercase, ascii_uppercase, digits

from __lib.base import exc_error

LOWER_CASE_PREPOSITIONS = False


def to_camel_case(name, preserved_words=None):
    try:
        preserved = []
        preserved_words = preserved_words or []

        if LOWER_CASE_PREPOSITIONS:
            for w in ['a', 'an', 'the', 'da', 'but', 'and', 'or',
                      'at', 'in', 'on', 'by', 'from', 'to', 'of',
                      'd\'', 'de', 'het', 'een', 'van', 'op', 'en',
                      'du',  # German Du unfort. also matches - see below
                      'des', 'ne', 'le', 'la', 'les',
                      'ein', 'eine', 'einen', 'das',
                      'des', 'los', 'las', 'les', 'del']:
                preserved.append(w)
                name = name.replace(' ' + w.title() + ' ', ' ' + w + ' ')
                name = name.replace('- ' + w + ' ', '- ' + w.title() + ' ')

        for w in ['aka', 'x']:
            preserved.append(w)

        preserved.extend(preserved_words)  # it is important to extend them at
        #                                    the end, and not at the beginning

        name = '^' + name + '$'
        name = name.replace('´', "'")
        name = name.replace('’', "'")
        name = name.replace("I'M", "I'm")  # seems to happen regularly
        for c in ['(', '[']:
            name = name.replace(c + 'With ', c + 'preservemewith ')
            name = name.replace(c + 'with ', c + 'preservemewith ')
            name = name.replace(c + 'preservemewith the ', c + 'With the ')

        if not LOWER_CASE_PREPOSITIONS:
            name = name.replace('Live at ', 'Live Preservemeat ')
            name = name.replace('Remix by ', 'Remix Preservemeby ')

        name = name.replace('a.k.a.', 'Preservemea.Preservemek.Preservemea.')

        for c in ascii_uppercase:
            name = name.replace(c, ' preserveupper ' + c)
        for c in ascii_lowercase:
            name = name.replace("+" + c, ' preserveplus' + c)
            name = name.replace("*" + c, ' preserveasterix' + c)
            name = name.replace("$" + c, ' preservedollarsign' + c)
            name = name.replace("'" + c, ' preservesinglequote' + c)
            for d in digits:
                name = name.replace(d + c, ' preserve' + d + 'digit' + c)
        for special in ('É', 'Ø', 'Á'):
            name = name.replace(special, ' preserveme ' + special)
        for word in preserved:
            for begin_char in ('^', ' ', ',', '/'):
                for end_char in (' ', '$', ',', '/'):
                    match = begin_char + word + end_char
                    rematch = begin_char + 'preserveme' + word + end_char
                    name = name.replace(match, rematch)

        name = name.title()

        name = name.replace(' Preserveupper ', '')
        name = name.replace(' Preserveplus', "+")
        name = name.replace(' Preserveasterix', "*")
        name = name.replace(' Preservedollarsign', "$")
        name = name.replace(' Preservesinglequote', "'")
        for d in digits:
            name = name.replace(' Preserve' + d + 'Digit', d)
        name = name.replace(' Preserveme ', '')
        name = name.replace('Preserveme', '')

        name = name.replace('Featuring', 'featuring')
        name = name.replace('Feat.', 'feat.')

        if LOWER_CASE_PREPOSITIONS:
            name = name.replace('st du', 'st Du')  # german Du
            name = name.replace('du Liebst', 'Du Liebst')

        # always overrule first char, no matter the above, EXCEPT when it is
        # part of the special preserved words
        for c in ascii_lowercase:
            name = name.replace('^' + c, '^' + c.upper())
        for s in preserved_words:
            name = name.replace('^' + s.title(), '^' + s)

        name = name[1:-1]
        return name
    except UnicodeDecodeError as e:
        exc_error(e, 'Safer is to re-run as Py3')
