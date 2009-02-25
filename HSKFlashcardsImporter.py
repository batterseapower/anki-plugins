"""
Anki plugin for importing HSK files from http://hskflashcards.com/download.php

Author: Max Bolingbroke (batterseapower@hotmail.com)
License: BSD3 (http://www.opensource.org/licenses/bsd-license.php)
"""

import sys
import string
import re
import os.path

import xml.dom.minidom

import codecs
import anki.importing
import traceback

from ankiqt import mw, ui
from anki.lang import _
from anki.errors import *

# Uncomment exactly one of these lines to choose which kind of character to use:
CHARACTER_FIELD='simplified'
#CHARACTER_FIELD='traditional'

# Optionally uncomment the line belowe to import only cards from a particular level:
LEVEL_FILTER=None
#LEVEL_FILTER=1


"""
Class used to represent Words as they proceed through the import process.
"""

class Word(object):
    pass


"""
This is a plug-in that allows HSKflashcards.com formatted vocabulary lists to be imported into Anki.
"""

class HSKFlashcardsImporter(anki.importing.Importer):
    """
    The importer sub-class for HSKflashcards.com files.
    """

    def __init__(self, *args):
        anki.importing.Importer.__init__(self, *args)
        self.words = None
        
    def fields(self):
        """
        Number of fields.  We have level, expression, reading, meaning and part of speech.
        Inherited from default importer.
        """
        return 4

    def foreignCards(self):
        """
        Returns the cards read from the XML file.
        Inherited from default importer.
        """
        cards = []
        self.log = []
        try:
            self.read_file()

            for word in self.words:
                # Buid an Anki card from the processed 'word' node
                card = anki.importing.ForeignCard()
                card.fields.extend([word.expression, word.meaning, word.reading, u"Level" + word.level])
                cards.append(card)
        except Error, e:
            self.log.append(e.message)
        except ImportFileError, e:
            self.log.append(e.message)
        
        return cards

    def read_file(self):
        """
        Read the XML file into self.words, unless it has already been
        done.
        """
        if self.words is not None: return

        # To start off, load up the XML and parse out all the word nodes
        ui.utils.showWarning("Reading")
        document = xml.dom.minidom.parse(self.file)
        ui.utils.showWarning("Raw")
        raw_words = [self.read_word(word_node) for word_node in document.getElementsByTagName('word')]
        
        # Filter out unwanted levels, if necessary
        ui.utils.showWarning("Filtering")
        if LEVEL_FILTER is not None:
            raw_words = [raw_word for raw_word in raw_words if raw_word.level == str(LEVEL_FILTER)]

        # Disambiguate words if necessary
        ui.utils.showWarning("Disambiguating")
        self.words = self.disambiguate_words(raw_words)

    def read_word(self, word_node):
        # This nested function does the common task of extracting information from
        # a single XML node that represents some subcomponent of a 'word'
        def readField(name):
            candidate_nodes = word_node.getElementsByTagName(name)
            if len(candidate_nodes) < 1:
                # No node under the 'word' with the given name, so we need to give up
                raise "No field " + name + " in word node!"
            else:
                # Otherwise, try and find the text that node contains, and return
                # the empty string if there was no text at all
                value_node = candidate_nodes[0].firstChild
                if not value_node:
                    return ""
                else:
                    return unicode(value_node.nodeValue)
        
        # Read the data and blast it back as a Word
        word = Word()
        word.expression     = readField(CHARACTER_FIELD)
        word.meaning        = readField('en')
        word.reading        = readField('pinyin')
        word.level          = readField('level')
        word.part_of_speech = readField('part_of_speech')
        
        return word
    
    def disambiguate_words(self, raw_words):
        # Group words by expression
        by_expression = {}
        for raw_word in raw_words:
            by_expression.setdefault(raw_word.expression, []).append(raw_word)
        
        # Nested function for disambiguation
        def disambiguate(word):
            word.expression += u" (" + word.part_of_speech + u")"
            return word
        
        # Get them back out
        final_words = []
        for expression, these_words in by_expression.iteritems():
            if len(these_words) == 1:
                final_words.append(these_words[0])
            else:
                final_words.extend([disambiguate(this_word) for this_word in these_words])
        
        return final_words

# Hook this thing up to the main program
def init_hook():
    """
    Initialises the Anki GUI to present an option to invoke the plugin.
    """
    l = list(anki.importing.Importers)
    l.append(('hskflashcards.com XML file (*.xml)', HSKFlashcardsImporter))
    anki.importing.Importers = tuple(l)

if __name__ == '__main__':
    print "Don't run me from the command line - put me in the Anki plugins directory!"
    
else:
    mw.addHook('init', init_hook)
    print 'HSKFlashcardsImporter plugin loaded'