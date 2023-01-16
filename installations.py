import zcrmsdk

def search_records_by_criteria():
    try:
        module_ins = zcrmsdk.ZCRMModule.get_instance('Installations')
        resp = module_ins.search_records_by_criteria('((Account:equals:APX))')
        print(resp.status_code)
        resp_info = resp.info
        print(resp_info.count)
        print(resp_info.page)
        print(resp_info.per_page)
        print(resp_info.is_more_records)
        record_ins_arr = resp.data
        for record_ins in record_ins_arr:
            print(record_ins.get_field_value('Account')['name'])
            print(record_ins.get_field_value('Name'))
            print(record_ins.get_field_value('Service Installs'))
            print(record_ins.get_field_value('Purchase_Price'))
            print(record_ins.get_field_value('PO_Number'))
            print(record_ins.get_field_value('Date_Installed'))
            print(record_ins.get_field_value('Maintenance'))
            print(record_ins.get_field_value('Q2'))
            print(record_ins.get_field_value('Discount'))
            print(record_ins.get_field_value(''))

            print(record_ins.entity_id)
            print(record_ins.created_by.id)
            print(record_ins.modified_by.id)
            print(record_ins.owner.id)
            print(record_ins.created_by.name)
            print(record_ins.created_time)
            print(record_ins.modified_time)
    except zcrmsdk.ZCRMException as ex:
        print(ex.status_code)
        print(ex.error_message)
        print(ex.error_code)
        print(ex.error_details)
        print(ex.error_content)


if __name__ == '__main__':
    config = {
            "client_id":"1000.YH9HF9IC6EL4D6WQG38W5M4KSN2UIH",
            "client_secret":"bc0dbd088e7203e8c11369e1aeaa34954cbda5ce8a",
            "redirect_uri":"self",
            "currentUserEmail":"tlundy@optimation.com",
            "accounts_url":"https://accounts.zoho.com",
            "token_persistence_path":"./config"
            }
    zcrmsdk.ZCRMRestClient.initialize(config)
    oauth_client = zcrmsdk.ZohoOAuth.get_client_instance()
    refresh_token = "1000.e45c9b3ecca0c77e64d24b3f3c6197e9.66a21b6bd165fe1f9e95f76ee1285824"
    user_identifier = "tlundy@optimation.com"
    oauth_tokens = oauth_client.generate_access_token_from_refresh_token(refresh_token, user_identifier)

    search_records_by_criteria()