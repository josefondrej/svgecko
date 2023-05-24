import matplotlib.pyplot as plt

from svgecko.svg import SVG

# Load the SVG
svg_path = 'resources/cross.svg'
svg = SVG.from_file(svg_path)

# Define the transformation and apply it to the SVG
transformation = lambda point: (point[0] + 1, point[1] + 1)
svg.transform(transformation=transformation, inplace=True)

# Plot the transformed SVG
image = svg.to_pil_image()
plt.imshow(image)
plt.show()
