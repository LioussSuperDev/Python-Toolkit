import json
import os


def save_data(data, full_path = None, folder = None, file = None):
    if full_path == None:
        if not os.path.isdir(folder):
            os.makedirs(folder)
        full_path = os.path.join(folder, file)
        
    with open(full_path, "w+") as f:
        json.dump(data, f)
        
def load_data(full_path = None, folder = None, file = None):
    if full_path == None:
        full_path = os.path.join(folder, file)
        
    with open(full_path, "r") as f:
        return json.load(f)