#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import sys
import re
import pygtk
pygtk.require('2.0')

import gtk
import commands

# Check for new pygtk: this is new class in PyGtk 2.4
if gtk.pygtk_version < (2,3,90):
   print "PyGtk 2.3.90 or later required for this example"
   raise SystemExit

class HelloWorld:
   pixbuf = None
   imagen = gtk.Image()
   ruta = "/home/mauro/Imágenes/art/4995443800_e68125ac35_o.jpg"
   conffile = "/home/mauro/git/greeter.gconf-defaults"
   layout = "zoom" #wallpaper, centered, scaled, stretched, zoom

   def dibujar_imagen(self):
      imagen_cargada = gtk.gdk.pixbuf_new_from_file(self.ruta)
      ancho_img = imagen_cargada.get_width()
      alto_img = imagen_cargada.get_height()

      ratio_disp = float(self.wscreen)/float(self.hscreen)
      ratio_imag = float(ancho_img)/float(alto_img)

      ancho_img_scaled = None
      alto_img_scaled = None

      self.pixbuf.fill(0x88888888)
      self.pixbuf.saturate_and_pixelate(self.pixbuf, 0.0, True)
      
      if self.layout == "zoom":
         if ratio_disp > ratio_imag:
            ancho_img_scaled = self.wscreen/4.0
            alto_img_scaled = alto_img*((self.wscreen/4.0)/ancho_img)
         else:
            alto_img_scaled = self.hscreen/4.0
            ancho_img_scaled = ancho_img*((self.hscreen/4.0)/alto_img)

         imagen_cargada = imagen_cargada.scale_simple(int(ancho_img_scaled),
                                                      int(alto_img_scaled),
                                                      gtk.gdk.INTERP_BILINEAR)
         imagen_cargada.copy_area( int((ancho_img_scaled-self.wscreen/4.0)/2),
                                   int((alto_img_scaled-self.hscreen/4.0)/2),
                                   int(self.wscreen/4), int(self.hscreen/4),
                                   self.pixbuf, 0, 0)
      elif self.layout == "scaled":
         scale_x = (self.wscreen/4.0)/ancho_img
         scale_y = (self.hscreen/4.0)/alto_img
         
         ancho_img_scaled = ancho_img*min(scale_x, scale_y)
         alto_img_scaled = alto_img*min(scale_x, scale_y)

         imagen_cargada = imagen_cargada.scale_simple(int(ancho_img_scaled),
                                                      int(alto_img_scaled),
                                                      gtk.gdk.INTERP_BILINEAR)
         imagen_cargada.copy_area( 0, 0, ancho_img_scaled, alto_img_scaled,
                                   self.pixbuf,
                                   int((self.wscreen/4-ancho_img_scaled)/2),
                                   int((self.hscreen/4-alto_img_scaled)/2))
      elif self.layout == "centered":
         imagen_cargada = imagen_cargada.scale_simple(int(ancho_img/4),
                                                      int(alto_img/4),
                                                      gtk.gdk.INTERP_BILINEAR)

         x0 = (self.wscreen-ancho_img)/8
         y0 = (self.hscreen-alto_img)/8
         
         imagen_cargada.copy_area( max(-x0,0), max(-y0,0),
                                   min(self.wscreen/4,ancho_img/4),
                                   min(self.hscreen/4,alto_img/4),
                                   self.pixbuf, max(x0,0), max(y0,0))
         print "copy_area(" + str(max(-x0,0)) + "," + str(max(-y0,0)) + "," \
         + str(min(self.wscreen/4,ancho_img/4)) + "," \
         + str(min(self.hscreen/4,alto_img/4)) + ",self.pixbuf," \
         + str(max(x0,0)) + "," + str(max(y0,0)) + ") " + str(x0) + " "\
         + str(y0) + " " + str(ancho_img) + " " + str(alto_img)
      elif self.layout == "stretched":
         imagen_cargada = imagen_cargada.scale_simple(self.wscreen/4,
                                                      self.hscreen/4,
                                                      gtk.gdk.INTERP_BILINEAR)
         imagen_cargada.copy_area( 0, 0,self.wscreen/4, self.hscreen/4,
                                   self.pixbuf, 0, 0)
                                   
      elif self.layout == "wallpaper":
         imagen_cargada = imagen_cargada.scale_simple(int(ancho_img/4),
                                                      int(alto_img/4),
                                                      gtk.gdk.INTERP_BILINEAR)
         x0=0
         while( x0 < self.wscreen ):
            y0=0
            while( y0 < self.hscreen):
               imagen_cargada.copy_area( 0, 0,
                                   min(self.wscreen/4-x0,ancho_img/4),
                                   min(self.hscreen/4-y0,alto_img/4),
                                   self.pixbuf, x0, y0)
               y0 += alto_img/4
            x0 += ancho_img/4
               
      self.imagen.set_from_pixbuf(self.pixbuf)


   def get_screen_size(self):
      (status,output)=commands.getstatusoutput('xwininfo -root|grep "geometry"')
      m1 = re.match(r".*geometry\s([0-9]+)x([0-9]+)\+.*", output)
      if m1:
         return (int(m1.group(1)), int(m1.group(2)))
      return (-1, -1)

   # This is a callback function. The data arguments are ignored
   # in this example. More on callbacks below.
   def hello(self, widget, data=None):
      print "Hello World"

   def delete_event(self, widget, event, data=None):
      #print "delete event occurred"
      # Change FALSE to TRUE and the main window will not be destroyed
      # with a "delete_event".
      return False

   def destroy(self, widget, data=None):
      print "destroy signal occurred"
      gtk.main_quit()

   def imagen_seleccionada( self, widget, response):
      if response == gtk.RESPONSE_ACCEPT:
         self.ruta = widget.get_filename()
         self.dibujar_imagen()

   def layout_cambiado( self, widget):
      self.layout = widget.get_active_text()
      self.dibujar_imagen()

   def leer_conf( self ):
      with open(self.conffile, 'r') as conf:
         for linea in conf:
            m1 = re.match(r"\s*/desktop/gnome/background/picture_filename\s+((?:\S*(?:(?<=\\)\s)*)+)", linea)
            m2 = re.match(r"\s*/desktop/gnome/background/picture_options\s+(\w+)", linea)
            if m1:
                  print "imagen encontrada. " + m1.group(1)
                  self.ruta = m1.group(1)
            elif m2:
               print "configuración encontrada: " + m2.group(1)
               self.layout = m2.group(1)

   def guardar_conf( self, widget ):
      with open(self.conffile, 'r') as conf:
         salida = ""
         for linea in conf:
            m1 = re.match(r"\s*/desktop/gnome/background/picture_filename\s+((?:\S*(?:(?<=\\)\s)*)+)", linea)
            m2 = re.match(r"\s*/desktop/gnome/background/picture_options\s+(\w+)", linea)
            if m1:
               salida += "/desktop/gnome/background/picture_filename " + self.ruta + "\n"
            elif m2:
               salida += "/desktop/gnome/background/picture_options " + self.layout + "\n"
            else:
               salida += linea

         with open(self.conffile, 'w') as f:
            f.write(salida)
            print "Se ha guardado la nueva configuración."

   def __init__(self):
 
      (self.wscreen, self.hscreen) = self.get_screen_size()

      self.leer_conf()

      self.pixbuf = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB, True, 8,
                                    int(self.wscreen/4.0),
                                    int(self.hscreen/4.0) )
      # create a new window
      self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
      # self.window.set_size_request(400,600)
      
      # The data passed to the callback
      # function is NULL and is ignored in the callback function.
      self.window.connect("delete_event", self.delete_event)
    
      # Here we connect the "destroy" event to a signal handler.  
      # This event occurs when we call gtk_widget_destroy() on the window,
      # or if we return FALSE in the "delete_event" callback.
      self.window.connect("destroy", self.destroy)
    
      # Sets the border width of the window.
      self.window.set_border_width(10)
    
      self.label = gtk.Label("<big><b>Elija la imagen nueva a mostrar</b></big>\n\
La imagen actualmente configurada es /home/mauro.")
      self.label.set_use_markup(True)

      # Creates a new button with the label "Hello World".
      self.button = gtk.Button("Hello World")
    
      self.button.connect("clicked", self.guardar_conf)
      #self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
      
      self.vbox = gtk.VBox();
      self.hbox = gtk.HBox();

      self.dibujar_imagen()

      self.filechooserdialog = gtk.FileChooserDialog("Elija un archivo",
                                                     self.window,
                                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                     (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                                      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
      self.filechooserbutton = gtk.FileChooserButton(self.filechooserdialog)
      self.filechooserdialog.connect("response", self.imagen_seleccionada)

      self.combo = gtk.combo_box_new_text()
      self.combo.append_text("zoom")
      self.combo.append_text("centered")
      self.combo.append_text("stretched")
      self.combo.append_text("scaled")
      self.combo.append_text("wallpaper")
      self.combo.connect("changed", self.layout_cambiado)

      self.vbox.pack_start(self.label)
      self.vbox.pack_start(self.imagen)
      self.vbox.pack_start(self.filechooserbutton)
      self.vbox.pack_start(self.hbox)
      self.hbox.pack_start(self.combo)
      self.hbox.pack_start(self.button)

      self.vbox.show()
      self.filechooserbutton.show()
      self.hbox.show()
      self.label.show()
      self.imagen.show()
      self.combo.show()

      self.window.add(self.vbox)
      
      # The final step is to display this newly created widget.
      self.button.show()
    
      # and the window
      self.window.show()

   def main(self):
      # All PyGTK applications must have a gtk.main(). Control ends here
      # and waits for an event to occur (like a key press or mouse event).
      gtk.main()

if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
