from fileinput import filename
from json import load
import string
from os import listdir
from pickle import dump
from keras.applications.vgg16 import VGG16
from matplotlib import lines
from matplotlib.pyplot import table
from tensorflow.keras.utils import load_img,img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.models import Model

# extract features from each photo in the directory

def extract_features(directory):
    #load the model
    model = VGG16()
    # re-structure the model
    model.layers.pop()
    model = Model(inputs = model.inputs , outputs = model.layers[-1].output)
    # summarize
    print(model.summary())
    # extract features from each photo
    features = dict()
    for name in listdir(directory):
        # load an image from file
        filename = directory + '/' + name
        image = load_img(filename , target_size = (224, 224))
        # convert the image pixels to numpy array
        image = img_to_array(image)
        # reshape data for the model
        image = image.reshape((1,image.shape[0], image.shape[1], image.shape[2]))
        # prepare the image for the VGG model
        image = preprocess_input(image)
        # get features
        feature = model.predict(image, verbose=0)
        # get image id
        image_id = name.split('.')[0]
        #store feature
        features[image_id] = feature
        print('>%s' % name)
    return features

# extract features from all images
directory = 'Flicker8k_Dataset'
features = extract_features(directory)
print('Extracted features : %d' % len(features))

# save to file
dump(features , open('Image_Caption_Project_model_data/features.pkl', 'wb'))


# load doc into memory
def load_doc(filename):
    # open file as read only
    file = open(filename, 'r')
    # read all text
    text = file.read()
    # close the file
    file.close()
    return text

# extract descriptions for images
def load_descriptions(doc):
    mapping = dict()
    # process lines
    for line in doc.split('\n'):
        # split line by white spaces
        tokens = line.split()
        if len(line) < 2:
            continue
        # take the first token as the image_id , the rest as the description
        image_id , image_desc = tokens[0], tokens[1:]
        # remove filename from image_id
        image_id = image_id.split('.')[0]
        # convert description tokens back to strings  
        image_desc = ' '.join(image_desc)
        # create the list if needed
        if image_id not in mapping:
            mapping[image_id] = list()

        # store description
        mapping[image_id].append(image_desc)
    return mapping

def clean_description(description):
    # prepare translation table for removing punctuation
    table = str.maketrans('', '', string.punctuation)
    for key , desc_list in description.items(): 
        for i in range(len(desc_list)) :
            desc = desc_list[i]
            # tokenize
            desc = desc.split()
            # convert to lower case
            desc = [word.lower() for word in desc]
            # remove punctuation from each token
            desc = [w.translate(table) for w in desc]
            # remove hanging 's' ans 'a'    
            desc = [word for word in desc if len(word)>1]
            # remove tokens with numbers in them
            desc = [word for word in desc if word.isalpha()]
            # store as string
            desc_list[i] = ' '.join(desc)

# convert the loaded description into vocabulary of words
def to_vocabulary(descriptions):
    # build a list of all description strings
    all_desc = set()
    for key in descriptions.keys():
        [all_desc.update(d.split()) for d in descriptions[key]] 
    return all_desc


# save descriptions to file,  one per line
def save_descriptions(descriptions, filename):
    lines = list()
    for key, desc_list in descriptions.items():
        for desc in desc_list:
            lines.append(key + ' ' + desc)
    data = '\n'.join(lines)
    file = open(filename,'w')
    file.write(data)
    file.close()

# filename = 'flickr8k_text/flickr8k.tokens.txt'
filename = 'Flickr8k.token.txt'
#load descriptions
doc = load_doc(filename)
# parse descriptions
descriptions = load_descriptions(doc)
print('Loaded: %d ' % len(descriptions))

# clean descriptions
clean_description(descriptions)
# summarize vocabulary
vocabulary = to_vocabulary(descriptions)
print('Vocabulary size : %d' % len(descriptions))
# save to file
save_descriptions(descriptions, 'Image_Caption_Project_model_data/descriptions.txt')


        

        
        
