import json


#Main function of the program, here we read the game data and process the game loop
def main():
    #Initialize the game data from json and set the first scene data
    game_state = read_json('game_data/game_state.json')
    scenes = read_json('game_data/scenes.json')
    scene = scenes["start_menu"]

    #Game loop
    while True:
        #Read the current state of the scene and update the game state if necessary
        current_state = scene["current_state"]
        update_game_state(scene["states"][current_state], game_state)

        #Print the scene text on the screen
        print("\n" + get_scene_text(scene) + "\n")

        #If this scene do not have available choices it means we reached the end of the game
        if not "choices" in scene["states"][current_state]:
            print("\nPress ENTER to END...")
            input()
            break

        #Get the available choices of this scene and print them to the screen
        available_choices = get_available_choices(scene, game_state)
        print_available_choices(available_choices)
        
        #Select the choice and print the result on the screen
        choice = select_choice(available_choices)
        update_game_state(choice, game_state)
        print("\n" + choice["result"])

        #Update state and handle scene transition
        if "to_state" in choice:
            scene["current_state"] = choice["to_state"]
        if "to_scene" in choice:
            scene = scenes[choice["to_scene"]]

        #Wait for player input to make the next iteration of the game loop
        print("\nPress ENTER to continue...")
        input()

    return 0


#Aux function that reads the data of a json and return a dictionary
def read_json(json_path):
    with open(json_path) as json_file:
        return json.load(json_file, encoding='utf-8')


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


#Prints the choices given by param
def print_available_choices(available_choices):
    i = 1
    for available_choice in available_choices:
        print(str(i) + " - " + available_choice["choice"])
        i += 1


#Returns the selected choice from a list of choices
def select_choice(choices):
    while True:
        print("\nWhat are you going to do? ")
        player_choice = input()
        try:
            player_choice = int(player_choice) - 1
            if player_choice >= 0 and player_choice < len(choices):
                return choices[player_choice]
            else:
                print("This is not a correct choice, please try again.")
        except:
            print("This is not a correct choice, please try again.")


#Updates the game state if the object has the property "updates_game_state"
def update_game_state(object, game_state):
    if "updates_game_state" in object:
        updates_game_state = object["updates_game_state"]
        for key in updates_game_state:
            value = updates_game_state[key]
            game_state[key] = value


main()
