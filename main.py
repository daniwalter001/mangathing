
from kakalot import kakalot
from origin import origin, clear

main_menu_options = {
    1: 'Origin',
    2: 'Kakalot',
    3: 'Exit',
}


def print_menu():
    for key in main_menu_options.keys():
        print(key, '--', main_menu_options[key])


if __name__ == "__main__":
    try:
        while True:
            print_menu()
            option = ''
            try:
                option = int(input('Enter your choice: '))
                clear()
            except:
                print('Wrong input. Please enter a number ...')
            if option == 1:
                origin()
            elif option == 2:
                kakalot()
            else:
                exit()
    except KeyboardInterrupt:
        print("Program exited.\n")
