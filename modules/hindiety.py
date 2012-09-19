#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hindiety.py - Jenni Hindi Etymology Module
Copyright 2012, Kenneth K. Sham
Licensed under the Eiffel Forum License 2.

More info:
 * Jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
import web

url = 'http://www.shabdkosh.com/s?e=%s&t=1'
r_inl = re.compile(r'([^<]+)<')
r_speech = re.compile(r'(?i)h3 class="([^"]+)">\1\&nbsp;')
r_gender = re.compile(r'(?i)<span title="Gender">([^<]+)</span>')
r_html   = re.compile(r'(?i)<[^>]+>')

term = None
speech = None


def hindiety(jenni, word):
    parts = word.split(' ')

    if len(parts) == 1:
        jenni.say('No term given.')
        return

    term = parts[1]
    speech = None

    if len(parts) == 3:
        speech = parts[2]

    bytes = web.get(url % term)

    # Skip to Meanings section
    check = '<h2 class="inline">Meanings</h2>'
    index = bytes.find(check)
    if index == -1:
        jenni.say('Term `%s\' not found.' % term)
        return

    bytes = bytes[index + len(check):]

    # From Meanings, skip pass the Hide Transliteration part
    check = 'Hide Transliteration</a>)'
    index = bytes.find(check)
    if index == -1:
        jenni.say('ERR 120: Parse error.')
        return

    bytes = bytes[index + len(check):]

    # Stop before Synonyms
    check = '<h2>Synonyms</h2>'
    index = bytes.find(check)
    if index == -1:
        jenni.say('ERR 121: Parse error.')
        return

    bytes = bytes[:index]

    init(jenni, bytes)


def init(jenni, bytes):
    definitions = bytes.split('class="in l">')

    output = []
    out_hash = {}
    t_speech = ''
    for line in definitions:
        definition = r_inl.findall(line)

        if not definition:
            continue

        aline = '==|=='.join(definition)
        a_speech = r_speech.findall(aline)
        if len(a_speech) > 0:
            a_speech_clean = a_speech[0].strip()

            # only whitespace?
            if a_speech_clean <> '':
                t_speech_tmp = t_speech
                t_speech = a_speech_clean

                # was there a change from '' -> something
                if t_speech_tmp == '' and t_speech <> '':
                    continue

        if t_speech == '':
            continue

        if not t_speech in out_hash:
            out_hash[t_speech] = 0

        # do not print more than 5 in
        # any speech category
        if out_hash[t_speech] == 5:
            continue
        if not speech is None:
            if speech.lower() != t_speech.lower():
                continue

        if definition[0].startswith('div'):
            continue

        definition_term = definition[0]
        definition_term = definition_term.decode('utf-8')

        definition_gender = r_gender.findall(line)
        if definition_gender:
            definition_gender = definition_gender[0]
            definition_gender = r_html.sub('', definition_gender)
            definition_gender = '(' + definition_gender + ') '
        else:
            definition_gender = ''

        definition_latin = None
        definition_latin_idx = 3
        if definition_gender <> '':
            definition_latin_idx = 5

        if len(definition) >= definition_latin_idx + 1:
            if definition[definition_latin_idx - 1] == 'span class="latin">':
                definition_latin = definition[definition_latin_idx]
                definition_latin = definition_latin.replace('br>', '')
                definition_latin = definition_latin.decode('utf-8')

        if definition_latin is None:
            output.append(u'\x02%s:\x02 %s%s' % (t_speech, definition_gender, definition_term))
        else:
            output.append(u'\x02%s:\x02 %s%s (%s)' % \
                    (t_speech, definition_gender, definition_term, definition_latin))

        out_hash[t_speech] = out_hash[t_speech] + 1

    if output == []:
        jenni.say('Speech `%s\' not found for term `%s\'' % \
                (speech, term))
        return

    current_line = ''
    for oute in output:
        if len(current_line + ', ' + oute) > 200:
            jenni.say(current_line)
            current_line = oute
            continue
        if current_line == '':
            current_line = oute
            continue
        current_line += ', ' + oute
    if current_line != '':
        jenni.say(current_line)

hindiety.commands = ['hi']
hindiety.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()
