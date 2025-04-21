import dearpygui.dearpygui as imgui
import pyperclip
import re
import os
import Keys

class MainWindow():
    def __init__(self):
        self.CreateViewport()

        with imgui.window(tag="Primary Window"):
            self.CreateMenuBar()
            self.CreateVirtualKeypad()

        imgui.set_primary_window("Primary Window", True)

    def Start(self):
        imgui.start_dearpygui()
        imgui.destroy_context()

    def CreateViewport(self):
        imgui.create_context()
        imgui.create_viewport(title="Keypad Configuration")
        imgui.setup_dearpygui()
        imgui.show_viewport()

    def CreateMenuBar(self):
        with imgui.menu_bar():
            with imgui.menu(label="File", tag="file_menu"):
                imgui.add_menu_item(label="Save", callback=self.SaveConfiguration)
                imgui.add_menu_item(label="Load", callback=self.LoadConfiguration)
            with imgui.menu(label="Tools"):
                # small useful thingey
                imgui.add_menu_item(label="Show About", callback=lambda:imgui.show_tool(imgui.mvTool_About))
                imgui.add_menu_item(label="Show Metrics", callback=lambda:imgui.show_tool(imgui.mvTool_Metrics))
                imgui.add_menu_item(label="Show Documentation", callback=lambda:imgui.show_tool(imgui.mvTool_Doc))
                imgui.add_menu_item(label="Show Debug", callback=lambda:imgui.show_tool(imgui.mvTool_Debug))
                imgui.add_menu_item(label="Show Style Editor", callback=lambda:imgui.show_tool(imgui.mvTool_Style))
                imgui.add_menu_item(label="Show Font Manager", callback=lambda:imgui.show_tool(imgui.mvTool_Font))
                imgui.add_menu_item(label="Show Item Registry", callback=lambda:imgui.show_tool(imgui.mvTool_ItemRegistry))
                imgui.add_menu_item(label="Show Stack Tool", callback=lambda:imgui.show_tool(imgui.mvTool_Stack))

    def CreateVirtualKeypad(self):
        self.keypad_buttons: list[dict] = []  # Store button info for editing
        with imgui.child_window(tag="Keypad Layout", width=650, height=632):
            with imgui.table(tag="Keypad Table", 
                            policy=imgui.mvTable_SizingFixedFit,
                            header_row=False,
                            row_background=False,
                            borders_innerH=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_outerV=True):
                
                for _ in range(4):
                    imgui.add_table_column()

                for row in range(4):
                    with imgui.table_row():
                        for col in range(4):
                            idx = row * 4 + col
                            tag = f"btn_{idx}"
                            default_color = [120, 120, 255, 255]
                            pressed_color = [255, 120, 120, 255]

                            # Store each button's state
                            self.keypad_buttons.append({
                                "tag": tag,# key index = int(tag.strip("btn_"))
                                "color": default_color,
                                "pressed_color": pressed_color,
                                "keys": [],
                                "repeat": False
                            })

                            def _OpenInspector(sender, app_data, user_data):
                                self.OpenButtonInspector(user_data)

                            imgui.add_button(label=f"{[]}", tag=tag, width=150, height=150,
                                            callback=_OpenInspector, user_data=idx)
                            imgui.bind_item_theme(tag, self.CreateButtonTheme(idx))

    def CreateButtonTheme(self, idx):
        """Creates a custom theme for a button to show pressed color on hover."""
        button_info = self.keypad_buttons[idx]
        theme_tag = f"theme_{idx}"
        button_tag = button_info["tag"]

        if (imgui.does_item_exist(theme_tag)):
            imgui.bind_item_theme(button_tag, 0)
            imgui.delete_item(theme_tag)

        with imgui.theme(tag=theme_tag):
            with imgui.theme_component(imgui.mvButton):
                imgui.add_theme_color(imgui.mvThemeCol_Button, button_info["color"])
                imgui.add_theme_color(imgui.mvThemeCol_ButtonHovered, button_info["pressed_color"])
                imgui.add_theme_color(imgui.mvThemeCol_ButtonActive, button_info["pressed_color"])
        
        return theme_tag

    def OpenButtonInspector(self, idx):
        """Opens an inspector window to edit a button's properties."""
        button = self.keypad_buttons[idx]

        if not imgui.does_item_exist("Button Inspector"):
            with imgui.window(label=f"Inspector - Button {idx}", tag="Button Inspector", width=600, height=400, modal=True, no_resize=False, on_close=lambda:imgui.delete_item("Button Inspector")):
                imgui.add_text(f"Editing Button {idx}")

                def _CopyReleventButtonData():
                    color = button["color"]
                    pColor = button["pressed_color"]
                    keys = button["keys"]

                    colStr =f"{color[0]},{color[1]},{color[2]}"
                    pColStr =f"{pColor[0]},{pColor[1]},{pColor[2]}"
                    keysStr ="None"

                    if (len(keys) > 0):
                        keysStr = ""
                        for i in range(len(keys)):
                            keysStr += f"{keys[i]}{"," if (not i == len(keys) - 1) else ""}"

                    pyperclip.copy(f"{colStr}|{pColStr}|{keysStr}|{button["repeat"]}")
                
                def _PasteReleventButtonData():# thanks chatgpt
                    text = pyperclip.paste()
                    pattern = re.compile(r"(\d+),(\d+),(\d+)\|(\d+),(\d+),(\d+)\|([^|]*)\|(True|False)")
                    match = pattern.match(text)
                    if (not match):
                        print("Text in clipboard dosent match pattern")
                        return
                    
                    r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    pr, pg, pb = int(match.group(4)), int(match.group(5)), int(match.group(6))
                    key_str = match.group(7)
                    repeat = match.group(8) == "True"

                    keys = [int(k.strip()) for k in key_str.split(",")] if key_str.strip() else []

                    button["color"] = [r, g, b, 255]
                    button["pressed_color"] = [pr, pg, pb, 255]
                    button["keys"] = keys
                    button["repeat"] = repeat

                    # Update theme to reflect new colors
                    tag = button["tag"]
                    imgui.bind_item_theme(tag, self.CreateButtonTheme(idx))

                    imgui.set_value("color_selection", [r, g, b, 255])
                    imgui.set_value("pressed_color_selection", [pr, pg, pb, 255])
                    imgui.set_value("repeat_toggle", repeat)

                    self.UpdateDisplayedValues(idx)

                    #print(f"Pasted to Button {idx}: {button}")

                with imgui.group(horizontal=True):
                    imgui.add_button(label="Copy", callback=_CopyReleventButtonData)
                    imgui.add_button(label="Paste", callback=_PasteReleventButtonData)

                imgui.add_checkbox(label="Repeat", tag="repeat_toggle", default_value=button["repeat"],
                                callback=lambda s, a, u: self.UpdateButtonRepeat(idx, a))

                with imgui.group(horizontal=True):
                    imgui.add_text("Key Binding")

                    imgui.add_combo(["None"] + Keys.keys, tag="key_choice_btn_0", default_value="None", width=80, callback=lambda s, a, u: self.UpdateButtonKey(idx, 0, a))
                    imgui.add_combo(["None"] + Keys.keys, tag="key_choice_btn_1", default_value="None", width=80, callback=lambda s, a, u: self.UpdateButtonKey(idx, 1, a))
                    imgui.add_combo(["None"] + Keys.keys, tag="key_choice_btn_2", default_value="None", width=80, callback=lambda s, a, u: self.UpdateButtonKey(idx, 2, a))

                    self.UpdateDisplayedValues(idx) # easiest way i can think right now to sync values

                with imgui.group(horizontal=True):
                    # might be able to use imgui.add_color_edit
                    imgui.add_color_picker(label="Color", tag="color_selection", default_value=button["color"], width=200, display_rgb=True,
                                           callback=lambda s, a, u: self.UpdateButtonColor(idx, a, is_pressed=False))

                    imgui.add_color_picker(label="Pressed Color", tag="pressed_color_selection", default_value=button["pressed_color"], width=200, display_rgb=True,
                                           callback=lambda s, a, u: self.UpdateButtonColor(idx, a, is_pressed=True))

    def UpdateButtonColor(self, idx, color, is_pressed=False):
        if is_pressed:
            self.keypad_buttons[idx]["pressed_color"] = [round(color[0] * 255), round(color[1] * 255), round(color[2] * 255), 255]
        else:
            self.keypad_buttons[idx]["color"] = [round(color[0] * 255), round(color[1] * 255), round(color[2] * 255), 255]

        # Re-apply theme
        tag = self.keypad_buttons[idx]["tag"]
        imgui.bind_item_theme(tag, self.CreateButtonTheme(idx))

    def UpdateDisplayedValues(self, idx):
        #set all displayed values
        for i in range(3):
            if (len(self.keypad_buttons[idx]["keys"]) >= i+1):
                imgui.set_value(f"key_choice_btn_{i}", Keys.inverseValues[self.keypad_buttons[idx]["keys"][i]])
            else:
                imgui.set_value(f"key_choice_btn_{i}", "None")

        keysStr = self.GetkeysString(self.keypad_buttons[idx]["keys"])
        imgui.configure_item(self.keypad_buttons[idx]["tag"], label=keysStr)


    def UpdateButtonKey(self, idx, keyIndex, keyName):
        keys: list = self.keypad_buttons[idx]["keys"]

        if (keyName == "None"):
            # remove this key and any keys after
            while (len(keys) > keyIndex):
                keys.pop(keyIndex)
            self.UpdateDisplayedValues(idx)
            return

        if (keys.__contains__(Keys.values[keyName])):
            self.UpdateDisplayedValues(idx)
            return # do nothing, don't want to have multiples of keys
        
        if (len(keys) == keyIndex):
            keys.append(Keys.values[keyName])
        elif (len(keys) > keyIndex):
            keys[keyIndex] = Keys.values[keyName]

        self.keypad_buttons[idx]["keys"] = keys

        self.UpdateDisplayedValues(idx)

    def UpdateButtonRepeat(self, idx, repeat):
        self.keypad_buttons[idx]["repeat"] = repeat
    
    def SaveConfiguration(self):
        print("Saving")
        saveStr = ""
        for btn in self.keypad_buttons:
            index = int(btn["tag"].strip("btn_"))
            color = btn["color"]
            pColor = btn["pressed_color"]
            keys = btn["keys"]

            colStr =f"{color[0]},{color[1]},{color[2]}"
            pColStr =f"{pColor[0]},{pColor[1]},{pColor[2]}"
            keysStr ="None"

            if (len(keys) > 0):
                keysStr = ""
                for i in range(len(keys)):
                    keysStr += f"{keys[i]}{"," if (not i == len(keys) - 1) else ""}"
            
            # index|color|pressed color|keys to press|repeat
            saveStr += f"{index}|{colStr}|{pColStr}|{keysStr}|{btn["repeat"]}\n"

        with open("KeypadSave.save", "wt") as file:
            file.write(saveStr)

        print("Saved")

    def LoadConfiguration(self):
        print("Loading")
        if (os.path.exists("KeypadSave.save")):
            with open("KeypadSave.save", "r") as file:
                keysList = []
                file.seek(0)

                for line in file.readlines():
                    line = line.strip(' ')
                    #previousSaveHash += line
                    tokens = line.split("|")
                    colorTokens = tokens[1].split(",")
                    pressedColorTokens = tokens[2].split(",")

                    index = int(tokens[0])
                    color = (int(colorTokens[0]), int(
                        colorTokens[1]), int(colorTokens[2]))
                    pressedColor = (int(pressedColorTokens[0]), int(
                        pressedColorTokens[1]), int(pressedColorTokens[2]))
                    repeting = tokens[4].lower() == "true"
                    
                    tag = f"btn_{index}"

                    keys = []
                    if (not tokens[3] == "None"):
                        for key in tokens[3].split(","):
                            keys.append(int(key))

                    keyVar = {
                        "tag": tag,
                        "color": [color[0], color[1], color[2], 255],
                        "pressed_color": [pressedColor[0], pressedColor[1], pressedColor[2], 255],
                        "keys": keys,
                        "repeat": repeting
                        }

                    keysList.append(keyVar)

                self.keypad_buttons = keysList

                for btn in self.keypad_buttons:
                    imgui.bind_item_theme(btn["tag"], self.CreateButtonTheme(int(btn["tag"].strip("btn_"))))
                    keysStr = self.GetkeysString(btn["keys"])
                    imgui.configure_item(btn["tag"], label=keysStr)

        print("Loaded")

    def GetkeysString(self, list: list[int]) -> str:
        keysStr = ""
        for key in list:
            if (not list[len(list) - 1] == key):
                keysStr += f"{Keys.inverseValues[key]}, "
            else:
                keysStr += f"{Keys.inverseValues[key]}"

        return keysStr


mw = MainWindow()
mw.Start()
