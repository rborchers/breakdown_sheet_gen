import sys

import PySimpleGUI as psg


class ProductList:
    def __init__(self, all_products):
        self.is_error = False
        self.errors = []
        self.product_list = []
        for p in all_products.data:
            # make sure I have a product code, because that's my main key
            try:
                p.field_data['Product_Code']
            except KeyError:
                # I don't! Log that this product has a problem!
                try:
                    err_string = f'\"{p.field_data["Product_Name"]}\" has no product code.'
                except KeyError:
                    # Wow. I don't even have a product name. This thing is REALLY hosed.
                    err_string = 'Something really bad happened with some product.'
                # Add the error to the list and flag that I have one.
                self.errors.append(err_string)
                self.is_error = True
                continue
            temp = {'code': p.field_data['Product_Code'], 'price': p.field_data['Unit_Price']}
            self.product_list.append(temp)

        self.error_terminate()
        return

    def error_terminate(self):
        # I don't have any errors, all is well!
        if not self.is_error:
            return
        # I have errors! Build a simple window to list them and terminate.
        layout = [[psg.Text('')]]
        for e in self.errors:
            layout.append([psg.Text(e)])
        layout.append([psg.Text('')])
        layout.append([psg.Text('The above errors must be fixed to continue.')])
        layout.append([psg.Ok(size=(5, 1))])
        w = psg.Window('Breakdown Sheet Creator', layout=layout)
        w.Read()
        w.Close()
        sys.exit(1)
        return

    def get_price(self, code):
        for p in self.product_list:
            if p['code'] == code:
                return p['price']
            else:
                # pop up lets user know which product code is not valid
                # psg.popup(p['code'], 'not valid code')
                self.error_terminate()

        return
