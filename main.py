import json
from ncurses import CursesMenu


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


#TODO define this inside the Json to be generic
def print_choice_result(str):
    menu = {
        'title' : 'The Dark Room',
        'type' : 'menu',
        'subtitle' : str
    }
    menu['options'] = [{'title' : 'Continue'}]
    m = CursesMenu(menu)
    m.display()


def print_scene_and_get_choice(scene, choices):
    menu = {
        'title' : 'The Dark Room',
        'type' : 'menu',
        'subtitle' : get_scene_text(scene)
    }
    i = 0
    menu_items = []

    # Fallback for the end because there are no choices
    if choices == None:
        menu_items.append({'title': 'END', 'type': 'end', 'choice_num': 0})
    # Normal flow
    else:
        for choice in choices:
            menu_items.append({
               'title': choice["choice"], 'type': 'choice_num', 'choice_num': i
            })
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
def select_language():
    menu = {
        'title' : 'The Dark Room',
        'type' : 'menu',
        'subtitle' : 'Which language are you going to choose?'
    }
    option_1 = {
        'title' : 'English',
        'type' : 'language',
        'language' : 'en'
    }
    option_2 ={
        'title' : 'Español',
        'type' : 'language',
        'language' : 'es'
    }

    menu['options'] = [option_1, option_2]
    m = CursesMenu(menu)
    selected_action = m.display()  
    return selected_action['language']


def main():
    language = select_language()

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

        #Get the available choices of this scene
        try:
            available_choices = get_available_choices(scene, game_state)
        except:
            available_choices = None
        
        #Select the choice and print the result on the screen
        choice = print_scene_and_get_choice(scene, available_choices)
        update_game_state(choice, game_state)
        print_choice_result(choice["result"])

        #Update state and handle scene transition
        if "to_state" in choice:
            scene["current_state"] = choice["to_state"]
        if "to_scene" in choice:
            scene = scenes[choice["to_scene"]]

    return 0


if __name__ == "__main__":
    main()