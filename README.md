<div align="center">
  
# Reverse Vending Machine (RVM)

<img src="./assets/project2.png" width="420">

<br>

**AI • Computer Vision • Embedded Systems • TensorFlow • OpenCV • Raspberry Pi • PyQt5 • Automation • Mechatronics • IoT**

<br>

*Graduation Project - State Engineering Diploma - Electronic and Automatic Systems*  
*ENSA Tangier · 2022–2023*

</div>

<hr>



# Reverse Vending Machine (RVM) - Automated Sorting Waste Classification Prototype


This project is a Qt-based recycling and waste-sorting vision mechanism . The main application provides a touchscreen desktop UI is built on a camera for waste classification with a TensorFlow Lite model and controlled GPIO hardware from a raspberry pi that work together to detect an item, classify it, and react through the UI and motors.


RVM is a PyQt5-based GUI application developed for Raspberry Pi. It provides a touchscreen-friendly desktop UI, UI resources (icons and images), and a motor-control module so the application can control attached hardware (motors) from the GUI.

## Stack
- **Language(s):** Python 3
- **Framework / runtime:** PyQt5 (Qt Designer .ui files compiled with pyuic5 / pyrcc5)
- **Notable libraries:** PyQt5, standard Raspberry Pi GPIO libraries (used in motor control code)


## How it's organized (important files)
- developement/raspberry/
  - `main.py` / `raspberry_main.py` — application entrypoints that start the Qt event loop and wire UI to application logic.
  - `ui_pano.ui`, `messagebox.ui` — Qt Designer files (source UI layout).
  - `res_img.qrc` — Qt resource collection (references images/icons used by the UI).
  - `modules/` — generated Python modules from .ui/.qrc and helper modules:
    - `ui_main.py`, `ui_main_2.py` — UI class glue generated from `ui_pano.ui`.
    - `messagebox.py` — generated from `messagebox.ui`.
    - `resources.py` — compiled resources (contains embedded image assets used by the UI).
    - `ui_functions.py`, `app_settings.py` — small helper modules for UI behavior and settings.
  - `motor.py` — motor control / hardware interface (GPIO interaction lives here).
  - `images/` — icons and images used by the UI.


## How it fits together (runtime shape)
1. The application starts in `main.py` or `raspberry_main.py` which create a QApplication and the main window object.
2. Generated UI modules (from `modules/ui_main.py` / `modules/ui_main_2.py`) provide UI classes which the entrypoint imports and instantiates.
3. The UI code imports `modules/resources.py` so icons/images are available via Qt resource paths.
4. When the user interacts with the UI, event handlers call helper functions in `modules/ui_functions.py` or `app_settings.py` and, for hardware actions, call `motor.py` to actuate motors via GPIO.


Mermaid-style (also included) — renderable on GitHub if your viewer supports Mermaid:
roduce a guided walkthrough of the startup flow and key functions.
