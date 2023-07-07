# Author: LIU LI
# Date: 2023/06/13
# Description: Translate Japanese address to Zip Code or vice-versa.

import PySimpleGUI as sg
import pandas as pd
import requests


# Read cvs file into the dataframe.
def readFile(readFile_path):
    # Check all widely used encodings for Japanese.
    codecs = ['cp932', 'euc_jp', 'iso2022_jp', 'shift_jis',
              'utf_32', 'utf_16', 'utf_7', 'utf_8', 'utf_8_sig']
    for c in codecs:
        try:
            df = pd.read_csv(readFile_path, encoding=c)
        except:
            pass
    return df


def saveFile(df, saveFile_path):
    df.to_csv(saveFile_path + '/output.csv', index=False, encoding='utf-8-sig', mode='w+')
    return 'Finished'


# Translate Japanese address to Zip Code or vice-versa.
# Find Zip Code using Japanese address with miss words function is also works, but very not recommended.
def translate(readFile_path, saveFile_path, method):
    # read csv file into dataframe.
    df = readFile(readFile_path)

    # The actual name of the methods in api-endpoint.
    METHODS = ['findzipcode', 'findaddr', 'findzipcodeambg']
    if method == 'ATZ':
        METHOD = METHODS[0]
    elif method == 'ZTA':
        METHOD = METHODS[1]
    elif method == 'AMWTZ':
        METHOD = METHODS[2]
    # api-endpoint
    URL = 'https://zipcode.milkyfieldcompany.com/api/v1/' + METHOD

    # If you want to use unlimited version, please replace this API_KEY with your own key.
    API_KEY = '8dd576355933fd12755899140ab97c00'
    # API_KEY = '2ee6b1417a9748c963b332104083328f'


    # Parameters that use for updating the progress bar.
    length = len(df)
    if length > 100:
        tenPercent = length * 0.01
    else:
        tenPercent = 1
        perForSmallLen = int(100 / length)
    currentPercent = 0
    count = 0
    window['-PERCENTAGE-'].update(str(currentPercent) + '%')
    window['-PBAR-'].update(currentPercent)

    outputs = []
    # Loop through each row of the first column in the csv file.
    for input in df[df.columns[0]]:
        # Show current progress bar, update every 1 percent.
        count += 1
        if count >= tenPercent:
            if length > 100:
                currentPercent += 1
            else:
                currentPercent += perForSmallLen
            count = 0
            window['-PERCENTAGE-'].update(str(currentPercent) + '%')
            window['-PBAR-'].update(currentPercent)

        # data to be sent to api
        if method == 'ATZ' or method == 'AMWTZ':
            data = {'apikey': API_KEY,
                    'address': input}
        else:
            if len(str(input)) < 7:
                input = '0' + str(input)
            data = {'apikey': API_KEY,
                    'zipcode': input}

        # sending post request and saving the response as response object
        r = requests.post(url=URL, data=data)

        # extracting data in json format
        data = r.json()
        # Save the output into a list.
        if method == 'ATZ' or method == 'AMWTZ':
            if len(data['items']) > 0:
                outputs.append(data['items'][0]['zipcode'])
            else:
                outputs.append("unfounded")
        else:
            outputs.append(data['items'][0]['address'])
    # Add zipcode/address into dataframe.
    if method == 'ATZ' or method == 'AMWTZ':
        df['Zipcode'] = outputs
        df['Zipcode'] = df['Zipcode'].apply('="{}"'.format)
    else:
        df['Address'] = outputs

    # Save the dataframe into csv file. And update final progress bar.
    saveFile(df, saveFile_path)
    window['-PERCENTAGE-'].update('100%')
    window['-PBAR-'].update(100)
    return 'Finished'


sg.theme('reddit')

# Features in the control panel.
layout = [
    [sg.Push(), sg.Text('メソッド:'), \
     sg.Spin(['Address with Missing Words to Zipcode', 'Zipcode to Address', 'Address to Zipcode'], enable_events=True, \
             initial_value='Address to Zipcode', readonly=True, key='-TRANSLATE-')],
    [sg.Text('入力ファイル')],
    [sg.Text('Path:'), sg.InputText(key='-INPUT ADDRESS-', disabled=True), sg.Button('Open', key='-INPUT BUTTON-')],
    [sg.Text('出力フォルダ')],
    [sg.Text('Path:'), sg.InputText(key='-OUTPUT ADDRESS-', disabled=True), sg.Button('Open', key='-OUTPUT BUTTON-')],
    [sg.Push(), sg.Button('実行'), sg.Push()],
    [sg.Push(), sg.Text('0%', key='-PERCENTAGE-'), sg.Push()],
    [sg.Push(), sg.ProgressBar(100, orientation='h', size=(20, 20), bar_color='white', key='-PBAR-'), sg.Push()]
]
window = sg.Window('Japanese Address to Zipcode', layout, icon='postal.ico')

# Most of the codes below are checking if the input file and output folder are selected by users correctly.
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '-INPUT BUTTON-':
        input_path = sg.popup_get_file('Open', no_window=True)
        window['-INPUT ADDRESS-'].update(input_path)
        window['-PERCENTAGE-'].update('0%')
        window['-PBAR-'].update(0)

    if event == '-OUTPUT BUTTON-':
        output_path = sg.popup_get_folder('Open', no_window=True)
        window['-OUTPUT ADDRESS-'].update(output_path)

    if event == '実行':
        in_p = values['-INPUT ADDRESS-']
        ou_p = values['-OUTPUT ADDRESS-']
        fileType = in_p.split('/')[-1].split('.')[-1]

        if in_p == '':
            window['-INPUT ADDRESS-'].update('入力ファイルを選んでください。')

        elif fileType != 'csv' and in_p != '入力ファイルを選んでください。':
            window['-INPUT ADDRESS-'].update('入力ファイルはcsvではありません。')

        if ou_p == '':
            window['-OUTPUT ADDRESS-'].update('出力フォルダを選んでください。')

        if in_p != '' and ou_p != '' and in_p != '入力ファイルを選んでください' and ou_p != '出力フォルダを選んでください。' \
                and in_p != '入力ファイルはcsvではありません。' and fileType == 'csv':
            try:
                # The translating processing starts below.
                match values['-TRANSLATE-']:
                    case 'Address to Zipcode':
                        translate(in_p, ou_p, method='ATZ')
                    case 'Zipcode to Address':
                        translate(in_p, ou_p, method='ZTA')
                    case 'Address with Missing Words to Zipcode':
                        translate(in_p, ou_p, method='AMWTZ')
            except UnicodeDecodeError:
                print('Encoding type is wrong.')
window.close()
