import logging.config
import os
import pathlib
import sys

from xhtml2pdf import pisa

logger = logging.getLogger('opti')


class DataObject:
    def __init__(self):
        return

    def __str__(self):
        return

class HTMLQuick:
    # If I just want to load in an HTML and immediately convert it
    # to PDF to see what it looks like, this is the class for me!
    def __init__(self,html_loc=None,terminate=False):
        if not os.path.exists(html_loc):
            print(f'Quick input file {html_loc} missing!')
            return
        h=HTML(template_loc=html_loc)
        h.html_lines=h.template_lines
        h.dump_to_pdf('quick.pdf')
        print(f'Quick HTML {html_loc} written to quick.pdf')
        if terminate:
            sys.exit(0)
        return

    def __str__(self):
        return


class HTML:
    def __init__(self, template_loc='template.html', data_path=None):
        self.html_lines=[]
        self.data = DataObject()
        rp = pathlib.Path(resource_path(template_loc))
        self.template_loc = os.path.abspath(rp)
        verify_file(self.template_loc, action='r')
        with open(self.template_loc, 'r') as fi:
            self.template_lines = [line.rstrip('\n') for line in fi.readlines()]
        return

    def __str__(self):
        return

    def grab_loops(self, lines):
        ret = {}
        inloop = False
        loop_lines = []
        for lidx, l_org in enumerate(lines):
            l = l_org.lstrip(' ').split()
            if len(l) >= 2 and (l[0] == '{%end' or l[0] + l[1] == '{%end'):
                ret.update({loop_name: {'lines': loop_lines, 'start': loop_start, 'end': lidx}})
                inloop = False
                loop_name = None
                loop_start = None
                continue
            if inloop:
                loop_lines.append(l_org)
                continue
            loop_name = None
            loop_start = None
            if len(l) >= 1 and l[0] == '{%start':
                loop_name = l[1]
            if len(l) >= 2 and l[0] + l[1] == '{%start':
                loop_name = l[2]
            if loop_name is None:
                continue
            inloop = True
            loop_start = lidx
            loop_lines = []
        return ret

    def replace_template_key(self, l, t_lab, val):
        try:
            ix1 = l.index('{{')
            ix2 = l.index('}}')
        except ValueError:
            return l
        return l[:ix1] + str(val) + l[ix2 + 2:]

    def find_next_template_key(self, l):
        try:
            ix1 = l.index('{{')
        except ValueError:
            return None
        ix2 = l.index('}}')
        t_lab = l[ix1 + 2:ix2].lstrip(' ').rstrip(' ')
        return t_lab

    def process_template(self):
        logger.debug(f'Processing {self.template_loc}')
        loops = self.grab_loops(self.template_lines)
        self.html_lines = []
        inloop = False
        for lidx, l in enumerate(self.template_lines):
            if inloop:
                if lidx <= loop_end:
                    continue
            inloop = False
            for loop_name in loops:
                loop = loops[loop_name]
                if loop['start'] == lidx:
                    loop_end = loop['end']
                    inloop = True
                    try:
                        loop_data = getattr(self.data, loop_name)
                        loop_res = self.spin_loop(loop, data=loop_data)
                        self.html_lines.extend(loop_res)
                    except AttributeError:
                        val = '---BAD LOOP NAME-' + loop_name + '---'
                        self.html_lines.append(val)
                    break
            if inloop:
                continue
            while True:
                t_lab = self.find_next_template_key(l)
                if t_lab is None:
                    break
                # If I find a colon in t_lab, then anything after is my formatting string.
                colon_loc = t_lab.find(':')
                format_mask=None
                if colon_loc >= 0:
                    format_mask=t_lab[colon_loc+1:]
                    t_lab=t_lab[:colon_loc]
                try:
                    val = getattr(self.data, t_lab)
                    if format_mask is not None:
                        val = apply_format(val, format_mask, var_label=t_lab)
                except AttributeError:
                    print(f'Unknown key: Line {lidx}: {t_lab}')
                    val = '---BAD ATTRIBUTE-' + t_lab + '---'
                l = self.replace_template_key(l, t_lab, val)
            self.html_lines.append(l)
        return

    def spin_loop(self, loop=None, data=None):
        ret = []
        odd = False
        for p in data:
            odd = not odd
            for ll in loop['lines']:
                while True:
                    t_lab = self.find_next_template_key(ll)
                    if t_lab is None:
                        ret.append(ll)
                        break
                    if t_lab.startswith('evenodd:'):
                        x = t_lab.split(':')
                        if odd:
                            val = x[1]
                        else:
                            val = x[2]
                        ll = self.replace_template_key(ll, t_lab, val)
                        continue
                    # If I find a colon in t_lab, then anything after is my formatting string.
                    colon_loc = t_lab.find(':')
                    format_mask = None
                    if colon_loc >= 0:
                        format_mask = t_lab[colon_loc + 1:]
                        t_lab = t_lab[:colon_loc]
                    try:
                        val = getattr(p, t_lab)
                        if format_mask is not None:
                            val=apply_format(val,format_mask,var_label=t_lab)
                    except AttributeError:
                        print(f'Input object has no attribute {t_lab}')
                        val = '---BAD ATTRIBUTE-' + t_lab + '---'
                    ll = self.replace_template_key(ll, t_lab, str(val))

            iii = 1
        return ret

    def dump_to_file(self, f):
        with open(f, 'w', encoding='utf-8') as fo:
            for l in self.html_lines:
                fo.write(l + '\n')

    def dump_to_pdf(self, fpdf):
        logger.debug(fpdf)
        self.dump_to_file('2.htm')
        x = os.access(fpdf, os.W_OK)
        with open('2.htm', 'r') as fi:
            try:
                with open(fpdf, 'wb') as fo:
                    pisa.CreatePDF(fi.read(), fo)
            except PermissionError:
                logger.error(f'File not writeable: {fpdf}')
        os.remove('2.htm')
        return


def verify_file(file=None, action=None, extra_text=''):
    action = action.lower()
    if action == 'r':
        action = 'read'
    if action == 'w':
        action = 'write'
    if action == 'read':
        if os.access(file, os.F_OK) and os.access(file, os.R_OK):
            return True
        logger.error(f'File {file} missing. ' + extra_text)
        sys.exit(1)
    # This tests for write access, but needs to be flessed out a bit to test for complex file permissions
    # problems, such as a file not existing, but being invisible because of read being denied.
    if action == 'write':
        if not os.access(file, os.F_OK) or os.access(file, os.W_OK):
            return True
        logger.error(f'No {action} permissions for file {file}. ' + extra_text)
        sys.exit(1)
    return


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def apply_format(v,f,var_label='None'):
    try:
        val = f'{v:{f}}'
    except ValueError:
        logger.warning(f'Data object attribute "{var_label}" is "{v}" and cannot be formatted with "{f}", written as-is.')
        val=v
    return val


if __name__ == '__main__':
    #h=HTMLQuick(html_loc='out.html',terminate=True)


    # make a dummy template file
    with open('template.html', 'w') as fo:
        fo.write('<style>\n')
        fo.write('p{font-size:20pt;color:#0a0;font-weight:bold;font-family:courier}\n')
        fo.write('@page{size:8.5in portrait; margin:1cm}\n')
        fo.write('@page landscape{size:11in landscape; margin:1cm}\n')
        fo.write('.page-break{page-break-after:always;}\n')
        fo.write('</style>\n')
        fo.write('<p>\n')
        fo.write('{{cust_name}}: {{user_count}} Opti users (they make {{product}})\n')
        fo.write('{%start phone_numbers loop}}\n')
        fo.write('<br>{{type}}: {{number}}\n')
        fo.write('{%end phone_numbers loop}}\n')
        fo.write('<br>Decimal rounding!\n')
        fo.write('<br>Regular: {{dec_num}}\n')
        fo.write('<br>2 places: {{dec_num:.2f}}\n')
        fo.write('<br>4 places: {{dec_num:.4f}}\n')
        fo.write('<br><br>Dec List Test: 3 decimal places\n')
        fo.write('{%start dec_num_list loop}}\n')
        fo.write('<br>{{dec_num}} = {{dec_num:.3f}} --> {{what}}\n')
        fo.write('{%end dec_num_list loop}}\n')
        fo.write('<p style=white-space:pre>12345678901234567890\n')
        fo.write('{{pad_int:>7}}</p>\n')
        fo.write('</p>\n')
        fo.write('<pdf:nexttemplate name="landscape" />\n')
        fo.write('<div class="page-break"></div>\n')
        fo.write('<p>This is a landscape page.</p>\n')

    # create an HTML object with the dummy template
    h = HTML(template_loc='template.html')

    # stock the data object with data
    h.data.cust_name = 'Crown'
    h.data.product = 'forklifts'
    h.data.user_count = 3
    h.data.dec_num = 3.141592653589793238
    h.data.dec_num = 'steve'
    h.data.pad_int=97
    # phone numbers will be a list. To get it to work with the HTML processor,
    # each item in the list much be another data object. The name of the list
    # has to match the loop name in the HTML template
    h.data.phone_numbers = []
    h.data.phone_numbers.append(DataObject())
    h.data.phone_numbers[0].number = '816-123-4567'
    h.data.phone_numbers[0].type = 'Office'
    h.data.phone_numbers.append(DataObject())
    h.data.phone_numbers[1].number = '816-987-6543'
    h.data.phone_numbers[1].type = 'Cell'
    h.data.dec_num_list=[]
    h.data.dec_num_list.append(DataObject())
    h.data.dec_num_list[0].dec_num=7.8974
    h.data.dec_num_list[0].what='Random number'
    h.data.dec_num_list.append(DataObject())
    h.data.dec_num_list[1].dec_num=2.45
    h.data.dec_num_list[1].what='Hamburgers Eaten'
    h.data.dec_num_list.append(DataObject())
    h.data.dec_num_list[2].dec_num=45.9999999
    h.data.dec_num_list[2].what='Weight Gained'
    h.data.dec_num_list.append(DataObject())
    h.data.dec_num_list[3].dec_num='string'
    h.data.dec_num_list[3].what='This is a string and cannot be formatted with .2f'

    # To review, here's what the HTML object data object looks like for THIS SPECIFIC test...
    # self.data  <- the parent data location
    # self.data.cust_name  <- a string with the name
    # self.data.product    <- a string with what they make
    # self.data.user_count <- and integer of how many opti users they have
    # self.data.phone_numbers  <- this is a list of DataObject objects. Each loop in the template must
    #                             have one of these lists. Each object in the list can have attributes
    #                             added to it to satisfy the requirements of the HTML template.
    # self.data.phone_numbers[n].number  <- a string with the phone number
    # self.data.phone_numbers[n].type    <- a string where the number goes to.

    h.process_template()

    h.dump_to_file('out.html')
    h.dump_to_pdf('out.pdf')

    sys.exit(0)
