"""
Anki plugin for inserting lesson numbers into cards based on tag data.

Author: Max Bolingbroke (batterseapower@hotmail.com)
License: BSD3 (http://www.opensource.org/licenses/bsd-license.php)
"""

# Model to modify
MODEL_NAME = "Heisig"

# Field to write the lesson number to
LESSON_FIELD_NAME = "Lesson number"

# Tag prefix
LESSON_TAG_PREFIX = "Lesson"


from PyQt4 import QtGui, QtCore
from anki.cards import Card
from anki.utils import parseTags
from ankiqt import mw

######################################################################
#  Add Tag to lesson number choice to the Tool menu. On pressing it, #
#  the update_deck function will run.                                #
######################################################################
def init_hook():
  mw.mainWin.TagToLessonNo = QtGui.QAction("Tags to lesson numbers", mw)
  mw.mainWin.TagToLessonNo.setStatusTip("Change tags like " + LESSON_TAG_PREFIX + "N into values for the " + LESSON_FIELD_NAME  + " field")
  mw.mainWin.TagToLessonNo.setEnabled(True)
  mw.mainWin.TagToLessonNo.setIcon(QtGui.QIcon(":/icons/kanji.png"))
  mw.connect(mw.mainWin.TagToLessonNo, QtCore.SIGNAL('triggered()'), update_deck)
  mw.mainWin.menuTools.addAction(mw.mainWin.TagToLessonNo)

#######################################
#  Run when the menu item is clicked. #
#######################################
def update_deck():
  model = mw.deck.s.scalar('select id from models where name = \'%s\'' % MODEL_NAME)
  card_model = mw.deck.s.scalar('select id from cardmodels where modelId = %s' % model)
  
  for card in mw.deck.s.query(Card).filter('cardModelId = %s' % card_model):
    update_card(card)
  
  print "Deck modification complete"
  mw.deck.s.flush()
  mw.deck.setModified()

############################################################
#  Does the actual update of a card with the lesson number #
############################################################
def update_card(card):
  candidate_lesson_nos = []
  for tag in parseTags(card.allTags()):
    if tag.startswith(LESSON_TAG_PREFIX):
      suffix = tag.lstrip(LESSON_TAG_PREFIX)
      
      try:
        candidate_lesson_nos.append(int(suffix))
      except ValueError:
        continue
  
  if len(candidate_lesson_nos) != 1:
    print "Too many or too few lesson numbers, skipping"
    return
  
  card.fact[LESSON_FIELD_NAME] = unicode(candidate_lesson_nos[0])


if __name__ == "__main__":
  print "Don't run me.  I'm a plugin!"

else:
  mw.addHook('init', init_hook)
  print 'Tag to lesson number plugin loaded'