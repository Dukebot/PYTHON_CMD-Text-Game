import json


def main():
    #print("\033[1;32;40m Bright Green  \n")

    #Read game data from json files
    game_state = read_json('game_data/game_state.json')
    scenes = read_json('game_data/scenes.json')

    #Load the data of the firt scene
    scene = scenes["starting_room"]

    while True:
        #Get the scene data
        state = scene["current_state"]
        text = scene["states"][state]["text"]
        choices = scene["states"][state]["choices"]

        available_choices = get_choices_filtered(choices, game_state)
        
        #Print scene text
        print("\n" + text + "\n")
        i = 0
        for available_choice in available_choices:
            print(str(i) + " - " + available_choice["choice"])
            i += 1

        #Select choice
        choice_selected = select_choice(available_choices)
        choice = available_choices[choice_selected]

        #Print choice result
        choice_result = choice["result"]
        print("\n" + choice_result)

        #Check if this choice brigs us to other scene
        if "to_scene" in choice:
            to_scene = choice["to_scene"]
            scene = scenes[to_scene]
        
        #Check if this choice updates the state of the scene
        if "to_state" in choice:
            to_state = choice["to_state"]
            scene["current_state"] = to_state
        
        #Check if this choice updates the game state
        if "updates_game_state" in choice:
            updates_game_state = choice["updates_game_state"]
            for key in updates_game_state:
                value = updates_game_state[key]
                game_state[key] = value

        #Wait for player input to continue
        print("\nPress any key to continue...")
        input()

    return 0


#Returns the data inside a json file
def read_json(json_path):
    with open(json_path) as json_file:
        return json.load(json_file)


def get_choices_filtered(choices, game_state):
    available_choices = []
    for choice in choices:
        choice_available = True
        if "show_if" in choice:
            for key in choice["show_if"]:
                if game_state[key] != choice["show_if"][key]:
                    choice_available = False
        if choice_available:
            available_choices.append(choice)
    return available_choices


#Returns the choice made by the player, it's an integer starting from 0
def select_choice(choices):
    #Read choices until it's correct
    while True:
        print("\nWhat are you going to do? ")

        #Read the player input
        action = input()
        try:
            action = int(action)
            #Check if the action choosen is a correct choice
            if action >= 0 and action < len(choices):
                return action
            else:
                print("This is not a correct choice, please try again.")
        except:
            print("This is not a correct choice, please try again.")


main()