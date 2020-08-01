import gi
import re
import os
import sys
import shutil
import json

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf

class MainForm:
        def __init__(self):
                self.filelist = []
                self.index = -1
                self.outdir = os.path.expandvars("$HOME")
                self.lastdonefile = os.path.expandvars("$HOME/.photochecker")
                self.listfile = ""
                try:
                        with open(self.lastdonefile, "rt") as f:
                                data = json.load(f)
                                self.listfile = data["listfile"]
                                self.outdir = data["outdir"]
                                self.parseListFile(self.listfile)
                                self.index = data["index"]
                                builder.get_object("foInput").set_filename(self.listfile)
                                builder.get_object("doOutput").set_filename(self.outdir)
                except:
                        e = sys.exc_info()[0]
                        self.textDlg(e)
                        self.filelist = []
                        self.index = -1
                self.updateProgress()
                self.showPicture()

        def saveLastDone(self):
                try:
                        with open(self.lastdonefile, "wt") as f:
                                data = {}
                                data["listfile"] = self.listfile
                                data["outdir"] = self.outdir
                                data["index"] = self.index
                                json.dump(data, f)
                except:
                       e = sys.exc_info()[0]
                       self.textDlg(e)
        
        def actionShow(self, *args):
                self.updateProgress()
                self.showPicture()
                

        def textDlg(self, txt):
                dlg = Gtk.MessageDialog(
                        flags = 0,                        
                        buttons = Gtk.ButtonsType.OK,
                        text = txt,
                )
                dlg.run()
                dlg.destroy()

        def updateProgress(self):
                pb = builder.get_object("pbProgress")
                lb = builder.get_object("lbProgress")
                lc = builder.get_object("lbCurrent")
                if len(self.filelist) == 0:
                        lc.set_text("- /")
                        pb.set_fraction(0.0)                        
                        lb.set_text("-/0")
                else:
                        lc.set_text(self.filelist[self.index][0] + " " + self.filelist[self.index][1])
                        pb.set_fraction((self.index + 1) * 1.0 / len(self.filelist))
                        lb.set_text(str(self.index) + "/" + str(len(self.filelist)))
                self.saveLastDone()
                
        def parseListFile(self, filename):
                try:
                        with open(filename, "rt") as f:
                                fl = [re.findall('([0-9a-fA-F]{32})\s+(.+)', line)[0] for line in f]
                                fl.sort(key = lambda x : x[1])
                                self.filelist = fl
                                if len(self.filelist) == 0:
                                        self.index = -1
                                else:
                                        self.index = 0
                                self.updateProgress()
                                self.showPicture()
                except:
                       e = sys.exc_info()[0]
                       self.textDlg(e)
                
        def showPicture(self):
                pi = builder.get_object("pictImage")
                if self.index < 0:
                        pi.set_from_file("")
                else:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                                self.filelist[self.index][1], 500, 500, True)
                        pi.set_from_pixbuf(pixbuf)

        def actionSetPhotoListFile(self, widget):
                self.listfile = widget.get_filename()
                self.parseListFile(self.listfile)
                self.textDlg("Found " + str(len(self.filelist)) + " entries")

        def actionOutputDir(self, widget):
                self.outdir = widget.get_filename()

        def actionPrev(self, widget):
                if self.index > 0:
                        self.index = self.index - 1
                        self.updateProgress()
                        self.showPicture()

        def actionNext(self, widget):
                if self.index < len(self.filelist) - 1:
                        self.index = self.index + 1
                        self.updateProgress()
                        self.showPicture()

        def actionSave(self, widget):
                try:
                        if self.index >= 0:
                                shutil.copyfile(self.filelist[self.index][1], 
                                        self.outdir + "/" + 
                                        os.path.basename(self.filelist[self.index][1]))
                                self.textDlg(self.filelist[self.index][1])
                except:
                       e = sys.exc_info()[0]
                       self.textDlg(e)


builder = Gtk.Builder()
builder.add_from_file("PhotoChecker.glade")
builder.connect_signals(MainForm())

window = builder.get_object("wndMain")
window.connect("destroy", Gtk.main_quit)
window.show_all()

Gtk.main()
