import qrcode
import cv2

# qrc = qrcode.QRCode(
#     version=1,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=10,
#     border=4,
# )
data = "www.youtube.com"
# qrc.add_data(data)
# qrc.make(fit=True)
img = qrcode.make(data)
# qrc.make_image(fill_color="black", back_color="white").convert('RGB')
# img = qrcode.make_image(fill_color="black", back_color="white")
img.save('logo.png')

cv2.imread('logo.png')
