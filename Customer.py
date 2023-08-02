import Opti_HTML_Class
import pathlib
import ast



class Customer:
    def __init__(self, customer_info, rate, discount):


        self.install_list = []
        self.service_install = []
        self.company_name = customer_info['Account_Name']
        self.valid = None
        self.rate = rate
        self.discount = discount

        try:
            self.renewal_period = customer_info['Renewal_Period']
        except KeyError:
            self.renewal_period = None
        try:
            self.discount = customer_info['Discount']
        except KeyError:
            self.discount= 0.0
        try:
            self.renewal_month = customer_info['Renewal_Month']
        except KeyError:
            self.renewal_month = None
    #IF RATE DOES NOT EXIST WE SET TO 0 OTHERWISE MAINTENANCE
        if self.rate is None:
            self.rate = 0.0
        else:
            self.rate = self.rate
        return

    def create_pdf(self, folder=None, date=None, type=None, zoho=None, list_price=None, service_list=None):
        year = date[:4]
        total: int = 0
        service_total: int = 0
        self.install_list=sorted(self.install_list,key=lambda x: x['Date_Purchased'])
        p = self.rate
        d = self.discount
        a = self.renewal_period
        PoNumber = None
        html = Opti_HTML_Class.HTML(template_loc='./config/template.html')
        html.data.opti_logo=Opti_HTML_Class.resource_path('./config/opti.png')
        folder = pathlib.Path(folder).absolute()
        html.data.folder = folder.joinpath(self.company_name+'.pdf')
        html.data.year = year
        html.data.type = type
        html.data.name = self.company_name
        html.data.install_list = []
        html.data.service_install =[]
        html.data.rate = self.rate * 100
        html.data.renewal_month = self.renewal_month
        html.data.renewal_period = self.renewal_period


        if a == 'Quarterly':
            b = 4
        elif a == 'Semi-Annually':
            b = 2
        else:
            b = 1
        if self.discount > 0.0:
            html.data.discount = 'Corporate Discount: ' + str(self.discount) + '%'
        else:
            html.data.discount = " "
#        if self.service_install

#   ADD SERVICE INSTALLS TO THE BOTTOM OF THE PDF
        for s in self.service_install:
            install_ob = Opti_HTML_Class.DataObject()
            # IGNORING MISSING ITEM CODES NEEDS SOME LOVE FOR FUTURE
            install_ob.date_purchased = '-'
            install_ob.description = '-'
            install_ob.po_number = '-'
            install_ob.cost = '-'
            install_ob.quantity = 12
            try:
                install_ob.date_purchased = s['Date_Purchased']
            except KeyError:
                pass
            try:
                install_ob.description = s['Name']
            except KeyError:
                pass
            try:
                install_ob.po_number = s['PO_Number']
            except KeyError:
                pass
            try:
                install_ob.price = s['Unit_Price']
            except KeyError:
                pass
            try:
                if service_list is False:
                    install_ob.price = 0
                    price2 = install_ob.price
                    install_ob.date_purchased = " "
                    install_ob.description = " "
                    install_ob.quantity = 1
                    install_ob.percent = " "
                    install_ob.cost = 0
                else:
                    price2 = zoho.product_list.get_price(s['Item_Code1'])
                    install_ob.price = int(price2)
            except KeyError:
                pass

            try:
                if s['Inactive'] is True:
                    price2 = 0
                    install_ob.price = price2
                    install_ob.percent = 'N/A'
                    install_ob.quantity = 1
                    install_ob.cost = 0
                else:
                    install_ob.price = price2
            except KeyError:
                pass

            cost = price2 * install_ob.quantity
            service_total += cost
            install_ob.cost= cost
            html.data.service_install.append(install_ob)

        for i in self.install_list:
            install_ob = Opti_HTML_Class.DataObject()
            try:
                 if list_price is False:
                    install_ob.price = i['Purchase_Price']
                    price = install_ob.price
                 else:
                    price = zoho.product_list.get_price(i['Item_Code'])
                    install_ob.price = price
            except KeyError:
                install_ob.price = 0
                price = 0
                    # IGNORING MISSING ITEM CODES NEEDS SOME LOVE FOR FUTURE
            install_ob.date_purchased = '-'
            install_ob.description = '-'
            install_ob.po_number = '-'
            try:
                install_ob.date_purchased = i['Date_Purchased']
            except KeyError:
                pass
            try:
                install_ob.description = i['Name']
            except KeyError:
                pass
            try:
                install_ob.po_number = i['PO_Number']
            except KeyError:
                pass
            try:
                install_ob.quantity = i['Q2']
                multi = i['Q2']
            except KeyError:
                install_ob.quantity = 1
                multi = 1
                pass
            # if customer is under maintenance but does not have price it provide N/A
            if i['Maintenance']:
                install_ob.cost = 'N/A'
                install_ob.percent = 'N/A'
            else:
                install_ob.cost = f'$ {price :,.2f}'
                install_ob.percent = f'$ {(price * multi) * p:,.2f}'
                total += ((price * multi) * p)
            if install_ob.po_number != PoNumber:
                PoNumber = install_ob.po_number
            else:
                install_ob.date_purchased = ' '
            html.data.install_list.append(install_ob)

        html.data.total = total + service_total
        html.data.dis_total = (total / b - ((d / 100) * total)) + service_total
        html.process_template()
        # html.dump_to_file(folder.joinpath("opti_test.html"))
        html.dump_to_pdf(folder.joinpath(f"{self.company_name}{' '}{year}.pdf"))
# Message Andrew Marker:thumbsup:Dot your i's on the bottom!












