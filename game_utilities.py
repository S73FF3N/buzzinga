# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 19:54:59 2015

@author: List
"""
import os, pygame
from PIL import Image
import subprocess
import functools
from static import Static


def text_objects(text, font, color=Static.WHITE):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    return text_surface, text_rect

def optimize_text_in_container(screen, container, text, min_font_size=10, max_font_size=70, color=Static.WHITE):
    def can_fit_text(font, text, max_width, max_height):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if not current_line:  # If a single word is too long
                    return False
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        total_height = len(lines) * font.get_linesize()
        return total_height <= max_height

    optimal_font_size = min_font_size
    optimal_font = None
    
    while min_font_size <= max_font_size:
        current_font_size = (min_font_size + max_font_size) // 2
        font = pygame.font.Font(None, current_font_size)
        
        if can_fit_text(font, text, container.w - 16, container.h - 16):
            optimal_font_size = current_font_size
            optimal_font = font
            min_font_size = current_font_size + 1
        else:
            max_font_size = current_font_size - 1
    
    if optimal_font is None:
        optimal_font = pygame.font.Font(None, min_font_size)
    
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width, _ = optimal_font.size(test_line)
        
        if test_width <= container.w - 16:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    if len(lines) > 1:
        y_offset = optimal_font.get_linesize() * (-1) * ((len(lines)/2)-0.5)
    else:
        y_offset = 0
    
    for line in lines:
        blit_text_objects(screen, pygame.Rect(container.x, container.y + y_offset,
                                              container.w, container.h),
                          line, optimal_font, color)
        y_offset += optimal_font.get_linesize()

def blit_text_objects(screen, container, text, font, color=Static.WHITE):
    text_surface, text_rect = text_objects(text, font, color)
    text_rect.center = container.center
    screen.blit(text_surface, text_rect)

# Cache decorator to store loaded images
@functools.lru_cache(maxsize=128)  # Caches up to 128 unique images
def load_image(name, folder, colorkey=None):
    fullname = os.path.join(folder, name)
    
    try:
        image = pygame.image.load(fullname)
    except pygame.error as e:
        raise FileNotFoundError(f"Cannot load image: {fullname}") from e
    
    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))  # Use pixel at (0, 0) as colorkey
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    
    return image

def load_and_scale_image(image_name, folder, target_height, image_cache):
    if image_name not in image_cache:
        image_file = load_image(image_name, folder)
        rela = image_file.get_width() / float(image_file.get_height())
        image_cache[image_name] = pygame.transform.scale(image_file, (int(target_height * rela), int(target_height)))
    return image_cache[image_name]

def adjust_image_size(img, container_width, container_height):
    original_width, original_height = img.get_rect().size
    aspect_ratio = original_width / original_height
    if aspect_ratio >= 1:  # Landscape or square image
        new_height = int(container_width / aspect_ratio)
        if new_height <= container_height:
            return (container_width, new_height)
        else:
            new_width = int(container_height * aspect_ratio)
            return (new_width, container_height)
    else:  # Portrait image
        new_width = int(container_height * aspect_ratio)
        if new_width <= container_width:
            return (new_width, container_height)
        else:
            new_height = int(container_width / aspect_ratio)
            return (container_width, new_height)

# convert image to desired image format    
def convert_image_to(image_file, im_format):
    if image_file[-4:] == "."+im_format:
        file_out = image_file
    else:
        print("converting image file...")
        try:
            img = Image.open(image_file)
        except:
            print("Could not open {}".format(img))
            return
        file_out = str(image_file[0:-4])+"."+im_format
        if len(img.split()) == 4:
            # prevent IOError: cannot write mode RGBA as BMP
            r, g, b, a = img.split()
            img = Image.merge("RGB", (r, g, b))
        img.save(file_out)
        os.remove(image_file)
    return file_out

def reverse_mp3(mp3_file):
    print(mp3_file)
    reverse = subprocess.Popen('sox -v 0.98 '+mp3_file+' '+mp3_file[:-3]+'wav reverse', shell=True)
    subprocess.Popen.wait(reverse)
    os.remove(mp3_file)
    
def mp3_to_wav(mp3_file):
    if mp3_file[-3:] == "wav":
        file_out = mp3_file
    else:
        conversion = subprocess.Popen('sudo lame --decode ' + mp3_file + ' ' + mp3_file[:-3] + 'wav', shell=True)
        subprocess.Popen.wait(conversion)
        os.remove(mp3_file)
        file_out = mp3_file[:-3] + 'wav'
    return file_out

def count_files_by_extensions(directory, *extensions):
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(extensions):
            count += 1
    return count