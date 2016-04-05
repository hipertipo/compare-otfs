import lib
reload(lib)

import os

from vanilla import *
from vanilla.dialogs import getFile, getFolder

from mojo.UI import HTMLView
from mojo.extensions import getExtensionDefault, setExtensionDefault

from lib import CompareOTFs

#---------
# objects
#---------

class CompareOTFsDialog(object):

    padding         = 10
    width           = 960
    height          = 640
    text_height     = 23
    button_width    = 90
    button_width_2  = 105
    drawer_width    = 180

    title           = "CompareOTFs"
    extension_key   = 'com.hipertipo.compareotfs'

    otf_1           = None
    otf_2           = None
    folder          = None

    drawer_open     = False

    tables  = [
        ('BASE', 'BASE', False),
        ('CBDT', 'CBDT', False),
        ('CBLC', 'CBLC', False),
        ('CFF ', 'CFF_', True ),
        ('COLR', 'COLR', False),
        ('CPAL', 'CPAL', False),
        ('DSIG', 'DSIG', False),
        ('EBDT', 'EBDT', False),
        ('EBLC', 'EBLC', False),
        ('FFTM', 'FFTM', False),
        ('GDEF', 'GDEF', False),
        ('GMAP', 'GMAP', False),
        ('GPKG', 'GPKG', False),
        ('GPOS', 'GPOS', False),
        ('GSUB', 'GSUB', False),
        ('JSTF', 'JSTF', False),
        # ('LTSH', 'LTSH', False),
        ('MATH', 'MATH', False),
        ('META', 'META', False),
        ('OS/2', 'OS_2', True ),
        ('SING', 'SING', False),
        ('SVG ', 'SVG_', False),
        # ('TSIB', 'TSIB', False),
        # ('TSID', 'TSID', False),
        # ('TSIJ', 'TSIJ', False),
        # ('TSIP', 'TSIP', False),
        # ('TSIS', 'TSIS', False),
        # ('TSIV', 'TSIV', False),
        # ('TSI0', 'TSI0', False),
        # ('TSI1', 'TSI1', False),
        # ('TSI2', 'TSI2', False),
        # ('TSI3', 'TSI3', False),
        # ('TSI5', 'TSI5', False),
        ('VDMX', 'VDMX', False),
        ('VORG', 'VORG', False),
        ('avar', 'avar', False),
        ('cmap', 'cmap', True ),
        ('cvt ', 'cvt_', False),
        ('feat', 'feat', False),
        ('fpgm', 'fpgm', False),
        ('fvar', 'fvar', False),
        ('gasp', 'gasp', False),
        ('glyf', 'glyf', False),
        ('gvar', 'gvar', False),
        ('hdmx', 'hdmx', False),
        ('head', 'head', True ),
        ('hhea', 'hhea', True ),
        ('hmtx', 'hmtx', False),
        ('kern', 'kern', False),
        ('loca', 'loca', False),
        ('ltag', 'ltag', False),
        ('maxp', 'maxp', False),
        ('meta', 'meta', False),
        ('name', 'name', True ),
        ('post', 'post', False),
        ('prep', 'prep', False),
        ('sbix', 'sbix', False),
        ('trak', 'trak', False),
        ('vhea', 'vhea', False),
        ('vmtx', 'vmtx', False),
    ]

    def __init__(self):

        self.tabs_height = 500

        # make window
        self.w = Window((self.width, self.height), self.title, minSize=(self.width, self.height))

        x = self.padding
        y = self.padding

        # otf 1

        self.w.otf_1_button = Button(
            (x, y, self.button_width, self.text_height),
            'get font 1...',
            sizeStyle='small',
            callback=self.get_otf_1_callback)
        x += self.button_width
        self.w.otf_1_status = TextBox(
            (x+5, y+3, 80, self.text_height),
            '%s' % unichr(10007)
        )

        # otf 2

        x += self.padding + self.text_height
        self.w.otf_2_button = Button(
            (x, y, self.button_width, self.text_height),
            'get font 2...',
            sizeStyle='small',
            callback=self.get_otf_2_callback)
        x += self.button_width
        self.w.otf_2_status = TextBox(
            (x+5, y+3, 80, self.text_height),
            '%s' % unichr(10007)
        )

        # output folder

        x += self.padding + self.text_height
        self.w.folder_button = Button(
            (x, y, self.button_width, self.text_height),
            'get folder...',
            sizeStyle='small',
            callback=self.get_folder_callback)
        x += self.button_width
        self.w.folder_status = TextBox(
            (x+5, y+3, 80, self.text_height),
            '%s' % unichr(10007)
        )

        # open drawer button

        x += self.padding + self.text_height * 2
        self.w.drawer_button = Button(
            (x, y, self.button_width_2, self.text_height),
            u"select tables %s" % unichr(8674),
            sizeStyle='small',
            callback=self.open_drawer_callback)

        # apply button

        x = -(self.button_width_2 + self.padding + self.text_height)
        self.w.compare_button = Button(
            (x, y, self.button_width_2, self.text_height),
            "compare fonts",
            sizeStyle='small',
            callback=self.compare_fonts_callback)
        x += self.button_width_2
        self.w.compare_status = TextBox(
            (x+5, y+3, 80, self.text_height),
            '%s' % unichr(10007)
        )

        # HTMLView

        x  = 0
        y += self.text_height + self.padding
        self.w.html_view = HTMLView(
            (x, y, -0, -0)
        )
        # self.w.html_view.setHTMLPath()

        # drawer with tables

        self.d = Drawer(
            (self.drawer_width, self.height),
            self.w, preferredEdge='right')

        x = self.padding * 2
        y = self.padding

        checkbox_width  = (self.drawer_width - self.padding * 4) / 2

        # build checkboxes
        i = 0
        for name, attr, value in self.tables:
            checkbox = CheckBox((x, y, checkbox_width, self.text_height), name, value=value)
            setattr(self.d, '_' + attr, checkbox)

            if i < (len(self.tables) / 2) - 1:
                y += self.text_height
                i += 1

            else:
                x += checkbox_width + self.padding
                y = self.padding
                i = 0

        # open window

        self.get_defaults()
        self.w.open()

    #-----------
    # callbacks
    #-----------

    def get_otf_1_callback(self, sender):
        otf_1 = getFile(
            messageText='choose a first .otf font',
            title=self.title,
            allowsMultipleSelection=False)
        if otf_1 is not None:
            otf_1 = otf_1[0]
            if len(otf_1) > 0:
                self.otf_1 = otf_1
                if os.path.exists(self.otf_1):
                    setExtensionDefault('%s.otf_1' % self.extension_key, self.otf_1)
                    self.w.otf_1_status.set('%s' % unichr(10003))

    def get_otf_2_callback(self, sender):
        otf_2 = getFile(
            messageText='choose a first .otf font',
            title=self.title,
            allowsMultipleSelection=False)
        if otf_2 is not None:
            otf_2 = otf_2[0]
            if len(otf_2) > 0:
                self.otf_2 = otf_2
                if os.path.exists(self.otf_2):
                    setExtensionDefault('%s.otf_2' % self.extension_key, self.otf_2)
                    self.w.otf_2_status.set('%s' % unichr(10003))

    def get_folder_callback(self, sender):
        folder = getFolder(
            messageText='choose a folder for the output files',
            title=self.title,
            allowsMultipleSelection=False)
        if folder is not None:
            folder = folder[0]
            if len(folder) > 0:
                self.folder = folder
                if os.path.exists(self.folder):
                    setExtensionDefault('%s.folder' % self.extension_key, self.folder)
                    self.w.folder_status.set('%s' % unichr(10003))

    def open_drawer_callback(self, sender):
        self.d.toggle()
        if self.drawer_open:
            self.drawer_open = False
            self.w.drawer_button.setTitle(u"select tables %s" % unichr(8674))
        else:
            self.drawer_open = True
            self.w.drawer_button.setTitle(u"select tables %s" % unichr(8672))

    def compare_fonts_callback(self, sender):

        # check for None values
        # confirm all files and folders exist
        if self.otf_1 is not None and os.path.exists(self.otf_1) and \
            self.otf_2 is not None and os.path.exists(self.otf_2) and \
            self.folder is not None and os.path.exists(self.folder):

            # get selected tables
            tables = []
            for table, attr, _ in self.tables:
                exec "value = self.d._%s.get()" % attr
                if value == True:
                    tables.append(table)

            # compare otfs
            C = CompareOTFs(self.otf_1, self.otf_2, self.folder)
            C.table_names = tables
            C.compare()
            C.save_html(index=True, pages=True)

            # display html result
            html_path = os.path.join(self.folder, 'index.html')
            if os.path.exists(html_path):
                self.w.compare_status.set('%s' % unichr(10003))
                self.w.html_view.setHTMLPath(html_path)

    def get_defaults(self):

        otf_1  = getExtensionDefault('%s.otf_1'  % self.extension_key, None)
        otf_2  = getExtensionDefault('%s.otf_2'  % self.extension_key, None)
        folder = getExtensionDefault('%s.folder' % self.extension_key, None)

        if os.path.exists(otf_1):
            self.otf_1 = otf_1
            self.w.otf_1_status.set('%s' % unichr(10003))

        if os.path.exists(otf_2):
            self.otf_2 = otf_2
            self.w.otf_2_status.set('%s' % unichr(10003))

        if os.path.exists(folder):
            self.folder = folder
            self.w.folder_status.set('%s' % unichr(10003))

#------
# run!
#------

CompareOTFsDialog()
