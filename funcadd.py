# import libraries
import pickle

# saving data
def save_data(data, path):
    with open(path+'.pkl', 'wb') as file:
        pickle.dump(data, file)

# loading data
def load_data(path):
    return pickle.load(open(path+'.pkl', 'rb'))

# saving progress
def update_progress(name):
    try:
        with open('progress.txt', 'a') as file:
            file.write(name)
            file.write('\n')
    except:
        print('Smth went wrong while saving progress')