import matplotlib.pyplot as plt

def display(image, boundaries=None, vertical=True):
    plt.imshow(image)
    if boundaries is not None:
        if vertical:
            for boundary in boundaries:
                plt.axvline(boundary)
        else:
            for boundary in boundaries:
                plt.axhline(boundary)
    plt.show()
