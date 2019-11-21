from Models.Entry import Entry
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

def main():
    entry = Entry("C:/Users/lfr2l/Desktop/messed.jpg")
    display(entry.image)
    entry.split_into_words()
    entry.split_blocks_into_verticals()
    display(entry.blocks[2].verticals[0].image)

if __name__ == "__main__":
    main()