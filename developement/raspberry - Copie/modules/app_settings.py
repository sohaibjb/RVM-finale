# ///////////////////////////////////////////////////////////////
#
# BY: EZOUAGH YOUNESS
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
#
# ///////////////////////////////////////////////////////////////


class Settings:
    # APP SETTINGS
    # ///////////////////////////////////////////////////////////////
    ENABLE_CUSTOM_TITLE_BAR = True
    MENU_WIDTH = 240
    LEFT_BOX_WIDTH = 240
    RIGHT_BOX_WIDTH = 240
    TIME_ANIMATION = 100

    # BTNS LEFT AND RIGHT BOX COLORS
    BTN_LEFT_BOX_COLOR = "background-color: rgb(44, 49, 58);"
    BOX_THEME = "QMessageBox{background-color:rgb(44, 49, 58);color: white;}QMessageBox > QLabel {color: white;} "
    BTN_RIGHT_BOX_COLOR = "background-color: #ff79c6;"
    SELECTED_MODE = "{border-right: 5px solid rgb(0, 170, 255);border-left: 5px solid aqua;}"

    # MENU SELECTED STYLESHEET
    MENU_SELECTED_STYLESHEET = """
    border-left: 8px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
    background-color: rgb(40, 44, 52);
    """
