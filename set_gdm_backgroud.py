#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Mauro Torrez. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import re
import pygtk
pygtk.require('2.0')

import gtk
import commands
import os

# Check for new pygtk: this is new class in PyGtk 2.4
if gtk.pygtk_version < (2,3,90):
   print "PyGtk 2.3.90 or later required for this example"
   raise SystemExit

class App:
   path = None
   disp = "stretched"
   conffile = "/etc/gdm3/greeter.gconf-defaults"
   image = gtk.Image()
   screenw = -1
   screenh = -1

   # redraw the screen thumbnail with currently selected file and disposition
   def redraw(self):

      # new pixbuf from current path
      try:
         readimg = gtk.gdk.pixbuf_new_from_file(self.path)
      except:
         readimg = None
         print "WARNING: Unable to load image."

      # create an pixbuf for the thumbnail and fill it with a background pattern
      thumbpixbuf = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB, True, 8,
                                    int(self.screenw/4.0),
                                    int(self.screenh/4.0) )
      thumbpixbuf.fill(0x88888888)
      thumbpixbuf.saturate_and_pixelate(thumbpixbuf, 0.0, True)

      if readimg is not None:
         imgw = readimg.get_width()
         imgh = readimg.get_height()

         # calculate selected image and screen proportions (width-to-height ratio)
         disp_ratio = float(self.screenw)/float(self.screenh)
         img_ratio = float(imgw)/float(imgh)

         # switch between the different disposition styles
         if self.disp == "zoom":

            # if display wider than image, scale image to fit screen width
            if disp_ratio > img_ratio:
               thumbw = int(self.screenw/4.0)
               thumbh = int(imgh*((self.screenw/4.0)/imgw))

            # else scale image to fit screen height
            else:
               thumbh = int(self.screenh/4.0)
               thumbw = int(imgw*((self.screenh/4.0)/imgh))

            # scale previously loaded image and copy to the screen thumbnail pixbuf
            readimg = readimg.scale_simple(thumbw,thumbh,gtk.gdk.INTERP_BILINEAR)
            readimg.copy_area( int((thumbw-self.screenw/4.0)/2),
                            int((thumbh-self.screenh/4.0)/2),
                            int(self.screenw/4), int(self.screenh/4),
                            thumbpixbuf, 0, 0)

         
         elif self.disp == "scaled":

            # with the "scaled" disposition, image is scaled
            # so that it fits entirely onscreen
            xscale = (self.screenw/4.0)/imgw
            yscale = (self.screenh/4.0)/imgh

            thumbw = int(imgw*min(xscale, yscale))
            thumbh = int(imgh*min(yscale, yscale))

            readimg = readimg.scale_simple(thumbw,thumbh,gtk.gdk.INTERP_BILINEAR)
            readimg.copy_area( 0, 0, thumbw, thumbh, thumbpixbuf,
                            int((self.screenw/4-thumbw)/2),
                            int((self.screenh/4-thumbh)/2))

      
         elif self.disp == "centered":
         
            # scale image to 1/4 its original size
            # (the screen thumbnail is 1/4 of the real screen size)
            readimg = readimg.scale_simple( int(imgw/4), int(imgh/4),
                                         gtk.gdk.INTERP_BILINEAR)

            # the visible area coordinates of the image
            # (if negative, the image is bigger than the screen)
            x0 = int((self.screenw-imgw)/8)
            y0 = int((self.screenh-imgh)/8)
         
            readimg.copy_area( max(-x0,0), max(-y0,0),
                            int(min(self.screenw/4,imgw/4)),
                            int(min(self.screenh/4,imgh/4)),
                            thumbpixbuf, max(x0,0), max(y0,0))


         elif self.disp == "stretched":

            # in this case, simply stretch image so that both width and height
            # are the same as the screen's
            readimg = readimg.scale_simple( int(self.screenw/4),
                                         int(self.screenh/4),
                                         gtk.gdk.INTERP_BILINEAR)
            readimg.copy_area( 0, 0, int(self.screenw/4), int(self.screenh/4),
                            thumbpixbuf, 0, 0)

         
         elif self.disp == "wallpaper":

            # scale image to 1/4 as in centered
            readimg = readimg.scale_simple( int(imgw/4),
                                         int(imgh/4),
                                         gtk.gdk.INTERP_BILINEAR)

            # copy image as tiles until we fill the entire screen
            x0=0
            while( x0 < self.screenw ):
               y0=0
               while( y0 < self.screenh):
                  readimg.copy_area( 0, 0,
                                  int(min(self.screenw/4-x0,imgw/4)),
                                  int(min(self.screenh/4-y0,imgh/4)),
                                  thumbpixbuf, x0, y0)
                  y0 += imgh/4
               x0 += imgw/4

      # finally draw the gtk.Image from the pixbuf      
      self.image.set_from_pixbuf(thumbpixbuf)      


   # read GDM3 configuration file, and set correspondig variables
   def read_config( self ):

      with open( self.conffile, 'r') as conf:

         for line in conf:
            m1 = re.match(r"^\s*/desktop/gnome/background/picture_filename\s+(\S.*)$", line)
            m2 = re.match(r"^\s*/desktop/gnome/background/picture_options\s+(\w+)", line)

            if m1:
               if os.path.isfile( m1.group(1)):
                  print "Image file option read: " + m1.group(1)
                  self.path = m1.group(1)
               else:
                  print "Image file not found"
                  self.path = None

            elif m2:
               print "Image disposition option read: " + m2.group(1)
               self.disp = m2.group(1)

   # save GDM3 options file, replacing the options with the current ones
   def save_config( self, widget=None ):
      
      with open(self.conffile, 'r') as conf:
         out = ""

         for line in conf:
            m1 = re.match(r"^\s*/desktop/gnome/background/picture_filename", line)
            m2 = re.match(r"^\s*/desktop/gnome/background/picture_options", line)

            # if the current line matchs the picture_filename option, replace
            # it with a new one containing the current value of path
            if m1:
               out += "/desktop/gnome/background/picture_filename      " \
                   + self.path + "\n"

            # else if it macthes the picture_options option, put the
            # value of disp instead
            elif m2:
               out += "/desktop/gnome/background/picture_options       "\
                   + self.disp + "\n"

            # else copy the line as-is
            else:
               out += line

         # save the file putting in there the value of out
         with open(self.conffile, 'w') as f:
            f.write(out)
            print "Configuration file saved."

   # close event. don't know if or what it should do
   def close(self, widget, event, data=None):
      return

   # response event. should save setting if "apply", exit if "close"
   def response( self, widget, response):

      if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT:
         gtk.main_quit()

      elif response == gtk.RESPONSE_APPLY:
         self.save_config()

   # current image path changed callback. should redraw the screen thumbnail
   def path_changed( self, widget, response):

      if response == gtk.RESPONSE_ACCEPT:
         self.path = widget.get_filename()
         self.redraw()

   # current disposition option changed callback. should redraw
   def disp_changed( self, widget):
      self.disp = widget.get_active_text()
      self.redraw()

   # initialization function. called upon instantiating a new App object
   def __init__ (self):

      # obtain the root screen width and height
      (status,output)=commands.getstatusoutput('xwininfo -root|grep "geometry"')
      m1 = re.match(r".*geometry\s([0-9]+)x([0-9]+)\+.*", output)
      if m1:
         self.screenw = int(m1.group(1))
         self.screenh = int(m1.group(2))
      else:
         print "Error obtaining screen size. Defaulting to 1024x768."
         print "Verify that the xwininfo command is available in your system."
         self.screenw = 1024
         self.screenh = 768
      
      # read config file to set path and disp accordingly, then redraw
      self.read_config()
      self.redraw()

      # create a new window
      self.window = gtk.Dialog( "Change GDM3 background",
                                None,
                                gtk.DIALOG_NO_SEPARATOR)
      # add "apply" anc "close" buttons
      self.window.add_buttons( gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
                               gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)

      self.window.connect("close", self.close)
      self.window.connect("response", self.response)

      # file chooser dialog and button
      self.filedialog = gtk.FileChooserDialog( "Choose a file", self.window,
                                               gtk.FILE_CHOOSER_ACTION_OPEN,
                                               (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
      self.filebutton = gtk.FileChooserButton(self.filedialog)
      self.filedialog.connect( "response", self.path_changed)

      # disposition selection combo
      self.combo = gtk.combo_box_new_text()
      self.combo.append_text("zoom")
      self.combo.append_text("centered")
      self.combo.append_text("stretched")
      self.combo.append_text("scaled")
      self.combo.append_text("wallpaper")
      self.combo.connect( "changed", self.disp_changed)

      i=0
      self.combo.set_active(i)
      while self.combo.get_active_text() != self.disp:
         i+=1
         self.combo.set_active( i )

      if self.path is not None:
         self.filedialog.set_filename(self.path)
      
      #self.window.set_border_width(4)
      
      # aux hbox
      self.hbox = gtk.HBox()
      self.hbox.pack_start(self.filebutton)
      self.hbox.pack_end(self.combo)
      self.hbox.set_border_width(5)

      # image frame
      self.frame = gtk.Frame()
      self.frame.set_shadow_type(gtk.SHADOW_IN)
      self.frame.set_border_width(6)
      self.frame.add(self.image)

      # the window vbox
      self.window.vbox.pack_start(self.frame)
      self.window.vbox.pack_start(self.hbox)

      self.frame.show()
      self.image.show()
      self.filebutton.show()
      self.combo.show()
      self.hbox.show()
      self.window.show()

   def main(self):
      # All PyGTK applications must have a gtk.main(). Control ends here
      # and waits for an event to occur (like a key press or mouse event).
      gtk.main()

if __name__ == "__main__":
    app = App()
    app.main()
