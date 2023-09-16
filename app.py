from flask import Flask, abort
from flask import jsonify
from flask import send_file
from flask import request
from flask import render_template
from PIL import Image
import os
import mimetypes
import json
import random
import time

app = Flask(__name__)


########################################################################
# Data
########################################################################

BODY_COMMON = ['blackpink', 'blackpurple', 'donut', 'dots', 'flower', 'jacket', 'meadow', 'pocket', 'pull', 'ring', 'shirt', 'square', 'striped', 'tree', 'trinity', 'zigzag']
FACE_COMMON = ['bogoss', 'brown', 'caucasian', 'cheekbone', 'clown', 'covid', 'duck', 'glasses', 'green', 'love', 'makeup', 'metis', 'mustache', 'scars', 'stone', 'tired']
HAIR_COMMON = ['angel', 'antenna', 'blonde', 'blue', 'cap', 'clown', 'duck', 'egg', 'eggshell', 'hat', 'horns', 'leaf', 'nenuphar', 'pig', 'stem', 'tails']
BACKGROUND_COMMON = ['meadow', 'orange', 'peach', 'purple', 'sky']

BODY_RARE = ['hiphop', 'rap','skull']
FACE_RARE = ['abe', 'delta', 'pirate']
HAIR_RARE = ['devil', 'elvis', 'headphone', ]
BACKGROUND_RARE = ['galaxy', 'sun']

TOTAL_COMMON = len(BODY_COMMON) * len(FACE_COMMON) * len(HAIR_COMMON)
TOTAL_RARE = len(BODY_RARE) * len(FACE_RARE) * len(HAIR_RARE)
TOTAL_SUPPLY = TOTAL_COMMON + TOTAL_RARE

TOKENS = list(range(1, TOTAL_SUPPLY + 1))


########################################################################
# Routes
########################################################################
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<token_id>')
def read(token_id):
    filename = 'attributes/output/%s.json' % token_id
    #filename = 'attributes/output/0.json'
    return send_file(filename, mimetype='application/json')

@app.route('/<token_id>')
def image(token_id):
    token_id = int(token_id)
    filename = 'images/output/%s.png' % token_id
    #filename = 'images/output/0.png'
    return send_file(filename, mimetype='image/png')

# Error handling

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


########################################################################
# Utility code
########################################################################

def _add_attribute(existing, attribute_name, value, display_type=None):
    trait = {
        'trait_type': attribute_name,
        'value': value
    }
    if display_type:
        trait['display_type'] = display_type
    existing.append(trait)

def _compose_image(image_files, token_id):
    composite = None
    for image_file in image_files:
        foreground = Image.open(image_file).convert('RGBA')

        if composite:
            composite = Image.alpha_composite(composite, foreground)
        else:
            composite = foreground

    output_path = 'images/output/%s.png' % token_id
    composite.save(output_path)

def _characters(bodies, faces, hairs, backgrounds, boost_number_min, boost_number_max):

    for body in bodies:
        body_png = 'images/body/body-%s.png' % body
        body_attr = body

        for face in faces:
            face_png = 'images/face/face-%s.png' % face
            face_attr = face
            for hair in hairs:
                hair_png = 'images/hair/hair-%s.png' % hair
                hair_attr = hair

                background_attr = backgrounds[random.randint(0, (len(backgrounds) - 1))]
                background_png = 'images/background/background-%s.png' % background_attr

                #random ID
                token_id = random.choice(TOKENS)
                TOKENS.remove(token_id)


                # compose images
                _compose_image([background_png, body_png, face_png, hair_png], token_id)

                # write attributes
                attributes = []
                _add_attribute(attributes, 'Background', background_attr)
                _add_attribute(attributes, 'Body', body_attr)
                _add_attribute(attributes, 'Face', face_attr)
                _add_attribute(attributes, 'Hair', hair_attr)
                _add_attribute(attributes, 'Health', random.randint(boost_number_min, boost_number_max), 'boost_number')
                _add_attribute(attributes, 'Agility', random.randint(boost_number_min, boost_number_max), 'boost_number')
                _add_attribute(attributes, 'Stamina', random.randint(boost_number_min, boost_number_max), 'boost_number')
                _add_attribute(attributes, 'Vision', random.randint(boost_number_min, boost_number_max), 'boost_number')
                _add_attribute(attributes, 'Birthday', int(time.time()) , 'date')
                data = {
                    'name': token_id,
                    'description': 'Fantastic creatures in Greek mythology. Cyclop: %s' % token_id,
                    'external_url': 'https://cyclop.cryptixel.art/%s' % token_id,
                    'image': 'https://cyclop.cryptixel.art/%s' % token_id,
                    'attributes': attributes
                }
                with open('attributes/output/%s.json' % token_id, 'w') as f:
                    json.dump(data, f, sort_keys=True, indent=4)

                print(len(TOKENS), token_id, background_png, body_png, face_png, hair_png)
                print(len(TOKENS), token_id, background_attr, body_attr, face_attr, hair_attr)


########################################################################
# Main flow of execution
########################################################################

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
    #_characters(BODY_COMMON, FACE_COMMON, HAIR_COMMON, BACKGROUND_COMMON, 15, 75)
    #_characters(BODY_RARE, FACE_RARE, HAIR_RARE, BACKGROUND_RARE, 75, 99)
