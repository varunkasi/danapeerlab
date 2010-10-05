def __init__(self):
    self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.maximize()
    self.window.connect("delete_event",self.delete_event)
    self.window.connect("destroy",self.destroy)

    hbox=gtk.HBox(False,1)
    vbox=gtk.VBox(False,1)
    hbox.pack_start(vbox,False,False,0)
    vbox.show()
    for i in xrange(100):
        label=gtk.Label(str(i))
        vbox.pack_start(label,False,False,0)
        label.show()


    vbox=gtk.VBox(False,1)
    hbox.pack_start(vbox,False,False,0)
    vbox.show()
    vscrollbar = gtk.VScrollbar()
    vbox.pack_start(vscrollbar,True,True,0)
    vscrollbar.show()

    hbox.show()
    self.window.add(hbox)
    self.window.show()