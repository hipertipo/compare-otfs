import os
import difflib
from fontTools.ttx import TTFont
from xml.etree.ElementTree import parse

HEAD = '''\
<head>
<meta charset="UTF-8">
<title>CompareOTFs</title>
<style type="text/css">
* {
  padding: 0;
  margin: 0;
}
body {
  font-size: 0.9em;
  padding: 0 0.7em;
}
colgroup, tbody, th, table, tr {
  border: none;
  border-collapse: collapse;
}
a {
  text-decoration: none;
  color: #888;
}
a:hover {
  text-decoration: none;
  color: blue;
}
table {
    margin: 0;
    padding: 0;
}
table.diff {
  font-family: 'Menlo', 'Consolas', monospaced;
  font-weight: bold;
  margin-bottom: 0.65em;
  border: 1px solid #CCC;
}
table.diff td, table.diff th {
  padding: 0.3em 0.7em;
  line-height: 1.3em;
  border: 1px solid #CCC;
}
/*
table.main tr > th {
  position: -webkit-sticky;
  position: -moz-sticky;
  position: -o-sticky;
  position: -ms-sticky;
  position: sticky;
  top: 3.4em;
  left: 0;
}
*/
table.main td:nth-child(1), table.main td:nth-child(4) {
    width: 4%;
}
table.main td:nth-child(2), table.main td:nth-child(5) {
    width: 6%;
    text-align: right;
}
table.main td:nth-child(3), table.main td:nth-child(6) {
    width: 40%;
}
table.main tr:not(:last-child) {
  border-bottom: 1px solid #CCC;
}
table.main {
  width: 100%;
}
#menu table {
  float: left;
  margin: 0.7em 0.7em 0.7em 0;
}
#menu {
  position: -webkit-sticky;
  position: -moz-sticky;
  position: -o-sticky;
  position: -ms-sticky;
  position: sticky;
  top: 0;
  left: 0;
  background: #FFF;
  margin: 0;
  padding: 0.7;
  height: 3.4em;
}
#caption {}
td.diff_header, td.diff_next, .selected, th {
  background-color: #eeeeee;
  color: #888;
}
td.diff_header, td.diff_next {
  font-weight: normal;
}
.diff_add  {
  background-color: #aaffaa;
}
.diff_chg  {
  background-color: #ffff77;
}
.diff_sub  {
  background-color: #ffaaaa;
}
</style>
</head>
'''

LEGENDS = '''\
<div id="caption">
<table class='diff'>
<tr>
<td class="diff_add">added</td>
<td class="diff_chg">changed</td>
<td class="diff_sub">deleted</td>
</tr>
</table>
</div>
'''

DOCSTRING = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
'''

# functions

def extract_tables(otf_path, folder, tables, n=None):
    """
    Extract font tables from an OpenType font.

    """
    ttfont = TTFont(otf_path)
    info_file = os.path.splitext(os.path.split(otf_path)[1])[0]

    if n is not None:
        info_path = os.path.join(folder, '%s_%s.xml' % (n, info_file))

    else:
        info_path = os.path.join(folder, '%s.xml' % info_file)

    ttfont.saveXML(info_path, tables=tables, splitTables=True)
    return info_path

def add_main_menu(html, tables, table_codes, selected=0):

    if len(tables):

        sections = {
            'overview' : 'index.html',
            'tables'   : sorted(tables.keys())[0] + '.html',
        }

        find     = '<body>\n'
        replace  = '<body>\n'
        replace += '<table class="diff">\n'
        replace += '<tr>\n'

        for i, section in enumerate(sections.keys()):

            if i == selected:
                replace += '<td class="selected"><a href="%s">%s</a></td>\n' % (sections[section], section)

            else:
                replace += '<td><a href="%s">%s</a></td>\n' % (sections[section], section)

        replace += '</tr>\n'
        replace += '</table>\n'
        html = html.replace(find, replace)

    return html

def add_tables_menu(html, tables, table_codes, selected=None):

    if len(tables):
        find = '<body>\n'
        replace  = '<body>\n'
        replace += '<table class="diff">\n'
        replace += '<tr>\n'

        for table in sorted(tables.keys()):
            if table  == selected:
                replace += '<td class="selected">%s</td>\n' % table_codes[table]
            else:
                replace += '<td><a href="%s.html">%s</a></td>\n' % (table, table_codes[table])

        replace += '</tr>\n'
        replace += '</table>\n'
        diff_html = html.replace(find, replace)

        return diff_html

def add_index_menu(html, tables, table_codes):

    if len(tables):
        find     = '<body>\n'
        replace  = '<body>\n'
        # replace += '<a name="top"></a>\n'
        replace += '<table class="diff">\n'
        replace += '<tr>\n'

        for table in sorted(tables.keys()):
            replace += '<td><a href="#%s">%s</a></td>\n' % (table, table_codes[table])

        replace += '</tr>\n'
        replace += '</table>\n'
        diff_html = html.replace(find, replace)

        return diff_html

def add_menu_wrapper(html):
    # add opening div tag
    find       = '</style>\n</head>\n<body>\n<table'
    replace    = '</style>\n</head>\n<body>\n<div id="menu">\n<table'
    diff_html  = html.replace(find, replace)
    # add closing div tag
    find       = '</table>\n<table class="diff main"'
    replace    = '</table>\n</div>\n<table class="diff main"'
    diff_html_ = diff_html.replace(find, replace)
    # done
    return diff_html_

def fix_captions_table(html):
    start     = html.find('<table class="diff" summary="Legends">')
    end       = html.find('</table>\n</body>')
    find      = html[start:end+8]
    replace   = LEGENDS
    diff_html = html.replace(find, replace)
    return diff_html

def fix_html_diff(diff_html, table_codes, tables, selected=None, headers=None):

    diff_html = clean_up_html(diff_html)
    diff_html = diff_html.replace('&nbsp;', ' ')
    diff_html = diff_html.replace('nowrap="nowrap"', '')

    # fix doctype
    find      = DOCSTRING
    replace   = "<!DOCTYPE html>\n"
    diff_html = diff_html.replace(find, replace)

    # fix stylesheet
    start     = diff_html.find('<head>')
    end       = diff_html.find('</head>')
    find      = diff_html[start:end+7]
    replace   = HEAD
    diff_html = diff_html.replace(find, replace)

    # add 'main' class
    find      = 'class="diff" id="difflib'
    replace   = 'class="diff main" id="difflib'
    diff_html = diff_html.replace(find, replace)

    # add menus
    diff_html = add_tables_menu(diff_html, tables, table_codes, selected=selected)
    diff_html = add_main_menu(diff_html, tables, table_codes, selected=1)

    # add file names
    if headers is not None and len(headers) == 2:
        file1, file2 = headers
        find     = '<tbody>\n'
        replace  = '<tbody>\n'
        replace += '<tr><th></th><th></th><th>%s</th><th></th><th></th><th>%s</th></tr>\n' % (file1, file2)
        diff_html = diff_html.replace(find, replace)

    # etc
    diff_html = fix_captions_table(diff_html)
    diff_html = clean_up_html(diff_html)
    diff_html = add_menu_wrapper(diff_html)

    return diff_html

def clean_up_html(html):
    _html = ''
    for line in html.split('\n'):
        line = line.strip()
        if len(line) > 0:
            _html += '%s\n' % line
    return _html

#---------
# objects
#---------

class CompareOTFs(object):

    table_codes = {
        'B_A_S_E_' : 'BASE',
        'C_B_D_T_' : 'CBDT',
        'C_B_L_C_' : 'CBLC',
        'C_F_F_'   : 'CFF ',
        'C_O_L_R_' : 'COLR',
        'C_P_A_L_' : 'CPAL',
        'D_S_I_G_' : 'DSIG',
        'E_B_D_T_' : 'EBDT',
        'E_B_L_C_' : 'EBLC',
        'F_F_T_M_' : 'FFTM',
        'G_D_E_F_' : 'GDEF',
        'G_M_A_P_' : 'GMAP',
        'G_P_K_G_' : 'GPKG',
        'G_P_O_S_' : 'GPOS',
        'G_S_U_B_' : 'GSUB',
        'J_S_T_F_' : 'JSTF',
        'L_T_S_H_' : 'LTSH',
        'M_A_T_H_' : 'MATH',
        'M_E_T_A_' : 'META',
        'O_S_2f_2' : 'OS/2',
        'S_I_N_G_' : 'SING',
        'S_V_G_'   : 'SVG ',
        # 'T_S_I_B_' : 'TSIB',
        # 'T_S_I_D_' : 'TSID',
        # 'T_S_I_J_' : 'TSIJ',
        # 'T_S_I_P_' : 'TSIP',
        # 'T_S_I_S_' : 'TSIS',
        # 'T_S_I_V_' : 'TSIV',
        # 'T_S_I__0' : 'TSI0',
        # 'T_S_I__1' : 'TSI1',
        # 'T_S_I__2' : 'TSI2',
        # 'T_S_I__3' : 'TSI3',
        # 'T_S_I__5' : 'TSI5',
        # 'V_D_M_X_' : 'VDMX',
        # 'V_O_R_G_' : 'VORG',
        # '_a_v_a_r' : 'avar',
        '_c_m_a_p' : 'cmap',
        '_c_v_t'   : 'cvt ',
        '_f_e_a_t' : 'feat',
        '_f_p_g_m' : 'fpgm',
        '_f_v_a_r' : 'fvar',
        '_g_a_s_p' : 'gasp',
        '_g_l_y_f' : 'glyf',
        '_g_v_a_r' : 'gvar',
        '_h_d_m_x' : 'hdmx',
        '_h_e_a_d' : 'head',
        '_h_h_e_a' : 'hhea',
        '_h_m_t_x' : 'hmtx',
        '_k_e_r_n' : 'kern',
        '_l_o_c_a' : 'loca',
        '_l_t_a_g' : 'ltag',
        '_m_a_x_p' : 'maxp',
        '_m_e_t_a' : 'meta',
        '_n_a_m_e' : 'name',
        '_p_o_s_t' : 'post',
        '_p_r_e_p' : 'prep',
        '_s_b_i_x' : 'sbix',
        '_t_r_a_k' : 'trak',
        '_v_h_e_a' : 'vhea',
        '_v_m_t_x' : 'vmtx',
    }

    table_names  = sorted(table_codes.values())
    clear_folder = True
    diff_mode    = None

    def __init__(self, otf1, otf2, folder):
        self.otf1 = otf1
        self.otf2 = otf2
        self.folder = folder

    @property
    def font1(self):
        return os.path.split(self.otf1)[1]

    @property
    def font2(self):
        return os.path.split(self.otf2)[1]

    @property
    def tables(self):
        tables = {}
        for f in os.listdir(self.folder):
            if os.path.splitext(f)[1] == '.xml':
                if len(f.split('.')) == 3:
                    font, table, _ = f.split('.')
                    if table not in tables:
                        tables[table] = {}
                    if font not in tables[table]:
                        file_path = os.path.join(self.folder, f)
                        tables[table]['%s.otf' % font] = file_path
        return tables

    @property
    def diffs(self):
        diffs = {}
        for table in self.tables:
            font1, font2 = sorted(self.tables[table].keys())
            with open(self.tables[table][font1], mode='r', encoding='utf-8') as f1:
                ttx1 = f1.readlines()
            with open(self.tables[table][font2], mode='r', encoding='utf-8') as f2:
                ttx2 = f2.readlines()

            if self.diff_mode == 'ndiff':
                diff = difflib.ndiff(ttx1, ttx2)
            else:
                diff = difflib.unified_diff(ttx1, ttx2, lineterm='')

            diff = ''.join(list(diff))
            diffs[table] = diff

        return diffs

    @property
    def html(self):

        htmls = {}
        for table in self.tables:
            font1, font2 = sorted(self.tables[table].keys())
            with open(self.tables[table][font1], mode='r', encoding='utf-8') as f1:
                ttx1 = f1.readlines()
            with open(self.tables[table][font2], mode='r', encoding='utf-8') as f2:
                ttx2 = f2.readlines()

            D = difflib.HtmlDiff()
            diff_html = D.make_file(ttx1, ttx2)
            diff_html = fix_html_diff(diff_html, self.table_codes, self.tables, selected=table, headers=[self.font1, self.font2])

            htmls[table] = diff_html

        return htmls

    def clear_folder(self):
        for f in os.listdir(self.folder):
            os.remove(os.path.join(self.folder, f))

    def extract_tables(self, clear=True):

        if not os.path.exists(self.folder):
            return

        if clear:
            self.clear_folder()

        extract_tables(self.otf1, self.folder, self.table_names, n=1)
        extract_tables(self.otf2, self.folder, self.table_names, n=2)

    def save_html(self, index=True, pages=True):

        print('comparing .otfs...\n')

        print('\totf 1:\n\t%s\n' % self.otf1)
        print('\totf 2:\n\t%s\n' % self.otf2)

        # save index
        if index:

            html  = '<!DOCTYPE html>\n'
            html += '<html>\n'
            html += HEAD
            html += '<body>\n'

            for table in sorted(self.diffs.keys()):

                html += '<table class="diff main">\n'
                html += '<tr><th><a name="%s">%s</a></th></tr>\n' % (table, self.table_codes[table]) # &nbsp;<a class="top" href="#top">[top]</a>

                for line in self.diffs[table].split('\n'):
                    if not len(line.strip()) == 0:

                        # line = line.replace('&', '&amp;')
                        line = line.replace('<', '&lt;')
                        line = line.replace('>', '&gt;')

                        if line.startswith('+'):
                            html += '<tr><td class="diff_add">%s</td></tr>\n' % line

                        elif line.startswith('-'):
                            html += '<tr><td class="diff_sub">%s</td></tr>\n' % line

                        else:
                            html += '<tr><td>%s</td></tr>\n' % line

                html += '</table>\n'

            html += '</body>\n'

            html = add_index_menu(html, self.tables, self.table_codes)
            html = add_main_menu(html, self.tables, self.table_codes, selected=0)

            html = clean_up_html(html)
            html = add_menu_wrapper(html)

            html_path = os.path.join(self.folder, 'index.html')
            with open(html_path, mode='w', encoding='utf-8') as html_file:
                print('\tsaving %s...' % os.path.split(html_path)[1])
                html_file.write(html)

        # save pages
        if pages:
            for table in self.html.keys():
                html_path = os.path.join(self.folder, '%s.html' % table)
                with  open(html_path, mode='w', encoding='utf-8') as html_file:
                    print('\tsaving %s...' % os.path.split(html_path)[1])
                    html_file.write(self.html[table])

        print('\n...done.\n')

    def compare(self):
        self.extract_tables()
