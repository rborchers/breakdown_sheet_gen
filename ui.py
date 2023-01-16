import PySimpleGUI as sg


def cust_list_build(zoho):
    # GRABS ONLY THE ACTIVE ACCOUNTS AND CREATES THE UI LIST
    col = []
    for company in zoho.get_name_list():
        col.append([sg.Checkbox(company, key=company)])
    layout = [
        # [ sg.InputText('Search', size=(10,2), key='search' )],
        [sg.Text('Select Account(s)', justification='left', font='20', size=(15,1))],
        [sg.Column(col, size=(300, 300), scrollable=True)],
        [sg.Cancel('Exit'), sg.ReadButton('Next')]]
    window = sg.Window('Breakdown Sheet Creator', element_justification='c', grab_anywhere=True).Layout(layout)
    return window

# READS WINDOW INCLUDING LOCATION
def cust_list_read(zoho):
    ret = []
    window = cust_list_build(zoho)
    event, values = window.read()
    window_loc = window.CurrentLocation()
    window.close()
    del window
    if event is None or event == 'Exit':
        return None, None
    for tru in values:
        if values[tru]:
            ret.append(tru)
    return ret, window_loc

# BUILDS THE UI WINDOW FOR THE SAVE LOCATION SAVER
def folder_build(loc, z, valid, errored):
    # window = cust_list_build(list_price)
    # event, values = window.read()
    layout = [
        [sg.Text('Select Save Location', justification='center', font='20')],
        [sg.InputText('Folder', key='folder'), sg.FolderBrowse()],
        # [sg.InputCombo(['Quarterly', 'Annually'], key='type', size=(20, 3))],
        [sg.InputText('Year', key='date')],
        [sg.Checkbox('List Price', default=True , key='list_price')],
        [sg.Button('Exit'), sg.ReadButton('Create PDF')],
        [sg.Text('Accounts Selected:')]
    ]


    for v in valid:
        layout.append([sg.Text('Selected accounts - ' + v.company_name, text_color='yellow', font='bold 10')])
    for e in errored:
        layout.append([sg.Text('Errored accounts - ' + e.company_name, text_color='red', font='bold 10')])
    window = sg.Window('Breakdown Sheet Creator', layout=layout, location=loc)

    return window

# LISTENER FOR THE CREATE PDF BUTTON
def folder_read(loc, z, valid, errored):
    window = folder_build(loc, z, valid, errored)
    while True:
        event, values = window.Read()
        # CREATES PDF IN FOLDER SELECTED
        if event == 'Create PDF':

            break
        # CLOSES WINDOWS ON EXIT
        if event is None or event == 'Exit':
            break
    del window
    return event, values

# def install_list_build(list):
#         # GRABS ONLY THE ACTIVE ACCOUNTS
#     col = []
#     for company in list.verify_customer():
#         col.apppend([sg.Text(company)])
#         layout = [
#             [sg.Column(col, size=(200, 300), scrollable=True)],
#             [sg.Cancel('Exit'), sg.ReadButton('Next')]]
#         window = sg.Window('OPTIMATION', element_justification='c', grab_anywhere=True).Layout(layout)
#         return window
# def install_list_read(list):
#     window = install_list_build(list)
#     return window