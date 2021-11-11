# import libraries
import os
import requests
from langdetect import detect
from PIL import Image, ImageFont, ImageDraw
import six
from google.cloud import translate_v2 as translate

#creating empty canvas a3
def create_canvas(bg_color):
    return Image.new('RGB', size = (3508, 4961), color = bg_color)

# getting imdb data by film id
def get_imdb_data(imdb_id):
    try:
        url = 'https://imdb8.p.rapidapi.com/title/get-full-credits'
        querystring = {'tconst':imdb_id}
        headers = {
            'x-rapidapi-host': 'imdb8.p.rapidapi.com',
            'x-rapidapi-key': os.environ['imdbToken']
            
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        imdb_data = response.json()
        return imdb_data
    except:
        print('Getting imdb data failed')
        

# getting kinopoisk data by film id
def get_kinopoisk_data(kinopoisk_id):
    try:
        url = 'https://api.kinopoisk.cloud/movies/{}/token/{}'
        response = requests.get(url.format(kinopoisk_id, os.environ['KinopoiskToken']))
        kinopoisk_data = response.json()
        return kinopoisk_data
    except Exception as e:
        print('Getting kinopoisk data failed: %s', e)

def get_attributes(source, attributes):
    data = dict()
    for attribute in attributes:
        if attribute in source:
            data[attribute] = source[attribute]
        elif attribute in source['collapse']:
            data[attribute] = source['collapse'][attribute]
        else:
            data[attribute] = 'No data'
    return data

def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    translate_client = translate.Client()
    
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    return result['translatedText']
            
def check_tagline(text):
    if text == 'No data':
        return text
    else:
        try:
            text = text.strip('«»')
            lang = detect(text)
            if lang == 'ru':
                return text
            else:
                return translate_text('ru', text)
        except:
            return 'Failed translation'

def check_text_width(text, font_name, font_size, img_width):
    font = ImageFont.truetype(font_name, size=font_size)
    text_width = font.getsize(text)[0]
    while text_width > img_width-312*2:
        font_size -= 2
        font = ImageFont.truetype(font_name, size=font_size)
        text_width = font.getsize(text)[0]
    return font

def parse_duration(text):
    if text == 'No data':
        return text
    else:
        try:
            text = text[0].split(' / ')[0].strip('.')
            return text
        except:
            return 'Failed duration'
    
def get_movie_data(name):
    kinopoisk_id = name.split('_')[-1]
    kinopoisk_data = get_kinopoisk_data(kinopoisk_id)
    attributes = ['title', 'year', 'directors', 'tagline', 'duration']
    data = get_attributes(kinopoisk_data, attributes)
    data['tagline'] = check_tagline(data['tagline'])
    data['duration'] = parse_duration(data['duration'])
    return data

def create_poster(output_path, name, form, donut_path='', stripe_path=''):
    img = create_canvas(bg_color = (227, 220, 213))
    data = get_movie_data(name)
    title = data['title']
    title_font = check_text_width(title, 'fonts/FiraSans/FiraSans-ExtraBold.ttf', 46*4, img.size[0])
    year = data['year']
    year_font = ImageFont.truetype('fonts/FiraSans/FiraSans-ExtraBold.ttf', size=30*4)
    directors = ' | '.join(data['directors'])
    directors_font = ImageFont.truetype('fonts/FiraSans/FiraSans-Regular.ttf', size=20*4)
    tagline = data['tagline']
    tagline_font = check_text_width(tagline, 'fonts/FiraSans/FiraSans-Regular.ttf', 25*4, img.size[0])
    duration = 'Продолжительность: {}'.format(data['duration'])
    duration_font = ImageFont.truetype('fonts/FiraSans/FiraSans-Regular.ttf', size=15*4)
    
    if form == 'lines':
        pass
    elif form == 'donut':
        image_editable = ImageDraw.Draw(img)

        color = (0, 0, 0)

        #adding tagline
        tagline_position = (1754,280)
        image_editable.text(tagline_position, tagline, color, anchor='mt', font=tagline_font)

        #drawing line
        line_position = [((312,428)), (3197, 428)]
        image_editable.line(line_position, fill=color, width=6)
        
        #adding donut
        try:
            donut = Image.open(donut_path)
            donut = donut.resize((2725,2725), Image.ANTIALIAS)
            img.paste(donut, (390, 630), donut)
        except ValueError:
            donut = Image.open(donut_path)
            donut.putalpha(255)
            donut = donut.resize((2725,2725), Image.ANTIALIAS)
            img.paste(donut, (390, 630), donut)
        
        #adding title
        title_position = (1754,3625)
        image_editable.text(title_position, title.upper(), color, anchor='mt', font=title_font)
        
        #adding year
        year_position = (1754,3861)
        image_editable.text(year_position, str(year), color, anchor='mt', font=year_font)

        #adding directors
        directors_position = (1754,4047)
        image_editable.text(directors_position, directors, color, anchor='mt', font=directors_font)
        
        #adding stripe
        try:
            stripe = Image.open(stripe_path)
            stripe = stripe.resize((2884,165), Image.ANTIALIAS)
            img.paste(stripe, (312, 4355), stripe)
        except ValueError:
            stripe = Image.open(stripe_path)
            stripe.putalpha(255)
            stripe = stripe.resize((2884,165), Image.ANTIALIAS)
            img.paste(stripe, (312, 4355), stripe)
            
        
        #adding duration
        duration_position = (312,4593)
        image_editable.text(duration_position, duration, color, anchor='lt', font=duration_font)

        
        
    elif form == 'waves':
        pass
    
    img.save(output_path)