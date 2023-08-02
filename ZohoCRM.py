import zcrmsdk
import ProductList
import Customer
import sys
import os
import pathlib
import json

class ZohoCRM:
# API KEY TO GET ACCESS TO THE INFO IN OPTIAMTIONS ACCOUNT
    def __init__(self):
        self.customer_list = []
        self.account_info = []
        self.error = None
        res_path=pathlib.Path(resource_path(''))
        conf_path=res_path.joinpath('config')
        print(conf_path)
        self.config = {
            "client_id": "1000.YH9HF9IC6EL4D6WQG38W5M4KSN2UIH",
            "client_secret": "bc0dbd088e7203e8c11369e1aeaa34954cbda5ce8a",
            "redirect_uri": "self",
            "currentUserEmail": "tlundy@optimation.com",
            "accounts_url": "https://accounts.zoho.com",
            "token_persistence_path": str(conf_path)
        }
        zcrmsdk.ZCRMRestClient.initialize(self.config)
        self.oauth_client = zcrmsdk.ZohoOAuth.get_client_instance()
        self.refresh_token = "1000.e45c9b3ecca0c77e64d24b3f3c6197e9.66a21b6bd165fe1f9e95f76ee1285824"
        self.user_identifier = "tlundy@optimation.com"
        self.oauth_tokens = self.oauth_client.generate_access_token_from_refresh_token(self.refresh_token,
                                                                                       self.user_identifier)
        return
# GET ACCOUNT FROM ZOHO ONLY GRABS ACCOUNTS THAT ARE ON MAINTENANCE
    def get_accounts(self):
        ret = []
        try:
            module_ins = zcrmsdk.ZCRMModule.get_instance('Accounts')
            resp = module_ins.search_records_by_criteria('((Status:equals:Maintenance))')
            resp2 = module_ins.search_records_by_criteria('((Status:equals:Service Customer))')
            print(resp.status_code)
        except zcrmsdk.ZCRMException as ex:
            print(ex.status_code)
            print(ex.error_message)
            print(ex.error_code)
            print(ex.error_details)
            print(ex.error_content)

            self.error = ex
            return
        record_ins_arr = resp.data + resp2.data
        for record_ins in record_ins_arr:
            print(record_ins.get_field_value('Account_Name'))
            ret.append(record_ins.field_data)
        self.account_info = ret
        self.customer_list = []

        for cust in ret:
            try:
                rate = (cust['Maintenance_Rate1'])/100.0
            except KeyError:
                rate = None
            new_cust = Customer.Customer(cust, rate,0.0)
            self.customer_list.append(new_cust)
        return

#   GETS PRODUCT CODE AND PRICE
    def get_install_price(self):

        module_prod = zcrmsdk.ZCRMModule.get_instance('Products')
        all_products = module_prod.get_records()
        self.product_list = ProductList.ProductList(all_products)
        return

# GETS ALL THE INSTALLATIONS AN ACCOUNT HAS WHEN THE ACCOUNT IS CHECKED IN THE BOX
    def verify_customer(self, list):
        valid_customer = []
        errored_customer = []
        for customer in list:
            cust_obj = self.find_customer(customer)
            module_ins = zcrmsdk.ZCRMModule.get_instance('Installations')
            module_ins2 = zcrmsdk.ZCRMModule.get_instance('Service_Installs')
            fixed_name = customer.replace('(', '\(').replace(')', '\)')
            cust_obj.valid = True
            try:
                resp = module_ins.search_records_by_criteria(f'((Account:equals:{fixed_name}))')
                # INSTALLATION DATA GATHERING
                for install in resp.data:
                    cust_obj.install_list.append(install.field_data)

            except zcrmsdk.ZCRMException as ex:
                pass
            try:
                resp2 = module_ins2.search_records_by_criteria(f'((Account:equals:{fixed_name}))')

                for service_install in resp2.data:
                    cust_obj.service_install.append(service_install.field_data)
            except zcrmsdk.ZCRMException as ex:
                pass
            if not cust_obj.install_list and cust_obj.service_install:
               cust_obj.valid = False
               errored_customer.append(cust_obj)
            else:
                valid_customer.append(cust_obj)
        return valid_customer, errored_customer
# CREATES THE LIST OF ACCOUNTS
    def get_name_list(self):
        ret = []
        for c in self.customer_list:
            ret.append(c.company_name)
            ret.sort()
        return ret
# IF THE NAME CHECK MATCHES THE ONE IN ZOHO
    def find_customer(self, name):
        for c in self.customer_list:
            if c.company_name == name:
                return c

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)











  # except zcrmsdk.ZCRMException as ex:
            #     cust_obj.valid = False
            #     errored_customer.append(cust_obj)
            #     # SERVICE INSTALLS DATA GATHERING
            # try:
            #     resp2 = module_ins2.search_records_by_criteria(f'((Account:equals:{fixed_name}))')
            #     cust_obj.valid = True
            #     for service_install in resp2.data:
            #         cust_obj.service_install.append(service_install.field_data)
            #
            #     valid_customer.append(cust_obj)