# import libraries
import os
import requests
from langdetect import detect
from PIL import Image, ImageFont, ImageDraw
import six
from google.cloud import translate_v2 as translate
from dimensions import canvas
import random
from io import BytesIO

#creating empty canvas a3
def create_background(bg_color, canvas_size):
    return Image.new('RGB', size = canvas_size, color = bg_color)

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

def filter_images(images, ig_post, stack):
    frame_width = ig_post[0]
    frame_height = int(ig_post[1]/stack)
    frame_size = (frame_width,frame_height)
    target_ratio = frame_width/frame_height
    
    filtered_images = []
    for i in images:
        try:
            image_raw = requests.get(i)
            image = Image.open(BytesIO(image_raw.content))
            width, height = image.size
            if width > height:
                crop_mark = image.crop((0, 0, width, height*0.9))
                ratio = crop_mark.size[0]/crop_mark.size[1]
                if ratio > target_ratio:
                    cr_area = (crop_mark.size[0] - crop_mark.size[1] * target_ratio) / 2
                    top = int(cr_area)
                    bottom = int(crop_mark.size[0] - cr_area)
                    left = 0
                    right = crop_mark.size[1]
                    cropped = image.crop((top, left, bottom, right))
                elif ratio < target_ratio:
                    cr_area = (crop_mark.size[1] - crop_mark.size[0] / target_ratio) / 2
                    top = 0
                    bottom = crop_mark.size[0]
                    left = int(cr_area)
                    right = int(crop_mark.size[1] - cr_area)
                    cropped = image.crop((top, left, bottom, right))                        
                cropped.thumbnail(frame_size, Image.LANCZOS)
                width, height = cropped.size
                if width+1 >= frame_width:
                    if height+1 >= frame_height:
                        cropped.putalpha(255)
                        filtered_images.append(cropped)
        except:
            pass
    return filtered_images        
        
def merge_images(frames, name, ig_post, stack):
    def random_index():
        return random.randint(0,1000)
    
    frame_height = int(ig_post[1]/stack)
        
    img = Image.new('RGB', size = ig_post)
    sample = random.sample(frames,stack)
    frame_position = 0
    for frame in sample:
        img.paste(frame, (0,frame_position), frame)
        frame_position += frame_height
    output_path = os.path.join('output', name, '{}_frames{}.png'.format(name, random_index()))
    img.save(output_path, dpi=(300, 300))
    
def get_movie_data(name, stack=2, quantity=10):
    kinopoisk_id = name.split('_')[-1]
    kinopoisk_data = get_kinopoisk_data(kinopoisk_id)
    frames = kinopoisk_data['frames']
    screenshots = kinopoisk_data['screenshots']
    ig_post = (720,900)
    try:
        images = frames+screenshots
    except TypeError:
        images = frames
    images = filter_images(images, ig_post, stack)
    for i in range(quantity):
        merge_images(images, name, ig_post, stack)
    attributes = ['title', 'year', 'directors', 'tagline', 'duration', 'rating_kinopoisk']
    data = get_attributes(kinopoisk_data, attributes)
    data['tagline'] = check_tagline(data['tagline'])
    data['duration'] = parse_duration(data['duration'])
    return data

def create_poster(poster_size, output_path, name, form, donut_path='', stripe_path=''):
    img = create_background(bg_color = (255, 255, 255), canvas_size = canvas[poster_size]['size'])
    data = get_movie_data(name)
    title = data['title']
    title_font = check_text_width(title, 'fonts/FiraSans/FiraSans-ExtraBold.ttf', canvas[poster_size]['title_font_size'], img.size[0])
    year = data['year']
    year_font = ImageFont.truetype('fonts/FiraSans/FiraSans-ExtraBold.ttf', size=canvas[poster_size]['year_font_size'])
    directors = ' | '.join(data['directors'])
    directors_font = ImageFont.truetype('fonts/FiraSans/FiraSans-Regular.ttf', size=canvas[poster_size]['directors_font_size'])
    tagline = data['tagline']
    tagline_font = check_text_width(tagline, 'fonts/FiraSans/FiraSans-Regular.ttf', canvas[poster_size]['tagline_font_size'], img.size[0])
    duration = data['duration']
    duration_font = ImageFont.truetype('fonts/FiraSans/FiraSans-Regular.ttf', size=canvas[poster_size]['duration_font_size'])
    rating = str(data['rating_kinopoisk'])
    rating_font = ImageFont.truetype('fonts/FiraSans/FiraSans-Regular.ttf', size=canvas[poster_size]['rating_font_size'])
    
    
    if form == 'lines':
        pass
    elif form == 'donut':
        image_editable = ImageDraw.Draw(img)

        color = (0, 0, 0)

        #adding tagline
        tagline_position = canvas[poster_size]['tagline_position']
        image_editable.text(tagline_position, tagline, color, anchor='mt', font=tagline_font)

        #drawing line
        line_position = canvas[poster_size]['line_position']
        image_editable.line(line_position, fill=color, width=canvas[poster_size]['line_size'])
        
        #adding donut
        donut = Image.open(donut_path)
        donut = donut.resize(canvas[poster_size]['donut_size'], Image.ANTIALIAS)
        try:
            img.paste(donut, canvas[poster_size]['donut_position'], donut)
        except ValueError:
            donut.putalpha(255)
            img.paste(donut, canvas[poster_size]['donut_position'], donut)
        
        #adding title
        title_position = canvas[poster_size]['title_position']
        image_editable.text(title_position, title.upper(), color, anchor='mt', font=title_font)
        
        #adding year
        year_position = canvas[poster_size]['year_position']
        image_editable.text(year_position, str(year), color, anchor='mt', font=year_font)

        #adding directors
        directors_position = canvas[poster_size]['directors_position']
        image_editable.text(directors_position, directors, color, anchor='mt', font=directors_font)
        
        #adding stripe
        stripe = Image.open(stripe_path)
        stripe = stripe.resize(canvas[poster_size]['stripe_size'], Image.ANTIALIAS)
        try:
            img.paste(stripe, canvas[poster_size]['stripe_position'], stripe)
        except ValueError:
            stripe.putalpha(255)
            img.paste(stripe, canvas[poster_size]['stripe_position'], stripe)
        
        #adding clock
        clock = Image.open('resources/clock.png')
        clock = clock.resize(canvas[poster_size]['clock_size'], Image.ANTIALIAS)
        try:
            img.paste(clock, canvas[poster_size]['clock_position'], clock)
        except ValueError:
            clock.putalpha(255)
            img.paste(clock, canvas[poster_size]['clock_position'], clock)
        
        #adding duration
        duration_position = canvas[poster_size]['duration_position']
        image_editable.text(duration_position, duration, color, anchor='lm', font=duration_font)
        
        #adding kinopoisk_logo
        kinopoisk = Image.open('resources/kinopoisk.png')
        kinopoisk = kinopoisk.resize(canvas[poster_size]['kinopoisk_size'], Image.ANTIALIAS)
        try:
            img.paste(kinopoisk, canvas[poster_size]['kinopoisk_position'], kinopoisk)
        except ValueError:
            clock.putalpha(255)
            img.paste(kinopoisk, canvas[poster_size]['kinopoisk_position'], kinopoisk)
        
        #adding rating
        rating_position = canvas[poster_size]['rating_position']
        image_editable.text(rating_position, rating, color, anchor='lm', font=rating_font)
        
        #adding dp_logo
        logo = Image.open('resources/logo.png')
        logo = logo.resize(canvas[poster_size]['logo_size'], Image.ANTIALIAS)
        try:
            img.paste(logo, canvas[poster_size]['logo_position'], logo)
        except ValueError:
            clock.putalpha(255)
            img.paste(logo, canvas[poster_size]['logo_position'], logo)
        
    elif form == 'waves':
        pass
    
    img.save(output_path, dpi=(300, 300))