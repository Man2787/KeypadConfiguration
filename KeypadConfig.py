import dearpygui.dearpygui as imgui

class MainWindow():
    def __init__(self):
        self.CreateViewport()

        with imgui.window(tag="Primary Window"):
            self.CreateMenuBar()

            imgui.add_text("Hello world")

            self.CreateVirtualKeypad()

        imgui.set_primary_window("Primary Window", True)

    def CreateViewport(self):
        imgui.create_context()
        imgui.create_viewport(title="Keypad Configuration")
        imgui.setup_dearpygui()
        imgui.show_viewport()

    def SaveConfiguration(self):
        print("Saving")
        #TODO: Save config
        #testing
        saveStr = ""
        for btn in self.keypad_buttons:
            index = int(btn["tag"].strip("btn_"))
            color = btn["color"]
            pColor = btn["pressed_color"]
            saveStr += f"{index}|{color[0]},{color[1]},{color[2]}|{5}|{5}\r\n"

        print(saveStr)

        print("Saved")

    def LoadConfiguration(self):
        print("Loading")
        #TODO: Load config
        print("Loaded")

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
        with imgui.child_window(tag="Keypad Layout", width=700, height=700):
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
                                "key": f"Key {idx}",
                                "repeat": False
                            })

                            def _open_inspector(sender, app_data, user_data):
                                self.OpenButtonInspector(user_data)

                            imgui.add_button(tag=tag, width=150, height=150,
                                            callback=_open_inspector, user_data=idx)
                            imgui.bind_item_theme(tag, self.CreateHoverTheme(idx))

    def CreateHoverTheme(self, idx):
        """Creates a custom theme for a button to show pressed color on hover."""
        button_info = self.keypad_buttons[idx]
        theme_tag = f"theme_{idx}"

        if imgui.does_item_exist(theme_tag):
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
            with imgui.window(label=f"Inspector - Button {idx}", tag="Button Inspector", width=300, height=300, modal=True, no_resize=False, on_close=lambda:imgui.delete_item("Button Inspector")):
                imgui.add_text(f"Editing Button {idx}")

                #TODO: change for correct key setting
                imgui.add_input_text(label="Key Binding", default_value=button["key"],
                                    callback=lambda s, a, u: self.UpdateButtonKey(idx, a))
                
                imgui.add_checkbox(label="Repeat", default_value=button["repeat"],
                                callback=lambda s, a, u: self.UpdateButtonRepeat(idx, a))

                imgui.add_color_picker(label="Color", default_value=button["color"],
                                        callback=lambda s, a, u: self.UpdateButtonColor(idx, a, is_pressed=False))

                imgui.add_color_picker(label="Pressed Color", default_value=button["pressed_color"],
                                        callback=lambda s, a, u: self.UpdateButtonColor(idx, a, is_pressed=True))

    def UpdateButtonColor(self, idx, color, is_pressed=False):
        if is_pressed:
            self.keypad_buttons[idx]["pressed_color"] = color
        else:
            self.keypad_buttons[idx]["color"] = color

        # Re-apply theme
        tag = self.keypad_buttons[idx]["tag"]
        imgui.bind_item_theme(tag, self.CreateHoverTheme(idx))

    def UpdateButtonKey(self, idx, key):
        self.keypad_buttons[idx]["key"] = key

    def UpdateButtonRepeat(self, idx, repeat):
        self.keypad_buttons[idx]["repeat"] = repeat

    '''
    def CreateVirtualKeypad(self):
        #TODO: add a 4x4 button grid that displays buttons with a 1:1 aspect ratio
        #TODO: the buttons need to open a inspector window where you can change the buttons properties ie. color, pressed color, keys, repeting
        #TODO: the buttons are normally color but when hovering they display the pressed color

        layout_child = imgui.generate_uuid()
        with imgui.child_window(tag=layout_child, width=700, height=700):
            layout_table = imgui.generate_uuid()
            with imgui.table(tag=layout_table, policy=imgui.mvTable_SizingFixedFit, header_row=False, row_background=False,
                                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                borders_outerV=True, delay_search=True) as table_id:

                imgui.add_table_column(label="Header 1")
                imgui.add_table_column(label="Header 2")
                imgui.add_table_column(label="Header 3")
                imgui.add_table_column(label="Header 4")

                for i in range(4):
                    with imgui.table_row():
                        for j in range(4):
                            imgui.add_text(f"")
                            #imgui.add_text(f"Row{i} Column{j}")
    '''
    
    def Start(self):
        imgui.start_dearpygui()
        imgui.destroy_context()

mw = MainWindow()
mw.Start()