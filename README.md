# Movie Lines
#### *Movie timeline in its unique colours*
🔗 https://www.instagram.com/data_picture/

❕ *Current version only works in Yandex DataSphere development environment*


## Overview

**Movie Lines** is a media art project representing  movie timeline in its unique colours on a high-quality poster.

Each image represents an unique fingerprint of the movie generated with the power of big data and computer science. 

It consists of almost 2000 lines where each line stands for a few frames extracted from a movie at regular intervals and aggregated by mean color. 

## Algorithm

1. Any video is just a set of frames. Usually, the movie frame rate is accepted worldwide as 24 fps (frames per second). So, one second of a video file consists of 24 frames or one frame is a picture 1/24 sec long.
For example, The film Amélie is 122 minutes long = 7289 seconds = 174 936 frames

   <img src="https://github.com/g2r4i6e8/movie-lines/blob/main/docs/frame_example.png?raw=true" width="300" />

2. Each frame is an n x m matrix, where n is the frame height, m is the frame width. 
Each cell of the matrix contains a color value in RGB format.
So, one HD image is a matrix of 1080 by 1920 or 2 073 600 color cells.
    >[[[16, 77, 58],
    >[19, 80, 61],
    >[12, 73, 54]
    >…
    >[ 0, 36, 40],
    >[ 0, 29, 31],
    >[ 0, 27, 29]]]

3. For the poster, we take one frame every second and compress it into a frame-height, one-pixel-wide stripe. In this case, the colors are interpolated into the horizontal average.

   <img src="https://github.com/g2r4i6e8/movie-lines/blob/main/docs/compression_example.gif?raw=true" width="300" />

4. All stripes are then united to the bar where the width is represented by the total number of seconds of the movie. The bar height is the height of the frame.

   <img src="https://github.com/g2r4i6e8/movie-lines/blob/main/docs/frames_generation.gif?raw=true" height="100" width="700" />

5. Next, the bar is "wrapped" into a circle.

   <img src="https://github.com/g2r4i6e8/movie-lines/blob/main/docs/donut.png?raw=true" width="300" />
   
6. At the final stage, the attributes of the film are added: title, slogan, year, director, duration and rating (IMDB or Kinopoisk).

   <img src="https://github.com/g2r4i6e8/movie-lines/blob/main/docs/Amelie_341_interpolatedDonut_rendered_interdonut_a3.jpg?raw=true" width="300" />

7. Voilà! The poster is ready! ✨ 
