# Author: LIU LI
# Date: 2023/06/06
# Description: This application is used for translating Japanese/Kanji into Romaji.

import PySimpleGUI as sg
import numpy as np
import pandas as pd
import pykakasi

# Open the file, and translate Japanese/Kanji into Romaji using pykakasi library.
# And then save the new file into destination folder.
def translate(input_path, output_path):
    # Read cvs file with different encoding.
    codecs = ['cp932', 'euc_jp', 'iso2022_jp', 'shift_jis',
              'utf_32', 'utf_16', 'utf_7', 'utf_8', 'utf_8_sig']
    for c in codecs:
        try:
            df = pd.read_csv(input_path, encoding=c)
        except:
            pass


    kks = pykakasi.kakasi()
    ENG = []

    # Variables using for progress bar
    length = len(df)
    tenPercent = length * 0.01
    currentPercent = 0
    count = 0
    window['-PERCENTAGE-'].update(str(currentPercent) + '%')
    window['-PBAR-'].update(currentPercent)

    for JPN in df[df.columns[0]]:
        # For updating progress bar
        count += 1
        if count >= tenPercent:
            currentPercent += 1
            count = 0
            window['-PERCENTAGE-'].update(str(currentPercent) + '%')
            window['-PBAR-'].update(currentPercent)

        # Translate Kanji into Romaji
        result = kks.convert(JPN)
        romaji = ''
        for w in result:
            romaji += w['hepburn']
        ENG.append(romaji.capitalize())

    # Update dataframe and save the file
    df['Romaji'] = ENG
    df.to_csv(output_path + '/output.csv', index=False, encoding='utf-8-sig', mode='w+')

    window['-PERCENTAGE-'].update('100%')
    window['-PBAR-'].update(100)


sg.theme('reddit')

layout = [
    [sg.Text('入力ファイル')],
    [sg.Text('Path:'), sg.InputText(key='-INPUT ADDRESS-', disabled=True), sg.Button('Open', key='-INPUT BUTTON-')],
    [sg.Text('出力フォルダ')],
    [sg.Text('Path:'), sg.InputText(key='-OUTPUT ADDRESS-', disabled=True), sg.Button('Open', key='-OUTPUT BUTTON-')],
    [sg.Push(), sg.Button('実行'), sg.Push()],
    [sg.Push(), sg.Text('0%', key='-PERCENTAGE-'), sg.Push()],
    [sg.Push(), sg.ProgressBar(100, orientation='h', size=(20, 20), bar_color='white', key='-PBAR-'), sg.Push()]
]
window = sg.Window('Japanese/Kanji to Romaji', layout, icon='R.ico')

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
                translate(in_p, ou_p)
            except UnicodeDecodeError:
                print('Encoding type is wrong.')

window.close()
