
import os
import pprint
import random
import wx
import numpy

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import mir2
import mir
from matplotlib.colors import LogNorm
import main


class mirgui(wx.Frame):
    """ The main frame of the application
    """
    title = 'Music Search Application'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.data = [5, 6, 9, 14]
        
        self.create_menu()
        self.create_status_bar()
        
        self.create_main_panel()
        
        #self.textbox.SetValue(' '.join(map(str, self.data)))

        self.draw_figure()
        
        print 'Training.'
        self.musicsearch = main.Search(8, 32)
        for f in os.listdir('train'):
            print f
            x, fs, enc = mir.wavread('train/'+f)
            self.musicsearch.add(x, fs, f)
        print 'Done training.'

        

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()

        m_browse = menu_file.Append(-1, "&Import *.wav file...", "Shows a File Dialog")
        self.Bind(wx.EVT_MENU, self.openfile, m_browse)

        m_key = menu_file.Append(-1, "&Estimate Key...", "Estimates Key of the Entire wav file")
        self.Bind(wx.EVT_MENU, self.est_key, m_key)
        
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        
        menu_edit = wx.Menu()
        m_reset = menu_edit.Append(-1, "&Reset Parameters...", "Resets plot parameters to Default Values")
        self.Bind(wx.EVT_MENU, self.on_reset, m_reset)
        m_lognorm = menu_edit.AppendCheckItem(-1, "Log-Norm", "Plot gram values using Log Normalized spectrum")
        self.Bind(wx.EVT_MENU, self.on_log_norm, m_lognorm)

        m_WC1 = menu_edit.Append(-1, 'Adjust Input Plot', kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU,self.which_canvas1, m_WC1)
        m_WC2 = menu_edit.Append(-1, 'Adjust Output Plot', kind=wx.ITEM_RADIO)
        self.Bind(wx.EVT_MENU,self.which_canvas2, m_WC2)
        
        menu_help = wx.Menu()
        m_about = menu_help.Append(-1, "&About\tF1", "About the demo")
        self.Bind(wx.EVT_MENU, self.on_about, m_about)
        
        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_edit, "&Edit")
        self.menubar.Append(menu_help, "&Help")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        """ Creates the main panel with all the controls on it:
             * mpl canvas 
             * mpl navigation toolbar
             * Control panel for interaction
        """
        self.panel = wx.Panel(self)
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        self.canvas2= FigCanvas(self.panel, -1, self.fig)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        self.drawbutton = wx.Button(self.panel, -1, "Plot Gram")
        self.Bind(wx.EVT_BUTTON, self.on_draw_button, self.drawbutton)

        self.plot_select = ['Time Domain Signal', 'Spectrogram','Constant Q Spectrogram', 'Chromagram']
        self.combo = wx.ComboBox(self.panel, -1, pos = (0,400), choices = self.plot_select, style=wx.ALIGN_LEFT | wx.CB_READONLY)
        self.combo.SetSelection(2)        

        self.setbutton = wx.Button(self.panel, -1, "Set Parameters")
        self.Bind(wx.EVT_BUTTON, self.on_set_button, self.setbutton)

        self.record = wx.BitmapButton(self.panel, -1, wx.Bitmap('record.png'))
        self.Bind(wx.EVT_BUTTON, self.on_rec, self.record)
        
        self.play = wx.BitmapButton(self.panel, -1, wx.Bitmap('play.png'))
        self.Bind(wx.EVT_BUTTON, self.on_play, self.play)
        self.stop = wx.BitmapButton(self.panel, -1, wx.Bitmap('stop.png'))

        self.searchbutton = wx.Button(self.panel, -1, "Search Database")
        self.Bind(wx.EVT_BUTTON, self.search, self.searchbutton)

        
        self.searchbutton1 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name="1) Sonata in A Maj., Beethoven")
        self.searchbutton2 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "2) Polonaise in G Min., Chopin")
        self.searchbutton3 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "3) Rondo No. 5 in C# Min., Bartok")
        self.searchbutton4 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "1) Sonata in A Maj., Beethoven")
        self.searchbutton5 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "2) Polonaise in G Min., Chopin")
        self.searchbutton6 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "3) Rondo No. 5 in C# Min., Bartok")
        self.searchbutton7 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "1) Sonata in A Maj., Beethoven")
        self.searchbutton8 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "2) Polonaise in G Min., Chopin")
        self.searchbutton9 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "3) Rondo No. 5 in C# Min., Bartok")
        self.searchbutton10 = wx.Button(self.panel, -1, style=wx.BU_LEFT, name= "1) Sonata in A Maj., Beethoven")
        self.Sbuttonlist = [self.searchbutton1,self.searchbutton2,
                            self.searchbutton3,self.searchbutton4,
                            self.searchbutton5,self.searchbutton6,
                            self.searchbutton7,self.searchbutton8,
                            self.searchbutton9,self.searchbutton10]

        self.Bind(wx.EVT_BUTTON, self.getmeta1, self.searchbutton1)
        self.Bind(wx.EVT_BUTTON, self.getmeta2, self.searchbutton2)
        self.Bind(wx.EVT_BUTTON, self.getmeta3, self.searchbutton3)
        self.Bind(wx.EVT_BUTTON, self.getmeta4, self.searchbutton4)
        self.Bind(wx.EVT_BUTTON, self.getmeta5, self.searchbutton5)
        self.Bind(wx.EVT_BUTTON, self.getmeta6, self.searchbutton6)
        self.Bind(wx.EVT_BUTTON, self.getmeta7, self.searchbutton7)
        self.Bind(wx.EVT_BUTTON, self.getmeta8, self.searchbutton8)
        self.Bind(wx.EVT_BUTTON, self.getmeta9, self.searchbutton9)
        self.Bind(wx.EVT_BUTTON, self.getmeta10, self.searchbutton10)

        #self.plt_titlestr = ''
        #self.plot_title = wx.StaticText(self.panel, -1, 'text1',(30,15), style=wx.ALIGN_CENTRE)

        # Create the navigation toolbar, tied to the canvas
        #
        self.toolbar = NavigationToolbar(self.canvas)
        
        #
        # Layout with box sizers
        #

        flags = wx.ALIGN_LEFT | wx.ALL | wx.GROW
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox2 = wx.BoxSizer(wx.VERTICAL)
        self.vbox3 = wx.BoxSizer(wx.VERTICAL)
        
        self.vbox2.AddStretchSpacer(1)
        self.vbox2.Add(self.searchbutton1, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton2, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton3, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton4, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton5, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton6, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton7, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton8, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton9, 0, border=3, flag=flags)
        self.vbox2.Add(self.searchbutton10, 0, border=3, flag=flags)
        self.vbox2.AddStretchSpacer(1)

        self.vbox3.Add(self.canvas, 10, wx.RIGHT | wx.TOP | wx.ALIGN_RIGHT | wx.GROW)
        self.vbox3.Add(self.canvas2, 10, wx.RIGHT | wx.TOP | wx.ALIGN_RIGHT | wx.GROW)



        self.hbox2.Add(self.vbox2, 0, wx.LEFT | wx.TOP | wx.ALIGN_LEFT| wx.GROW)
        
        #self.panel.SetSizer(self.vbox)
        #self.vbox.Fit(self)
        self.hbox2.Add(self.vbox3, 10, wx.RIGHT | wx.TOP | wx.ALIGN_RIGHT | wx.GROW)

        self.vbox.Add(self.hbox2, 0, wx.LEFT | wx.TOP | wx.GROW)
        
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)
        self.vbox.AddSpacer(7)
        
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox.AddSpacer(15)
        self.hbox.Add(self.combo, 0, border=3, flag=flags)
        self.hbox.AddSpacer(30)
        self.hbox.Add(self.setbutton, 0, border = 3, flag=flags)
        self.hbox.AddSpacer(30)
        self.hbox.Add(self.drawbutton, 0, border=3, flag=flags)
        self.hbox.AddSpacer(30)
        self.hbox.Add(self.play, 0, flag = flags)
        self.hbox.Add(self.stop, 0, flag = flags)
        self.hbox.Add(self.record, 0, flag = flags)
        self.hbox.AddSpacer(30)
        self.hbox.Add(self.searchbutton, 0, border=3, flag=flags)
        self.hbox.AddSpacer(30)

        self.vbox.Add(self.hbox, 0, flag = wx.ALIGN_LEFT | wx.BOTTOM | wx.EXPAND |wx.GROW)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        self.mypath = None
        self.fsz = 0.040
        self.hop = 0.020
        self.fmax = 44100
        self.x, self.fs, self.nbits = mir2.wavread('default.wav')
        #self.tmax = round(float(len(self.x))/self.fs,2)
        self.rectime = 20
        self.tmax = self.rectime
        
        self.tmin = 0
        self.LG_flag = 0
        self.LG_str = None
        self.LG_vmin = 25
        self.LG_vmax = 50
        self.tmin_samp = None
        self.tmax_samp = None
        self.WC = 1
        #self.rec_input = mir2.wavread('default.wav')#None
        self.rec_input = None
        self.rankresults = [('Beethoven_vln_sonata5_Francescatti_01.wav',1),('adksfjghl',3)]

        self.dict = {'Beethoven_vln_sonata5_Zukerman_01.wav':
                     ('Sonata No. 5, Mvt. 1', 'L. V. Beethoven','F Major','Violin and Piano', 'Pinchas Zukerman'),
                     'Beethoven_vln_sonata5_Zukerman_02.wav':
                     ('Sonata No. 5, Mvt. 2', 'L. V. Beethoven','F Major','Violin and Piano', 'Pinchas Zukerman'),
                     'Beethoven_vln_sonata5_Zukerman_03.wav':
                     ('Sonata No. 5, Mvt. 3', 'L. V. Beethoven','F Major','Violin and Piano', 'Pinchas Zukerman'),
                     'Beethoven_vln_sonata5_Zukerman_04.wav':
                     ('Sonata No. 5, Mvt. 4', 'L. V. Beethoven','F Major','Violin and Piano', 'Pinchas Zukerman'),
                     'Beethoven_vln_sonata5_Zukerman_05.wav':
                     ('Sonata No. 5, Mvt. 5', 'L. V. Beethoven','F Major','Violin and Piano', 'Pinchas Zukerman'),
                     'Beethoven_vln_sonata5_Oistrakh_01.wav':
                     ('Sonata No. 5, Mvt. 1', 'L. V. Beethoven','F Major','Violin and Piano', 'David Oistrakh'),
                     'Beethoven_vln_sonata5_Oistrakh_02.wav':
                     ('Sonata No. 5, Mvt. 2', 'L. V. Beethoven','F Major','Violin and Piano', 'David Oistrakh'),
                     'Beethoven_vln_sonata5_Oistrakh_03.wav':
                     ('Sonata No. 5, Mvt. 3', 'L. V. Beethoven','F Major','Violin and Piano', 'David Oistrakh'),
                     'Beethoven_vln_sonata5_Oistrakh_04.wav':
                     ('Sonata No. 5, Mvt. 4', 'L. V. Beethoven','F Major','Violin and Piano', 'David Oistrakh'),
                     'Beethoven_vln_sonata5_Oistrakh_05.wav':
                     ('Sonata No. 5, Mvt. 5', 'L. V. Beethoven','F Major','Violin and Piano', 'David Oistrakh'),
                     'Beethoven_vln_sonata5_Francescatti_01.wav':
                     ('Sonata No. 5, Mvt. 1', 'L. V. Beethoven','F Major','Violin and Piano', 'Zino Francescatti'),
                     'Beethoven_vln_sonata5_Francescatti_02.wav':
                     ('Sonata No. 5, Mvt. 2', 'L. V. Beethoven','F Major','Violin and Piano', 'Zino Francescatti'),
                     'Beethoven_vln_sonata5_Francescatti_03.wav':
                     ('Sonata No. 5, Mvt. 3', 'L. V. Beethoven','F Major','Violin and Piano', 'Zino Francescatti'),
                     'Beethoven_vln_sonata5_Francescatti_04.wav':
                     ('Sonata No. 5, Mvt. 4', 'L. V. Beethoven','F Major','Violin and Piano', 'Zino Francescatti'),
                     'Beethoven_vln_sonata5_Francescatti_05.wav':
                     ('Sonata No. 5, Mvt. 5', 'L. V. Beethoven','F Major','Violin and Piano', 'Zino Francescatti'),
                     'Bach Vln Partita3 - Fischbach 2004 - 01.wav':
                     ('Partita No. 3 - Preludio', 'J. S. Bach', 'E Major', 'Violin', 'Garrett Fischbach'),
                     'Bach Vln Partita3 - Fischbach 2004 - 03.wav':
                     ('Partita No. 3 - Gavotte en Rondeau', 'J. S. Bach', 'E Major', 'Violin', 'Garrett Fischbach'),
                     'Bach Vln Sonata1 - Fischbach 2004 - 02.wav':
                     ('Sonata No. 1 - Fuga', 'J. S. Bach', 'G minor', 'Violin', 'Garrett Fischbach'),
                     'Bach Vln Partita3 - Milstein 1955 - 01.wav':
                     ('Partita No. 3 - Preludio', 'J. S. Bach', 'E Major', 'Violin', 'Nathan Milstein'),
                     'Bach Vln Partita3 - Milstein 1955 - 03.wav':
                     ('Partita No. 3 - Gavotte en Rondeau', 'J. S. Bach', 'E Major', 'Violin', 'Nathan Milstein'),
                     'Bach Vln Sonata1 - Milstein 1954 - 02.wav':
                     ('Sonata No. 1 - Fuga', 'J. S. Bach', 'G minor', 'Violin', 'Nathan Milstein'),
                     
                     'brahms_rhapsody_01.wav':
                     ('Brahms Rhapsody Op.79, No.2', 'J. Brahms','G minor','Piano','Lili Kraus'),

                     'brahms_rhapsody_02.wav':
                     ('Brahms Rhapsody Op.79, No.2', 'J. Brahms','G minor','Piano','Martha Argerich'),

                     'debussy_toccata.wav':
                     ('Debussy Toccata from Pour le Piano', 'C. Debussy','N/A','Piano','Boris Feiner'),

                     'dont_stop_believin.wav':
                     ('Don\'t Stop Believin\'', 'Journey','E major','Vocal, Guitar, Bass, Piano, Drums','Journey'),

                     'lady_madonna.wav':
                     ('Lady Madonna', 'The Beatles','E major','Vocal, Guitar, Bass, Piano, Saxophone, Drums','The Beatles'),

                     'let_it_be.wav':
                     ('Let it Be', 'The Beatles','C major','Vocal, Guitar, Bass, Piano, Drums','The Beatles'),

                     'moonlight.wav':
                     ('Beethoven Piano Sonata No.14', 'L. Beethoven','C# minor','Piano','Unknown'),

                     'office_theme.wav':
                     ('Theme from \'The Office\'', 'Unknown','G Major','Piano','Unknown'),

                     'konstantine.wav':
                     ('Konstantine', 'Andrew McMahon','D minor','Vocal, Piano','Something Corporate'),

                     }
                     
                     
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def draw_figure(self, i=0):
        """ Redraws the figure
        """
        if self.rec_input is None:
            return
        
        if self.mypath is None:
            self.mypath = 'default.wav'
        
        
        #self.x, self.fs, self.nbits = mir2.wavread(self.mypath)

        if self.WC == 2:
            path = 'train/'
            filename = self.rankresults[i][0]
            fullpath = path + filename
            self.x, self.fs, self.nbits = mir2.wavread(fullpath)

        if self.WC == 1:
            self.x = self.rec_input
            #self.x, self.fs, self.nbits = mir2.wavread(self.mypath)
            print 'storing rec_input'
        
        self.get_plot_type()

        G = 0

        self.tmax = float(len(self.x))/self.fs
        self.tmin_samp = int(self.tmin*self.fs)
        self.tmax_samp = int(self.tmax*self.fs)

        if self.tmax_samp > len(self.x):
            self.tmax_samp = len(self.x) - 1

        print self.x.shape, self.fs, self.fsz, self.hop
        if self.plot_type == 0:
            P = self.x[self.tmin_samp:self.tmax_samp]
        elif self.plot_type == 1:
            G = mir2.spectrogram(self.x,self.fs, framesz = self.fsz, hop=self.hop, tmin=self.tmin, tmax=self.tmax)
        elif self.plot_type == 2:
            G = mir2.qspectrogram(self.x,self.fs, framesz = self.fsz, hop=self.hop, tmin=self.tmin, tmax=self.tmax)
        elif self.plot_type == 3:
            G = mir2.chromagram(self.x,self.fs, framesz = self.fsz, hop=self.hop, tmin=self.tmin, tmax=self.tmax)

        #self.plot_titlestr = self.mypath + gramtype

        self.axes.clear()
        
        if self.plot_type == 0:
            self.axes.plot(P)
        elif self.plot_type == 1 or 2 or 3:
            
            if self.LG_flag == 0:
                self.LG_str = None
                self.axes.imshow(G.X, aspect='auto', interpolation ='nearest',origin='lower')
            elif self.LG_flag == 1:
                self.LG_str = 'LogNorm(vmin = 25, vmax = 50)'
                self.axes.imshow(G.X, aspect='auto', interpolation ='nearest',origin='lower', norm = LogNorm())  #vmin = self.LG_vmin, vmax = self.LG_vmax))
        #self.WC = 1

        if self.WC == 1:
            self.canvas.draw()
        if self.WC == 2:
            self.canvas2.draw()
            
    def which_canvas1(self, event):
        self.WC = 1

    def which_canvas2(self, event):
        self.WC = 2
    
    def on_draw_button(self, event):
        self.get_plot_type
        self.draw_figure()

    def search(self, event):
        self.ranklist = ['1) ','2) ','3) ','4) ','5) ','6) ','7) ','8) ','9) ','10) ']
        self.titlelist = ['Sonata', 'Polonaise in G Min., Chopin',
                           'Rondo No. 5 in C# Min., Bartok', 'Sonata in A Maj., Beethoven',
                           'Polonaise in G Min., Chopin', 'Rondo No. 5 in C# Min., Bartok',
                           'Sonata in A Maj., Beethoven', 'Polonaise in G Min., Chopin',
                           'Rondo No. 5 in C# Min., Bartok','Rondo No. 5 in C# Min., Bartok']
        self.rankresults = [('Beethoven_vln_sonata5_Francescatti_01.wav',1),('adksfjghl',3)]
        
        print self.rec_input.shape, self.fs
        
        for i in range(10):
            self.Sbuttonlist[i].SetLabel('')
            
        self.rankresults = self.musicsearch.query(self.rec_input, self.fs)
        print self.rankresults
        
        self.metalist = range(len(self.rankresults))
        
        for i in range(len(self.rankresults)):
            self.metalist[i] = self.dict[self.rankresults[i][0]]
        
        for i in range(min(10, len(self.metalist))):
            self.Sbuttonlist[i].SetLabel(self.ranklist[i] + self.metalist[i][0])
        
        #self.create_main_panel()
        self.WC = 2
        
        #self.getmeta1(None)
        

    def on_set_button(self, event):
        self.get_plot_type()
        
        params_box = ParamsDialog(self, -1, '', self.fsz, self.hop, self.tmin, self.tmax, self.plot_type)
        val = params_box.ShowModal()
        self.fsz, self.hop, self.tmin, self.tmax = params_box.return_params()
        self.draw_figure()
        
        params_box.Destroy()
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        dlg = wx.MessageDialog(
            self, 
            msg, 
            "Click!",
            wx.OK | wx.ICON_INFORMATION)

        dlg.ShowModal() 
        dlg.Destroy()        
    
    def on_text_enter(self, event):
        self.draw_figure()

    
    def openfile(self, event):
        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.wav", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            basename = os.path.basename(path)
            self.SetStatusText("You selected: %s" % basename)
        self.mypath = path
        self.x, self.fs, self.nbits = mir2.wavread(self.mypath)
        self.rec_input = self.x
        self.WC = 1
        self.on_reset(self)
        self.draw_figure()
        dlg.Destroy()

    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)

    def on_play(self,event):
        if self.WC == 2:
            mir2.play(self.x, self.fs)
        elif self.WC == 1:
            mir2.play(self.rec_input, self.fs)

    def on_rec(self,event):
        print 'Recording.'
        self.rec_input = mir.micread(self.rectime)
        self.WC = 1
        self.draw_figure()
        mir.play(self.rec_input, 44100)
        

    def est_key(self, event):
        self.statusbar.SetStatusText('Estimating Key...')
        keynum = mir2.Key(self.x, self.fs)
        keylist = ['C', 'C#','D','D#','E','F','F#','G','G#','A','A#','B']
        self.keystr = keylist[keynum]
        self.statusbar.SetStatusText('The Key is: ' + self.keystr)

    def on_exit(self, event):
        self.Destroy()

    def on_reset(self, event):
        self.fsz = 0.040
        self.hop = 0.020
        self.fmax = self.fs
        self.tmax = round(float(len(self.x))/self.fs,2)
        self.tmin = 0
        self.draw_figure()

    def on_log_norm(self, event):
        if self.LG_flag == 0:
            self.LG_flag = 1
        elif self.LG_flag == 1:
            self.LG_flag = 0
        self.draw_figure()
        
        
    def on_about(self, event):
        msg = """ Content-based musical search.\n Brennan Keegan, Steve Tjoa\n Signals and Information Group\n University of Maryland\n April 30, 2011 """
        dlg = wx.MessageDialog(self, msg, "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def get_plot_type(self):
        plotstr = self.combo.GetStringSelection()

        for x in range(len(self.plot_select)):
            if plotstr == self.plot_select[x]:
                self.plot_type = x

 
    def getmeta1(self, event):
        if self.searchbutton1.GetLabel() == '':
            return
        self.draw_figure(0)
        meta = self.metalist[0]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta2(self, event):
        if self.searchbutton2.GetLabel() == '':
            return
        self.draw_figure(1)
        meta = self.metalist[1]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta3(self, event):
        if self.searchbutton3.GetLabel() == '':
            return
        self.draw_figure(2)
        meta = self.metalist[2]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta4(self, event):
        if self.searchbutton4.GetLabel() == '':
            return
        self.draw_figure(3)
        meta = self.metalist[3]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
    def getmeta5(self, event):
        if self.searchbutton5.GetLabel() == '':
            return
        self.draw_figure(4)
        meta = self.metalist[4]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta6(self, event):
        if self.searchbutton6.GetLabel() == '':
            return
        self.draw_figure(5)
        meta = self.metalist[5]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta7(self, event):
        if self.searchbutton7.GetLabel() == '':
            return
        self.draw_figure(6)
        meta = self.metalist[6]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta8(self, event):
        if self.searchbutton8.GetLabel() == '':
            return
        self.draw_figure(7)
        meta = self.metalist[7]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta9(self, event):
        if self.searchbutton9.GetLabel() == '':
            return
        self.draw_figure(8)
        meta = self.metalist[8]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
        
    def getmeta10(self, event):
        if self.searchbutton10.GetLabel() == '':
            return
        self.draw_figure(9)
        meta = self.metalist[9]
        print meta
        metastr = 'Title: '+meta[0]+'\n\nComposer: '+meta[1]+'\n\nKey: '+meta[2]+'\n\nInstruments: '+meta[3]+'\n\nArtist: '+meta[4]
        dial = wx.MessageDialog(None, metastr, 'Piece Information', wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()
                    

class ParamsDialog(wx.Dialog):
    def __init__(self, parent, id, title, fsz, hop, tmin, tmax, plot_type):
        wx.Dialog.__init__(self, parent, id, title)#, size = (400,500))

        self.fsz, self.hop, self.tmin, self.tmax, self.plot_type = str(fsz), str(hop), str(tmin), str(tmax), plot_type
        
        if self.plot_type == 0:
            

            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            hbox2 = wx.BoxSizer(wx.HORIZONTAL)

            self.tmin_label = wx.StaticText(self, -1, "Start Time (sec):  ")
            self.tmin_box = wx.TextCtrl(self,-1, self.tmin,  style=wx.TE_PROCESS_ENTER)

            self.tmax_label = wx.StaticText(self, -1, "End Time (sec):  ")
            self.tmax_box = wx.TextCtrl(self,-1, self.tmax, style=wx.TE_PROCESS_ENTER)
            
            #self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.fsz)

            hbox1.AddSpacer(80)
            hbox1.Add(self.tmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox1.AddSpacer(3)
            hbox1.Add(self.tmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox2.AddSpacer(80)
            hbox2.Add(self.tmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox2.AddSpacer(9)
            hbox2.Add(self.tmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            sizer =  self.CreateButtonSizer(wx.CANCEL|wx.OK)

            vbox.AddSpacer(10)
            vbox.Add(hbox1, 1)
            vbox.Add(hbox2, 1)
            vbox.AddSpacer(15)
            vbox.Add(sizer, 0, wx.ALIGN_CENTER)
            vbox.AddSpacer(20)
            self.SetSizer(vbox)
            self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)

        elif self.plot_type == 1:

            self.fmin, self.fmax = '0.00', '44100'
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            hbox2 = wx.BoxSizer(wx.HORIZONTAL)
            hbox3 = wx.BoxSizer(wx.HORIZONTAL)
            hbox4 = wx.BoxSizer(wx.HORIZONTAL)
            hbox5 = wx.BoxSizer(wx.HORIZONTAL)
            hbox6 = wx.BoxSizer(wx.HORIZONTAL)
            
            self.fsz_label = wx.StaticText(self, -1, "Frame Size (sec):  ")
            self.fsz_box = wx.TextCtrl(self,-1, self.fsz,  style=wx.TE_PROCESS_ENTER)
            
            self.hop_label = wx.StaticText(self, -1, "Hop Size (sec):  ")
            self.hop_box = wx.TextCtrl(self,-1, self.hop, style=wx.TE_PROCESS_ENTER)
            
            self.tmin_label = wx.StaticText(self, -1, "Start Time (sec):  ")
            self.tmin_box = wx.TextCtrl(self,-1, self.tmin,  style=wx.TE_PROCESS_ENTER)

            self.tmax_label = wx.StaticText(self, -1, "End Time (sec):  ")
            self.tmax_box = wx.TextCtrl(self,-1, self.tmax, style=wx.TE_PROCESS_ENTER)

            self.fmin_label = wx.StaticText(self, -1, "Min Freq. (Hz):  ")
            self.fmin_box = wx.TextCtrl(self,-1, self.fmin,  style=wx.TE_PROCESS_ENTER)

            self.fmax_label = wx.StaticText(self, -1, "Max Freq. (Hz):  ")
            self.fmax_box = wx.TextCtrl(self,-1, self.fmax, style=wx.TE_PROCESS_ENTER)
            
            #self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.fsz)

            hbox1.AddSpacer(80)        
            hbox1.Add(self.fsz_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox1.Add(self.fsz_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox2.AddSpacer(80)
            hbox2.Add(self.hop_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox2.AddSpacer(13)
            hbox2.Add(self.hop_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox3.AddSpacer(80)
            hbox3.Add(self.tmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox3.AddSpacer(3)
            hbox3.Add(self.tmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox4.AddSpacer(80)
            hbox4.Add(self.tmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox4.AddSpacer(9)
            hbox4.Add(self.tmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox5.AddSpacer(80)
            hbox5.Add(self.fmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox5.AddSpacer(13)
            hbox5.Add(self.fmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox6.AddSpacer(80)
            hbox6.Add(self.fmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox6.AddSpacer(9)
            hbox6.Add(self.fmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            sizer =  self.CreateButtonSizer(wx.CANCEL|wx.OK)

            space = 10
            
            vbox.AddSpacer(10)
            vbox.Add(hbox1, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox2, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox3, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox4, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox5, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox6, 1)
            vbox.AddSpacer(15)
            vbox.Add(sizer, 0, wx.ALIGN_CENTER)
            vbox.AddSpacer(20)
            self.SetSizer(vbox)
            self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)

        elif self.plot_type == 2:

            self.fmin, self.fmax = '0', '136'
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            hbox2 = wx.BoxSizer(wx.HORIZONTAL)
            hbox3 = wx.BoxSizer(wx.HORIZONTAL)
            hbox4 = wx.BoxSizer(wx.HORIZONTAL)
            hbox5 = wx.BoxSizer(wx.HORIZONTAL)
            hbox6 = wx.BoxSizer(wx.HORIZONTAL)
            
            self.fsz_label = wx.StaticText(self, -1, "Frame Size (sec):  ")
            self.fsz_box = wx.TextCtrl(self,-1, self.fsz,  style=wx.TE_PROCESS_ENTER)
            
            self.hop_label = wx.StaticText(self, -1, "Hop Size (sec):  ")
            self.hop_box = wx.TextCtrl(self,-1, self.hop, style=wx.TE_PROCESS_ENTER)
            
            self.tmin_label = wx.StaticText(self, -1, "Start Time (sec):  ")
            self.tmin_box = wx.TextCtrl(self,-1, self.tmin,  style=wx.TE_PROCESS_ENTER)

            self.tmax_label = wx.StaticText(self, -1, "End Time (sec):  ")
            self.tmax_box = wx.TextCtrl(self,-1, self.tmax, style=wx.TE_PROCESS_ENTER)

            self.fmin_label = wx.StaticText(self, -1, "Min Pitch (MIDI):  ")
            self.fmin_box = wx.TextCtrl(self,-1, self.fmin,  style=wx.TE_PROCESS_ENTER)

            self.fmax_label = wx.StaticText(self, -1, "Max Pitch (MIDI):  ")
            self.fmax_box = wx.TextCtrl(self,-1, self.fmax, style=wx.TE_PROCESS_ENTER)
            
            #self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.fsz)

            hbox1.AddSpacer(80)        
            hbox1.Add(self.fsz_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox1.Add(self.fsz_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox2.AddSpacer(80)
            hbox2.Add(self.hop_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox2.AddSpacer(13)
            hbox2.Add(self.hop_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox3.AddSpacer(80)
            hbox3.Add(self.tmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox3.AddSpacer(3)
            hbox3.Add(self.tmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox4.AddSpacer(80)
            hbox4.Add(self.tmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox4.AddSpacer(9)
            hbox4.Add(self.tmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox5.AddSpacer(80)
            hbox5.Add(self.fmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox5.AddSpacer(13)
            hbox5.Add(self.fmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox6.AddSpacer(80)
            hbox6.Add(self.fmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox6.AddSpacer(9)
            hbox6.Add(self.fmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            sizer =  self.CreateButtonSizer(wx.CANCEL|wx.OK)

            space = 10
            
            vbox.AddSpacer(10)
            vbox.Add(hbox1, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox2, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox3, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox4, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox5, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox6, 1)
            vbox.AddSpacer(15)
            vbox.Add(sizer, 0, wx.ALIGN_CENTER)
            vbox.AddSpacer(20)
            self.SetSizer(vbox)
            self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)

        elif self.plot_type == 3:

            self.fmin, self.fmax = 'C', 'B'
            
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox1 = wx.BoxSizer(wx.HORIZONTAL)
            hbox2 = wx.BoxSizer(wx.HORIZONTAL)
            hbox3 = wx.BoxSizer(wx.HORIZONTAL)
            hbox4 = wx.BoxSizer(wx.HORIZONTAL)
            hbox5 = wx.BoxSizer(wx.HORIZONTAL)
            hbox6 = wx.BoxSizer(wx.HORIZONTAL)
            
            self.fsz_label = wx.StaticText(self, -1, "Frame Size (sec):  ")
            self.fsz_box = wx.TextCtrl(self,-1, self.fsz,  style=wx.TE_PROCESS_ENTER)
            
            self.hop_label = wx.StaticText(self, -1, "Hop Size (sec):  ")
            self.hop_box = wx.TextCtrl(self,-1, self.hop, style=wx.TE_PROCESS_ENTER)
            
            self.tmin_label = wx.StaticText(self, -1, "Start Time (sec):  ")
            self.tmin_box = wx.TextCtrl(self,-1, self.tmin,  style=wx.TE_PROCESS_ENTER)

            self.tmax_label = wx.StaticText(self, -1, "End Time (sec):  ")
            self.tmax_box = wx.TextCtrl(self,-1, self.tmax, style=wx.TE_PROCESS_ENTER)

            self.fmin_label = wx.StaticText(self, -1, "Min Pitch (Note):  ")
            self.fmin_box = wx.TextCtrl(self,-1, self.fmin,  style=wx.TE_PROCESS_ENTER)

            self.fmax_label = wx.StaticText(self, -1, "Max Pitch (Note):  ")
            self.fmax_box = wx.TextCtrl(self,-1, self.fmax, style=wx.TE_PROCESS_ENTER)
            
            #self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.fsz)

            hbox1.AddSpacer(80)        
            hbox1.Add(self.fsz_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox1.Add(self.fsz_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox2.AddSpacer(80)
            hbox2.Add(self.hop_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox2.AddSpacer(13)
            hbox2.Add(self.hop_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox3.AddSpacer(80)
            hbox3.Add(self.tmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox3.AddSpacer(3)
            hbox3.Add(self.tmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox4.AddSpacer(80)
            hbox4.Add(self.tmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox4.AddSpacer(9)
            hbox4.Add(self.tmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox5.AddSpacer(80)
            hbox5.Add(self.fmin_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox5.AddSpacer(13)
            hbox5.Add(self.fmin_box, 1, wx.ALIGN_CENTER|wx.TOP)
            hbox6.AddSpacer(80)
            hbox6.Add(self.fmax_label, 1, wx.ALIGN_CENTER | wx.TOP)
            hbox6.AddSpacer(9)
            hbox6.Add(self.fmax_box, 1, wx.ALIGN_CENTER|wx.TOP)
            sizer =  self.CreateButtonSizer(wx.CANCEL|wx.OK)

            space = 10
            
            vbox.AddSpacer(10)
            vbox.Add(hbox1, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox2, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox3, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox4, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox5, 1)
            vbox.AddSpacer(space)
            vbox.Add(hbox6, 1)
            vbox.AddSpacer(15)
            vbox.Add(sizer, 0, wx.ALIGN_CENTER)
            vbox.AddSpacer(20)
            self.SetSizer(vbox)
            self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)


        
        

    def OnOK(self, event):
        if self.plot_type != 0:
            self.fsz = float(self.fsz_box.GetValue())
            self.hop = float(self.hop_box.GetValue())
        self.tmin =float(self.tmin_box.GetValue())
        self.tmax =float(self.tmax_box.GetValue())
        
        self.Close()

    def return_params(self):
        return self.fsz, self.hop, self.tmin, self.tmax

if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = mirgui()
    app.frame.Show()
    app.frame.Maximize()
    app.MainLoop()
