import PySimpleGUI as sg
from time import time
from random import randint


def convert_pos_to_pixel(cell):
    tl = cell[0] * CELL_SIZE, cell[1] * CELL_SIZE
    br = tl[0] + CELL_SIZE, tl[1] + CELL_SIZE
    return tl, br


def place_apple():
    apple_pos = randint(0, CELL_NUM - 1), randint(0, CELL_NUM - 1)
    while apple_pos in snake_body:
        apple_pos = randint(0, CELL_NUM - 1), randint(0, CELL_NUM - 1)
    return apple_pos


def snake_start_direction():
    DIR = ['left', 'right', 'up', 'down']
    RandomDirIndex = randint(0, 3)
    currentDir = DIR[RandomDirIndex]
    direction = DIRECTIONS[currentDir]
    return currentDir, direction


def snake_start_position():
    currentDir, direction = snake_start_direction()
    head = randint(5, CELL_NUM - 5), randint(5, CELL_NUM - 5)
    snake_body = [head, (head + DIRECTIONS[currentDir]), (head + DIRECTIONS[currentDir] * 2)]
    return snake_body


# game constants
FIELD_SIZE = 600
CELL_NUM = 25
CELL_SIZE = FIELD_SIZE / CELL_NUM

# snake
DIRECTIONS = {'left': (-1, 0), 'right': (1, 0), 'up': (0, 1), 'down': (0, -1)}
snake_body = snake_start_position()
currentDir, direction = snake_start_direction()

# apple
apple_pos = place_apple()
apple_eaten = False

sg.theme('Green')
field = sg.Graph(canvas_size=(FIELD_SIZE, FIELD_SIZE),
                 graph_bottom_left=(0, 0),
                 graph_top_right=(FIELD_SIZE, FIELD_SIZE),
                 background_color='black',
                 key='-GRAPH-')

menu = sg.Push(), sg.Text('WELCOME TO GLUTTONOUS SNAKE!', key='-MESSAGE-', text_color='blue'), \
    sg.Text('SPEED:', key='-SPEED LABEL-'), \
    sg.Spin(['VERY SLOW', 'SLOW', 'NORMAL', 'FAST', 'VERY FAST'], enable_events=True, \
            initial_value='NORMAL', readonly=True, key='-SPEED-'), \
    sg.Button('PLAY', key='-START BUTTON-'), \
    sg.Button('PAUSE', key='-PAUSE BUTTON-', visible=False), \
    sg.Button('EXIT GAME', key='-EXIT BUTTON-', visible=False)

# layout = [[field]]

layout = [[menu], [field]]

window = sg.Window('Gluttonous Snake', layout, return_keyboard_events=True, icon='./img/snake.ico')

start_time = time()
game_start = False
pause_game = False
alive = True
snake_speed = 3

while True:
    event, values = window.read(timeout=10)
    if event == sg.WIN_CLOSED:
        break
    if event == 'Left:37':
        if currentDir != 'left' and currentDir != 'right':
            direction = DIRECTIONS['left']
            currentDir = 'left'
    if event == 'Up:38':
        if currentDir != 'down' and currentDir != 'up':
            direction = DIRECTIONS['up']
            currentDir = 'up'
    if event == 'Right:39':
        if currentDir != 'left' and currentDir != 'right':
            direction = DIRECTIONS['right']
            currentDir = 'right'
    if event == 'Down:40':
        if currentDir != 'down' and currentDir != 'up':
            direction = DIRECTIONS['down']
            currentDir = 'down'

    match values['-SPEED-']:
        case 'VERY SLOW':
            snake_speed = 0.5
        case 'SLOW':
            snake_speed = 0.4
        case 'NORMAL':
            snake_speed = 0.3
        case 'FAST':
            snake_speed = 0.2
        case 'VERY FAST':
            snake_speed = 0.1
    if event == '-EXIT BUTTON-':
        break

    if event == '-START BUTTON-':
        game_start = True
        alive = True
        window['-MESSAGE-'].update('')
        window['-SPEED-'].update(visible=False)
        window['-SPEED LABEL-'].update(visible=False)
        window['-PAUSE BUTTON-'].update(visible=True)
        window['-START BUTTON-'].update(visible=False)
        window['-EXIT BUTTON-'].update(visible=False)
        if pause_game:
            pause_game = False
        else:
            snake_body = snake_start_position()
            currentDir, direction = snake_start_direction()
            apple_pos = place_apple()

    if event == '-PAUSE BUTTON-':
        pause_game = True
        window['-MESSAGE-'].update('GAME PAUSED')
        window['-SPEED LABEL-'].update(visible=True)
        window['-SPEED-'].update(visible=True)
        window['-PAUSE BUTTON-'].update(visible=False)
        window['-START BUTTON-'].update('CONTINUE', visible=True)

    if game_start and not pause_game:
        time_since_start = time() - start_time
        if time_since_start >= snake_speed:
            start_time = time()

            # apple snake collision
            if snake_body[0] == apple_pos:
                apple_pos = place_apple()
                apple_eaten = True

            # snake update
            new_head = (snake_body[0][0] + direction[0], snake_body[0][1] + direction[1])
            snake_body.insert(0, new_head)
            if apple_eaten == False:
                snake_body.pop()
            else:
                apple_eaten = False

            # check death
            if not 0 <= snake_body[0][0] <= CELL_NUM - 1 or \
                    not 0 <= snake_body[0][1] <= CELL_NUM - 1 or \
                    snake_body[0] in snake_body[1:]:
                game_start = False
                alive = False
                window['-MESSAGE-'].update('GAME OVER')
                window['-SPEED LABEL-'].update(visible=True)
                window['-SPEED-'].update(visible=True)
                window['-START BUTTON-'].update('PLAY AGAIN', visible=True)
                window['-PAUSE BUTTON-'].update(visible=False)
                window['-EXIT BUTTON-'].update(visible=True)

        field.DrawRectangle((0, 0), (FIELD_SIZE, FIELD_SIZE), 'black')

        if alive:
            tl, br = convert_pos_to_pixel(apple_pos)
            field.DrawRectangle(tl, br, 'red')
            # field.DrawImage(filename='./img/apple.png',location=tl)

            # draw snake
            for index, part in enumerate(snake_body):
                tl, br = convert_pos_to_pixel(part)
                color = 'yellow' if index == 0 else 'green'
                field.DrawRectangle(tl, br, color)

        if len(snake_body) >= 30:
            game_start = False
            window['-MESSAGE-'].update('CONGRATULATIONS! YOU WIN!')
            window['-SPEED LABEL-'].update(visible=True)
            window['-SPEED-'].update(visible=True)
            window['-START BUTTON-'].update('PLAY AGAIN', visible=True)
            window['-PAUSE BUTTON-'].update(visible=False)
            window['-EXIT BUTTON-'].update(visible=True)

window.close()
