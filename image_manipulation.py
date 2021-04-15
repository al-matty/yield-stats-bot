#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image Manipulation Module for StatsBot
"""
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from math import floor
import data_aggregation as da



# Define colors as global variables
WHITE = (255, 255, 255)
GOLD = (237, 187, 130)
DARK = (32, 31, 25)
GREY = (200, 200, 200)


# Helper functions

# Pretty-parse float to str
def parse_str(float_, roundTo=1):
    '''
    Parses float to str.
    Conditionally appends nothing, 'k', 'm' or 'b'
    '''
    def round_or_not(float_, roundTo=roundTo):
        if roundTo:
            return round(float_, roundTo)
        else:
            return float_

    if float_ >= 1000000000:
        return str(round_or_not(float_/1000000000)) + 'bn'
    if float_ >= 1000000:
        return str(round(float_/1000000)) + 'm'
    else:
        return str(round(float_))

# Draw str on image at certain position. Needed by update_loan_stats()
def draw_str(s, img, pos, fontsize=20, color=(255, 255, 255), font='GothamBook.ttf'):
    """Draws a string on an image"""
    d1 = ImageDraw.Draw(img)
    myFont = ImageFont.truetype(font, size=fontsize)
    d1.text(pos, s, font=myFont, fill=color)

# Update loans.png with current values and save file
def update_loan_stats():
    """Saves loans.png with current information from the blockchain"""
    global WHITE, GOLD, DARK, GREY

    outfile = 'loans.png'
    img = Image.open('loans_template.png')

    # Define metrics and positions
    loans_total = len(da.get_all_loans())
    loans_active = len(da.get_active_loans())
    loans_defaulted = len(da.get_defaulted_loans())
#    loans_total, loans_active, loans_defaulted = (30, 15, 1)
# TODO: Uncomment again for real data


    # Draw loan metrics on template

    # Set font parameters
    color = DARK
    size = 32
    lcolor = GREY
    lsize = 24

    def l1_pos(pos):
        return (pos[0]+120, pos[1]+5)
    def l2_pos(pos):
        return (pos[0]+120, pos[1]+40)
    def long_pos(pos):
        return (pos[0]+100, pos[1]+40)

    # Loans taken
    s = parse_str(loans_total).center(5)
    pos = (75, 200)
    draw_str(s, img, pos, fontsize=size, color=color)
    label1 = 'LOANS'.center(7)
    label2 = 'TAKEN'.center(7)
    draw_str(label1, img, l1_pos(pos), fontsize=lsize, color=lcolor)
    draw_str(label2, img, l2_pos(pos), fontsize=lsize, color=lcolor)

    # Active loans
    s = parse_str(loans_active).center(5)
    pos = (75, 336)
    draw_str(s, img, pos, fontsize=size, color=color)
    label1 = 'ACTIVE'.center(7)
    label2 = 'LOANS'.center(7)
    draw_str(label1, img, l1_pos(pos), fontsize=lsize, color=lcolor)
    draw_str(label2, img, l2_pos(pos), fontsize=lsize, color=lcolor)

    # Defaulted fraction
    defaulted_frac = (loans_defaulted / loans_total)*100
    stage = parse_str(defaulted_frac) + '%'
    s = stage.center(5)
    pos = (75, 472)
    draw_str(s, img, pos, fontsize=size, color=color)
    label1 = '   %'.center(7)
    label2 = 'DEFAULTED'.center(7)
    draw_str(label1, img, l1_pos(pos), fontsize=lsize, color=lcolor)
    draw_str(label2, img, long_pos(pos), fontsize=lsize, color=lcolor)



    # Get current UTC time
    timeStamp = int(time.time())
    parsedTs = datetime.utcfromtimestamp(timeStamp).strftime('%d %b %Y [%H:%M UTC]')
    drawTime = 'Last updated: ' + str(parsedTs)

    # Draw time on image
    time_pos = (190,135)
    draw_str(drawTime, img, (190, 135), fontsize=20, color=GOLD)

    # Save outfile
    img.save(outfile)

    print('loans.png updated.')
