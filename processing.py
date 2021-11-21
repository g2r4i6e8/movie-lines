# import libraries
import numpy as np
import matplotlib.pyplot as plt
import cv2
from tqdm import tqdm
import math
import sys
from PIL import Image, ImageDraw
import math

# calculating perceived brightness of color by converting to greyscale
def get_color_brightness(c):
    return ((c[0] * 0.2989) + (c[1] * 0.5870) + (c[2] * 0.114))

# creating lined diagrams
def plot_lines(lines, path):
    plt.style.use('default')
    plt.figure(figsize=(10, 15))
    plt.axis('off')
    plt.imshow(lines)
    plt.savefig(path, dpi = 1000, bbox_inches='tight', pad_inches = 0)
    plt.close()
    
# creating donut diagram
def plot_donut(pielines, path, background_style='default'):
    values = np.ones(len(pielines))
    colorset = [tuple(c) for c in pielines]
    if background_style=='white':
        circle_color = 'white'
        facecolor='white'
    elif background_style=='dark':
        circle_color = 'black'
        facecolor = 'black'
    elif background_style=='beige':
        circle_color = '#e3dcd5'
        facecolor = '#e3dcd5'
    
    fig=plt.figure(figsize=(10, 15), facecolor=facecolor)
    plt.pie(values, colors = colorset, startangle = 90, counterclock=False)
    circle=plt.Circle( (0,0), 0.333, color=circle_color)
    p=plt.gcf()
    p.gca().add_artist(circle)
    plt.xlim([-1.0, 1.0])
    plt.ylim([-1.0, 1.0])
    plt.savefig(path, dpi = 1500, bbox_inches='tight', pad_inches = 0)
    plt.close()
    
# creating interpolated donut diagram
def plot_interpolated_donut(interpolated_image_path, output_path, background_style='default'):
    Ro = 2400.0
    Ri = 800.0
    
    if background_style == 'white':
        bg_color = (255,255,255)
    elif background_style == 'beige':
        bg_color = (227,220,213)
    
    circle = [[bg_color for x in range(int(Ro * 2))] for y in range(int(Ro * 2))]
    
    
    image = Image.open(interpolated_image_path)
    pixels = image.load()
    width, height = image.size
    
    for i in range(int(Ro)):
        outer_radius = math.sqrt(Ro*Ro - i*i)
        for j in range(-int(outer_radius),int(outer_radius)):
            if i < Ri:
                inner_radius = math.sqrt(Ri*Ri - i*i)
            else:
                inner_radius = -1
            if j < -inner_radius or j > inner_radius:
                x = Ro+j
                y = Ro-i
                # calculate source
                angle = math.atan2(y-Ro,x-Ro)/2
                distance = math.sqrt((y-Ro)*(y-Ro) + (x-Ro)*(x-Ro))
                distance = math.floor((distance-Ri+1)*(height-1)/(Ro-Ri))
                circle[int(y)][int(x)] = pixels[int(width*angle/math.pi) % width, height-distance-1]
                y = Ro+i
                # calculate source
                angle = math.atan2(y-Ro,x-Ro)/2
                distance = math.sqrt((y-Ro)*(y-Ro) + (x-Ro)*(x-Ro))
                distance = math.floor((distance-Ri+1)*(height-1)/(Ro-Ri))
                circle[int(y)][int(x)] = pixels[int(width*angle/math.pi) % width, height-distance-1]
    
    list_image = [item for sublist in circle for item in sublist]
    new_image = Image.new('RGB', (len(circle[0]), len(circle)))
    new_image.putdata(list_image)
    new_image = new_image.rotate(90)
    new_image.save(output_path, 'PNG')
    
# creating wave diagram
def plot_waves(wavelines, path, background_style='default'):
    width = wavelines.shape[0]
    values = [y for x in range(1, width+1) for y in [x, x]]
    colors = [tuple(c) for c in wavelines]
    colorset = [y for x in colors for y in [x, x]]
    bright_level = [get_color_brightness(c) for c in colors]
    brightness = [y for x in bright_level for y in [-x, x]]
    if background_style=='default':
        facecolor = 'white'
    elif background_style=='dark':
        facecolor = 'black'
    elif background_style=='beige':
        facecolor = '#fdf6e3'
    fig = plt.figure(figsize=(10, 12), facecolor = facecolor)
    plt.axis('off')
    plt.barh(values, brightness, align='center', height = 1, color=colorset)
    plt.savefig(path, facecolor=fig.get_facecolor(), dpi = 500, bbox_inches='tight', pad_inches = 0)
    plt.close()
                                                        
# calculating mean color   
def mean_color(image):
    return np.median(np.median(image, axis=1), axis=0)

# generating smooth lines
def gen_smooth_lines(video_path, width=1, height=1, pix_per_line=1):
    
    video_object = cv2.VideoCapture(video_path)
    fps = video_object.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_object.get(cv2.CAP_PROP_FRAME_COUNT))
    if width == 1 & height == 1:
        width = int(frame_count / fps)
        interval = int(fps)
        height = int(video_object.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
        interval = math.ceil(frame_count / width * pix_per_line)
    
    video_lines = np.zeros((height, width, 3))
    x = 0
    count = 0
    sys.stdout.flush()
    pbar = tqdm(total=width, position=0, leave=True)
    while count < frame_count:
        success, raw_image = video_object.read()
        if success & (count % interval == 0):
            b,g,r = cv2.split(raw_image)
            image = cv2.merge([r,g,b])
            line = cv2.resize(image, dsize=(pix_per_line, height),
                  interpolation=cv2.INTER_CUBIC)
            video_lines[:, x:x+pix_per_line, :] = mean_color(image)
            pbar.update(pix_per_line)
            x += pix_per_line
        else:
            pass
        count += 1
    pbar.close()
    return (video_lines / 255)

# generating interpolated lines
def gen_interpolated_lines(video_path, width=1, height=1, pix_per_line=1):
    video_object = cv2.VideoCapture(video_path)
    fps = video_object.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_object.get(cv2.CAP_PROP_FRAME_COUNT))
    if width == 1 & height == 1:
        width = int(frame_count / fps)
        interval = int(fps)
        height = int(video_object.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
        interval = math.ceil(frame_count / width * pix_per_line)
    
    video_lines = np.zeros((height, width, 3))
    x = 0
    count = 0
    sys.stdout.flush()
    pbar = tqdm(total=width, position=0, leave=True)
    while count < frame_count:
        success, raw_image = video_object.read()
        if success & (count % interval == 0):
            b,g,r = cv2.split(raw_image)
            image = cv2.merge([r,g,b])
            line = cv2.resize(image, dsize=(pix_per_line, height),
                  interpolation=cv2.INTER_CUBIC)
            video_lines[:, x:x+pix_per_line, :] = line
            pbar.update(pix_per_line)
            x += pix_per_line
        else:
            pass
        count += 1
    pbar.close()
    return (video_lines / 255)