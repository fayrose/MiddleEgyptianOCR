import os
import random
import json
class DataLoader:
    def __init__(self, entry_img_folder, data_json_path, char_img_folder):
        self.entry_folder = entry_img_folder
        self.data_path = data_json_path
        self.chars_path = char_img_folder

        with open(self.data_path, 'r') as file:
            self.data = json.load(file)

    def load_all_entries(self):
        lst = []
        for entry in os.listdir(self.entry_folder):
            page_num, indx = self.page_idx_from_filename(entry)
            lst.append(self.load_entry(page_num, indx))
        return lst

    def load_entries_subset(self, num_entries):
        lst = []
        sampled_entries = random.sample(os.listdir(self.entry_folder), num_entries)
        for entry in sampled_entries:
            page_num, indx = self.page_idx_from_filename(entry)
            lst.append(self.load_entry(page_num, indx))

    def load_entries_on_page(self, page_number):
        image_paths = []
        sign_lists = []
        answers = []
        idx = 0
       
        while True:
            image_path = os.path.join(self.entry_folder,
                                       "page{0}_entry{1}.tiff".format(page_number, idx))
            try:
                f = open(image_path)
            except IOError:
                return (image_paths, sign_lists, answers)
            image_path, sign_list, answer = self.load_entry(page_number,idx)

            image_paths.append(image_path)
            sign_lists.append(sign_list)
            answers.append(answer)
            idx += 1

        return (image_paths, sign_lists, answers)

    def load_entry(self, page_number,idx):
        image_path = os.path.join(self.entry_folder,
                                       "page{0}_entry{1}.tiff".format(page_number, idx))
        sign_list = self.data['Pages'][page_number - 1]['EntryData'][idx]['GardinerSigns']
        answer = self.data['Pages'][page_number - 1]['EntryData'][idx]['ManuelDeCodage']
        return (image_path, sign_list, answer)
        
    def page_idx_from_filename(self, entry):
        page_num = entry[4:entry.index("_")]
        indx = entry[entry.index(entry) + 5:entry.index('.')]
        return page_num, indx
        