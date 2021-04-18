import curses
import sys
from os import system, name
import json

# Borrowed almost all of the code from here http://adamlamers.com/post/FTPD9KNRA8CT

class CursesMenu(object):

    INIT = {'type' : 'init'}

    def __init__(self, menu_options):
        self.screen = curses.initscr()
        self.menu_options = menu_options
        self.selected_option = 0
        self._previously_selected_option = None
        self.running = True

        #init curses and curses input
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(0) #Hide cursor
        self.screen.keypad(1)

        #set up color pair for highlighted option
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.hilite_color = curses.color_pair(1)
        self.normal_color = curses.A_NORMAL

    def prompt_selection(self, parent=None):

        option_count = len(self.menu_options['options'])

        input_key = None

        ENTER_KEY = ord('\n')
        while input_key != ENTER_KEY:
            if self.selected_option != self._previously_selected_option:
                self._previously_selected_option = self.selected_option

            self.screen.border(0)
            self._draw_title()
            for option in range(option_count):
                if self.selected_option == option:
                    self._draw_option(option, self.hilite_color)
                else:
                    self._draw_option(option, self.normal_color)

            max_y, max_x = self.screen.getmaxyx()
            if input_key is not None:
                self.screen.addstr(max_y-3, max_x - 5, "{:3}".format(self.selected_option))
            self.screen.refresh()


            input_key = self.screen.getch()
            down_keys = [curses.KEY_DOWN, ord('j')]
            up_keys = [curses.KEY_UP, ord('k')]
            exit_keys = [ord('q')]

            if input_key in down_keys:
                if self.selected_option < option_count:
                    self.selected_option += 1
                else:
                    self.selected_option = 0

            if input_key in up_keys:
                if self.selected_option > 0:
                    self.selected_option -= 1
                else:
                    self.selected_option = option_count

            if input_key in exit_keys:
                self.selected_option = option_count #auto select exit and return
                break

        return self.selected_option

    def _draw_option(self, option_number, style):
        self.screen.addstr(7 + option_number,
                           4,
                           "{}".format(self.menu_options['options'][option_number]['title']),
                           style)

    def _draw_title(self):
        self.screen.addstr(2, 2, self.menu_options['title'], curses.A_STANDOUT)
        self.screen.addstr(4, 2, self.menu_options['subtitle'], curses.A_BOLD)

    def display(self):
        selected_option = self.prompt_selection()
        curses.endwin()
        self.screen.clear()
        if selected_option < len(self.menu_options['options']):
            selected_opt = self.menu_options['options'][selected_option]
            return selected_opt

#Aux function that reads the data of a json and return a dictionary
def read_json(json_path):
    #Encoding 'utf-8' for spanish special characters like accents
    with open(json_path, encoding='utf-8') as json_file:
        return json.load(json_file)


#Given the scene dictionary it returns the text of the current state
def get_scene_text(scene):
    current_state = scene["current_state"]
    return scene["states"][current_state]["text"]


#Given the scene sictionary it resurns all the choices of the current state
def get_scene_choices(scene):
    current_state = scene["current_state"]
    return scene["states"][current_state]["choices"]


#Filters the choices that has to be shown based on the game state
def get_available_choices(scene, game_state):
    available_choices = []
    
    choices = get_scene_choices(scene)
    for choice in choices:
        choice_available = True
        if "show_if" in choice:
            for key in choice["show_if"]:
                if game_state[key] != choice["show_if"][key]:
                    choice_available = False
                    break
        if choice_available:
            available_choices.append(choice)
    
    return available_choices

def print_with_ncurses(str):
    menu = {'title' : 'The Dark Room',
        'type' : 'menu',
        'subtitle' : str}

    menu['options'] = [{'title' : 'Continue'}]
    m = CursesMenu(menu)
    m.display()

def choice_menu(scene,choices):
    menu = {'title' : 'The Dark Room',
        'type' : 'menu',
        'subtitle' : get_scene_text(scene)}
    
    menu_items = []
    i = 0
    
    for choice in choices:
        menu_items.append({'title': choice["choice"], 'type': 'choice_num', 'choice_num': i})
        i += 1

    menu['options'] = menu_items
    m = CursesMenu(menu)
    selected_action = m.display()
    return choices[selected_action['choice_num']]

#Returns the selected choice from a list of choices
def select_choice(choices):
    while True:
        print_with_ncurses("\nWhat are you going to do? ")
        player_choice = input()
        try:
            player_choice = int(player_choice) - 1
            if player_choice >= 0 and player_choice < len(choices):
                return choices[player_choice]
            else:
                print_with_ncurses("This is not a correct choice, please try again.")
        except:
            print_with_ncurses("This is not a correct choice, please try again.")


#Updates the game state if the object has the property "updates_game_state"
def update_game_state(object, game_state):
    if "updates_game_state" in object:
        updates_game_state = object["updates_game_state"]
        for key in updates_game_state:
            value = updates_game_state[key]
            game_state[key] = value


#This functions allows the player to select the language and returns it's code (string)
def intro():

    menu = {'title' : 'The Dark Room',
        'type' : 'menu',
        'subtitle' : 'Which language are you going to choose?'}
    
    option_1 = {'title' : 'English',
            'type' : 'language',
            'language' : 'en'}
    
    option_2 ={'title' : 'Español',
            'type' : 'language',
            'language' : 'es'}
    menu['options'] = [option_1,option_2]
    m = CursesMenu(menu)
    selected_action = m.display()  
    return selected_action['language']

def main():
    language = intro()

    #Read the game data from json files
    game_state = read_json('game_data/game_state.json')
    scenes = read_json('game_data/scenes_' + language + '.json')

    #Load the first scene data
    scene = scenes["start_menu"]

    #Game loop
    while True:
        #Read the current state of the scene and update the game state if necessary
        current_state = scene["current_state"]
        update_game_state(scene["states"][current_state], game_state)

        #If this scene do not have available choices it means we reached the end of the game
        if not "choices" in scene["states"][current_state]:
            print_with_ncurses("Press ENTER to END...")
            break

        #Get the available choices of this scene
        available_choices = get_available_choices(scene, game_state)
        
        #Select the choice and print the result on the screen
        choice = choice_menu(scene, available_choices)
        update_game_state(choice, game_state)
        print_with_ncurses(choice["result"])

        #Update state and handle scene transition
        if "to_state" in choice:
            scene["current_state"] = choice["to_state"]
        if "to_scene" in choice:
            scene = scenes[choice["to_scene"]]

    return 0

if __name__ == "__main__":
    main()