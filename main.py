import sys

import reportlab.graphics.barcode.code128
import reportlab.graphics.barcode.code39
import reportlab.graphics.barcode.code93
import reportlab.graphics.barcode.common
import reportlab.graphics.barcode.ecc200datamatrix
import reportlab.graphics.barcode.usps
import reportlab.graphics.barcode.usps4s

import ZohoCRM
import ui

# This is a bunch of stuff that autopytoexe needs
x = reportlab.graphics.barcode.code128
x = reportlab.graphics.barcode.code39
x = reportlab.graphics.barcode.code93
x = reportlab.graphics.barcode.common
x = reportlab.graphics.barcode.ecc200datamatrix
x = reportlab.graphics.barcode.usps
x = reportlab.graphics.barcode.usps4s
del x

# import Opti_HTML_Class
# h = Opti_HTML_Class.HTMLQuick(html_loc="debug.html", terminate=True)

z = ZohoCRM.ZohoCRM()
z.get_accounts()
z.get_install_price()

c_list, loc = ui.cust_list_read(z)
if c_list is None:
    sys.exit(0)
valid, errored = z.verify_customer(c_list)

event, values = ui.folder_read(loc, z, valid, errored)
if event == 'Exit':
    sys.exit(0)
for customer in valid:
    customer.create_pdf(date=values['date'], folder=values['folder'], zoho=z, list_price=values['list_price'])
ii = 1
