pyuic5 -o modules\ui_main.py ui_pano.ui
pyuic5 -o modules\messagebox.py messagebox.ui

pyrcc5 res_img.qrc -o modules\resources.py