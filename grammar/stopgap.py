from dragonfly import (Grammar, AppContext, CompoundRule, Choice, Dictation, List, Optional, Literal)
import natlink, os

from comsat import ComSat

from raul import SelfChoice, processDictation, NUMBERS as numbers

#---------------------------------------------------------------------------
# Create this module's grammar and the context under which it'll be active.

grammar_context = AppContext(executable="notepad")
grammar = Grammar("notepad_example", context=grammar_context)

class MouseClick(CompoundRule):
  spec = "zap [<cmd>]"
  cmd = ["one", "two", "to", "too", "three"]
  extras = [SelfChoice("cmd", cmd)]

  def _process_recognition(self, node, extras):
    button = str(extras.get("cmd", 1))
    button = int(numbers.get(button, button))
    with ComSat() as cs:
      rpc = cs.getRPCProxy()
      rpc.callClick(button)

class QuadCommand(CompoundRule):
  spec = "zip <xcoord> <ycoord>"
  cmd = ["zero", "one", "two", "too", "to", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
  extras = [SelfChoice("xcoord", cmd), SelfChoice("ycoord", cmd)]

  def _process_recognition(self, node, extras):
    x = extras["xcoord"]
    y = extras["ycoord"]
    x = numbers.get(x, x)
    y = numbers.get(y, y)
    x = 1280 * int(x) / 10
    y = 800 * int(y) / 10
    with ComSat() as cs:
      rpc = cs.getRPCProxy()
      rpc.callMouse(x, y)
      if "zap" in extras:
        rpc.callClick(1)

class TranslateSpecial(CompoundRule):
  spec = "<cmd>"
  # say: law raw slaw sraw claw craw
  cmd = {"act":"Escape", "append":"a", "inns":"i", "vim replace":"R", "Kerry":"Home", "dolly":"End"}
  extras = [Choice("cmd", cmd)]

  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      cs.getRPCProxy().callKeys(str(extras["cmd"]).split())

class Translate(CompoundRule):
  spec = "<cmd>"

  cmd = {"push":"(", "pop":")", "push push":"((", "pop pop":"))", "slot":"[", "straw":"]", "claw":"{", "draw":"}",
         "law raw":"()", "slot straw":"[]", "claw draw":"{}", "light":"< ", "right":"> ",
         "light right":"<>", "typename int":"int ", "assign":"= ",
         "equal":"== ", "resolve":"::", "light light":"<< ", "right right":">> ",
         "alpha":"a", "bravo":"b", "charlie":"c", "ace ace":"  ", "slap slap":"\n\n",
         "pie deaf":"def ", "yeah":":", "yeah yeah":"::", "dub quote dub quote":'""',
         "dub quote dub quote dub quote":'"""', "yep":", ", "yep quote":'", "'}
  extras = [Choice("cmd", cmd)]
 
  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      cs.getRPCProxy().callText(str(extras["cmd"]))

class DocString(CompoundRule):
  spec = "doc string [<ind>]"

  extras = [Dictation("ind")]

  def _process_recognition(self, node, extras):
    if "ind" in extras:
      index = processDictation(extras["ind"])
    else:
      index = ""
    with ComSat() as cs:
      ds = "'''"
      cs.getRPCProxy().callText("%s%s%s" % (ds, index, ds))
      if not index:
        cs.getRPCProxy().callKeys("Left " * 3)
      
class DubDocString(CompoundRule):
  spec = "dub doc string [<ind>]"

  extras = [Dictation("ind")]

  def _process_recognition(self, node, extras):
    if "ind" in extras:
      index = processDictation(extras["ind"])
    else:
      index = ""
    with ComSat() as cs:
      ds = '"""'
      cs.getRPCProxy().callText("%s%s%s" % (ds, index, ds))
      if not index:
        cs.getRPCProxy().callKeys("Left " * 3)
      
class TemplateIndices(CompoundRule):
  spec = "diamond [<ind>]"

  extras = [Dictation("ind")]

  def _process_recognition(self, node, extras):
    if "ind" in extras:
      index = processDictation(extras["ind"])
    else:
      index = ""
    with ComSat() as cs:
      cs.getRPCProxy().callText("<%s>" % index)
      if not index:
        cs.getRPCProxy().callKeys("Left")

class ParIndices(CompoundRule):
  spec = "circle [<ind>]"
 
  extras = [Dictation("ind")]

  def _process_recognition(self, node, extras):
    if "ind" in extras:
      index = processDictation(extras["ind"])
    else:
      index = ""
    with ComSat() as cs:
      cs.getRPCProxy().callText("(%s)" % index)
      if not index:
        cs.getRPCProxy().callKeys("Left")
      
class ArrayIndices(CompoundRule):
  spec = "square [<ind>]"
 
  extras = [Dictation("ind")]

  def _process_recognition(self, node, extras):
    if "ind" in extras:
      index = processDictation(extras["ind"])
      index = numbers.get(index, index)
    else:
      index = ""
    with ComSat() as cs:
      cs.getRPCProxy().callText("[%s]" % index)
      if not index:
        cs.getRPCProxy().callKeys("Left")

class ScratchMove(CompoundRule):
  spec = "<cmd> [<ind>]"
  cmds = {"scratch":"BackSpace", "back scratch":"Delete", "up":"Up", "down":"Down",
           "left":"Left", "right":"Right", "ace":"ace", "slap":"Return",
           "dub quote":'shift apostrophe', "sing quote":"apostrophe",
           "tab":"Tab"}
  cmd = cmds.keys()
  extras = [Dictation("ind"), SelfChoice("cmd", cmd)]
 
  def _process_recognition(self, node, extras):
    if "ind" in extras:
      index = processDictation(extras["ind"])
      index = int(numbers.get(index, index))
    else:
      index = 1
    cmd = str(extras["cmd"]).lower()
    cmd = self.cmds[cmd]
    if cmd == "ace":
      cmd = "space"
    elif cmd == "shift apostrophe":
      cmd = "^apostrophe"
    with ComSat() as cs:
      cs.getRPCProxy().callModifiedKeys((cmd + " ") * index)
      
class Capitalization(CompoundRule):
  spec = "<cmd> <name>"
  cmd = {"camel":"c", "resolution":"R", "steadily":"s", ".word":".", "score":"_", "capscore":"C_",
         "up score":"U_", "jumble":"jumble"}
  extras = [Choice("cmd", cmd), Dictation("name")]
      
  def _process_recognition(self, node, extras):
    name = processDictation(extras["name"]).replace("std::\\", "std").split()
    cmd = extras["cmd"]
    if cmd == "c":
      var = ''.join([name[0]] + [x.capitalize() for x in name[1:]])
    elif cmd == "s":
      var = ''.join([x.capitalize() for x in name])
    elif cmd == ".":
      var = '.'.join(name).lower()
    elif cmd == "_":
      var = '_'.join(name).lower()
    elif cmd == "C_":
      var = '_'.join([x.capitalize() for x in name])
    elif cmd == "U_":
      var = '_'.join(name).upper()
    elif cmd == "R":
      var = '::'.join(name)
    elif cmd == "jumble":
      var = "".join(name).lower()
    with ComSat() as cs:
      cs.getRPCProxy().callText(var)


class LetMeTalk(CompoundRule):
  spec = "little <text>"
  extras = [Dictation("text")]

  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      cs.getRPCProxy().callText(processDictation(extras["text"]))

class TBNotJunk(CompoundRule):
  spec = "bird not spam"
  extras = []

  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      cs.getRPCProxy().callModifiedKeys("^j")
      
class TBJunk(CompoundRule):
  spec = "bird spam"
  extras = []

  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      cs.getRPCProxy().callText("j")
      
class TBBodyPane(CompoundRule):
  coords = {"pane":(400, 130),
            "body":(290, 522)}
            
  spec = "bird <location>"
  extras = [SelfChoice("location", coords)]
  
  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      location = str(extras["location"])
      cs.getRPCProxy().callPhantomClick(*self.coords[location], phantom=False)
      
class TBInbox(CompoundRule):
  spec = "bird <location>"
  coords = {"inbox":(75, 120),
            "limbo":(75, 210),
            "list":(75, 230)}
  extras = [SelfChoice("location", coords)]

  def _process_recognition(self, node, extras):
    with ComSat() as cs:
      location = str(extras["location"])
      if location not in ("pane", "body"):
        cs.getRPCProxy().callPhantomClick(*self.coords[location])
      cs.getRPCProxy().callPhantomClick(400, 130, phantom=False)

class IonFlipFlop(CompoundRule):
  spec = "<flip>"
  flip = ["flip", "flop"]
  extras = [SelfChoice("flip", flip)]

  def _process_recognition(self, node, extras):
    flip = str(extras["flip"])
    flip = {"flip":"Tab", "flop":"p"}[flip]
    with ComSat() as cs:
      cs.getRPCProxy().callModifiedKeys(["&" + flip])
      
class IonTab(CompoundRule):
  spec = "flip <tab>"
  tab = ["zero", "one", "two", "too", "to", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
  extras = [SelfChoice("tab", tab)]

  def _process_recognition(self, node, extras):
    tab = str(extras["tab"])
    tab = int(numbers.get(tab, tab))
       
    with ComSat() as cs:
      cs.getRPCProxy().callSetIonTab(tab)
      
class IonTwinkle(CompoundRule):
  spec = "work <workspace>"
  workspace = ["one", "to", "too", "two", "three", "four", "five", "six"]
  whimsical = {"quebec":"4", "whiskey":"5", "echo":"6",
               "organ":"4", "bird":"5", "miss":"6"}
  extras = [SelfChoice("workspace", workspace + whimsical.keys())]

  def _process_recognition(self, node, extras):
    workspace = str(extras["workspace"])
    workspace = self.whimsical.get(workspace, workspace)
    workspace = int(numbers.get(workspace, workspace))
       
    with ComSat() as cs:
      cs.getRPCProxy().callSetIonWorkspace(workspace)

grammar.add_rule(Translate())
grammar.add_rule(TranslateSpecial())
grammar.add_rule(ArrayIndices())
grammar.add_rule(ParIndices())
grammar.add_rule(LetMeTalk())
grammar.add_rule(DubDocString())
grammar.add_rule(DocString())
grammar.add_rule(ScratchMove())
grammar.add_rule(TemplateIndices())
grammar.add_rule(TBJunk())
grammar.add_rule(QuadCommand())
grammar.add_rule(MouseClick())
grammar.add_rule(TBNotJunk())
grammar.add_rule(Capitalization())
grammar.add_rule(TBInbox())
grammar.add_rule(TBBodyPane())
grammar.add_rule(IonTwinkle())
grammar.add_rule(IonFlipFlop())
grammar.add_rule(IonTab())

#---------------------------------------------------------------------------
# Load the grammar instance and define how to unload it.

grammar.load()

# Unload function which will be called by natlink at unload time.
def unload():
  global grammar
  if grammar: grammar.unload()
  grammar = None
