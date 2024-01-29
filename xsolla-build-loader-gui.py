import PySimpleGUI as sg                        # Part 1 - The import
import subprocess
from os.path import isdir
from datetime import datetime

def upload_build(output, api_key, game_path, descr, test):
    args = [
        "--init",
        "--api-key", api_key,
        "--game-path", game_path
    ]
    code = call_build_loader(output, args)

    if code != 0:
        return

    test_arg = "--set-build-on-test" if test else "--set-build-on-master"
    args = [
        "--update",
        "--game-path", game_path]
    if descr != "":
        args = args + ["--descr", descr]
    args = args + [test_arg]
    call_build_loader(output, args)


def call_build_loader(output, args):
    args = ["build_loader.exe"] + args
    print("Running {}...".format(" ".join(args)))
    start = datetime.now()

    sp = subprocess.Popen(args=args, stdout=subprocess.PIPE, text=True)
    while True:
        line = sp.stdout.readline()
        if line != "":
            output.print(line, end="")
        
        code = sp.poll()
        if code is not None:
            break

    end = datetime.now()
    print("-------------------------------------------")
    if code == 0:
        print("Program ended successfully. Time elapsed: {}s".format(end-start))
    else:
        print("Program terminated with error {}. Time elapsed: {}s".format(code, end-start))
        pass
    print("-------------------------------------------")

    return code


def verify_values(values):
    if values["api-key"] == "" or values["api-key"] is None:
        print("Please provide a valid API key.")
        return False
    if values["game-path"] == "" or not isdir(values["game-path"]):
        print("Please provide a valid game path.")
        return False
    return True


def clear_output(window):
    window.find_element("output").update(value="")
    

if __name__ == "__main__":
    # Define the window's contents
    layout = [
        [sg.Text("API key (launcher ID):"), sg.Input(expand_x=True, key="api-key")],     # Part 2 - The Layout
        [sg.Text("Game path:"), sg.FolderBrowse(key="game-path", target="game-path-input"), sg.Input(key="game-path-input", disabled=True, expand_x=True, disabled_readonly_background_color="#AAAAAA")],
        [sg.Text("Build description:"), sg.Input(expand_x=True, key="descr")],
        [sg.Text("Build type:"), sg.Radio("Test", 1, default=True, key="set-build-on-test"), sg.Radio("Master", 1, key="set-build-on-master")],
        [sg.Button('Send', key="send", bind_return_key=True, expand_x=True)],
        [sg.Button('Clear log', key="clear-log"), sg.Button('Save log', key="save-log"), sg.Button('Save settings', key="save-settings"), sg.Button('Test', key="test")],
        [sg.MLine(key="output", disabled=True, size=(80, 20), expand_x=True, expand_y=True, no_scrollbar=True, font=('Cascadia Mono Semibold', '10', 'normal'), auto_refresh=True, do_not_clear=False)] ]

    # Create the window
    window = sg.Window('Xsolla Build Launcher GUI', layout)      # Part 3 - Window Defintion
    window.find_element("output").reroute_stdout_to_here()
    
    # Display and interact with the Window
    while True:
        event, values = window.read()                   # Part 4 - Event loop or Window.read call

        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break    
        elif event == 'test':
            print("{}: {}".format(event, values))
        elif event == 'clear-log':
            clear_output(window)
        elif event == 'save-log':
            f = sg.filedialog.asksaveasfile(defaultextension=".log", filetypes=[("Log File", ".log")])
            if f is not None:
                f.write(values["output"])
                f.close()
        elif event == 'save-settings':
            pass
        elif event == 'send':
            values["game-path"] = values["game-path"].replace("/", "\\")
            output = window.find_element("output")
            if verify_values(values):
                clear_output(window)
                window.disable()
                upload_build(output, values["api-key"], values["game-path"], values["descr"], values["set-build-on-test"])
                window.enable()


    # Finish up by removing from the screen
    window.close()                                  # Part 5 - Close the Window