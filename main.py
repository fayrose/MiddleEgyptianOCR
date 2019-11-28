from Models.Entry import Entry
import matplotlib.pyplot as plt
from Services.DataLoader import DataLoader

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

    allEntries = []
    entry_img_folder = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/entry_images"
    data_json_path = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/DatasetGenerator/data.json"
    char_img_folder = "/Users/thomashorga/Documents/CSC420/Visual_Vygus/character_images"
    dataLoader = DataLoader(entry_img_folder,data_json_path,char_img_folder)
    image_path,sign_list,answer = dataLoader.load_entries_on_page(3)
    for i in range(len(image_path)):
        entry = Entry(image_path[i])
        entry.gardiners = sign_list[i]
        entry.process_image()
        allEntries.append(entry)
    # entry = Entry("/Users/thomashorga/Documents/CSC420/MiddleEgyptianOCR/sample4.png")
    # entry.gardiners = ["A1","B1","Z2", "Z2B","N16"]
    # display(entry.image)
    # entry.split_into_words()
    # entry.split_blocks_into_verticals()
    # display(entry.blocks[0].image)
    # display(entry.blocks[0].verticals[1].image)


if __name__ == "__main__":
    main()