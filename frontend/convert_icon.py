from PIL import Image

# Open the PNG image
img = Image.open("icons/app-icon.png")

# Convert to ICO format and save
img.save("icons/app-icon.ico", format="ICO")

print("Icon converted successfully!")
