# -*- coding: utf-8 -*-
"""
Crime Game
"""
import random
import numpy as np
import pygame
import os
import matplotlib as plt
plt.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
from sys import argv
import numpy.core._methods
import numpy.lib.format
import wraptext
import time
import winsound
import datetime
import csv

citymap_img = 0
selector_img = 0
resources_img = 0
damaged_img = 0
healthy_img =0


class Location:
    def __init__(self):
        self.name = "District Null"
        self.crimelevel = 0
        self.harmlevel = 0
        self.healthlevel = 0
        self.x = 0
        self.y = 0
        self.blueplayer = False
        self.immune = False
        self.crises = 0
        self.beastlevel = 0
    def __str__(self):
        return self.name 
    
class GameState:
    def __init__(self):
        self.resources = 0
        self.frame=""
        self.crimelevelhistory =[]
        self.images = {}
        self.scale = 1
        self.mapsize = 6

def createmap(x,y):
    citymap = []
    for a in range (x):
        column = []
        for b in range (y):
            z = Location()
            z.x = a
            z.y = b
            z.name = "District "+str(z.x)+str(z.y)
            column.append(z)
        citymap.append(column)
    return citymap

#Returns a new blank map of the same size as the map it was given
def reset_map(map):
    size = len(map)
    map = createmap(size, size)
    return map


# Function for getting a total of the overall crime level
def total_crimelevel(map):
    total_crimelevel = 0
    for precinct in map:
        for district in precinct:
            total_crimelevel = total_crimelevel + district.crimelevel
    return total_crimelevel

def total_beastlevel(map):
    total_beastlevel = 0
    for precinct in map:
        for district in precinct:
            total_beastlevel = total_beastlevel + district.beastlevel
    return total_beastlevel

# Function for getting a total number of crises that have happened
def total_crises(map):
    total_crises = 0
    for precinct in map:
        for district in precinct:
            total_crises = total_crises + district.crises
    return total_crises

#Function for assigning initial crime
def initial_crimelevel(map, gamestate):
    tilebag = refill_bag(len(map))
    for i in range(3):
        tile = random.choice(tilebag)
        tilebag.remove(tile)
        map[tile[0]][tile[1]].crimelevel = 1
    for i in range(3):
        tile = random.choice(tilebag)
        tilebag.remove(tile)
        map[tile[0]][tile[1]].crimelevel = 2
    for i in range(3):
        tile = random.choice(tilebag)
        tilebag.remove(tile)
        map[tile[0]][tile[1]].crimelevel = 3
    if gamestate.frame == "beast" or gamestate.frame == "crime-beast":
        tilebag = refill_bag(len(map))
        for i in range(3):
            tile = random.choice(tilebag)
            tilebag.remove(tile)
            map[tile[0]][tile[1]].beastlevel = 3
            map[tile[0]][tile[1]].crimelevel = 3


# Function for adding crime at the end of each turn, take the map and how much crime to add
#
def add_crimelevel(map, tilebag, crimerate):
    for i in range(crimerate):
        tile = random.choice(tilebag)
        tilebag.remove(tile)
        if map[tile[0]][tile[1]].healthlevel == 0:
#            print ("Crime increased from "+str(map[tile[0]][tile[1]].crimelevel)+" to "+ str(map[tile[0]][tile[1]].crimelevel+1)+" in: "+ (map[tile[0]][tile[1]].name))
            map[tile[0]][tile[1]].crimelevel += 1
        else:
#            print ("Community health prevented crime increase in: "+ (map[tile[0]][tile[1]].name))
            map[tile[0]][tile[1]].healthlevel -= 1
            
        

# Returns a list of all the crisis districts and sets them to immune
def crisis_check(map):
    crisis_list = []
    for precinct in map:
        for district in precinct:
            if district.crimelevel>3:
                district.crimelevel = 3
                district.crises += 1
                district.immune = True
                crisis_list.append([district.x,district.y])
                print("Crisis in "+district.name)
    return crisis_list

#Takes the the map and crisis list and increases crime in valid districts (not outside of the map, not immume)
def crisis_pop(map, crisis_list):
    boundary = len(map)-1
    target_districts = []
    for item in crisis_list:
        target_districts = neighbors(item,boundary)
        for target in target_districts:
            if map[target[0]][target[1]].immune == False:
                map[target[0]][target[1]].crimelevel = map[target[0]][target[1]].crimelevel +1

#Returns a list of the points adjacent to a given point, that are part of the map         
def neighbors(point, mapsize):
    neighbor_list =[]
    neighbor_list.append((point[0]+1, point[1]))
    neighbor_list.append((point[0]-1, point[1]))
    neighbor_list.append((point[0], point[1]+1))
    neighbor_list.append((point[0], point[1]-1))
    removal_list =[]
    for point in neighbor_list:
        if point[0]<0:
            removal_list.append(point)
        elif point[0]>mapsize:
            removal_list.append(point)
        elif point[1]<0:
            removal_list.append(point)
        elif point[1]>mapsize:
            removal_list.append(point)
    for point in removal_list:
        neighbor_list.remove(point)
    return neighbor_list


def all_neighbors(point, mapsize):
    neighbor_list =[]
    neighbor_list.append((point[0]+1, point[1]))
    neighbor_list.append((point[0]-1, point[1]))
    neighbor_list.append((point[0], point[1]+1))
    neighbor_list.append((point[0], point[1]-1))
    neighbor_list.append((point[0]+1, point[1]+1))
    neighbor_list.append((point[0]-1, point[1]-1))
    neighbor_list.append((point[0]+1, point[1]-1))
    neighbor_list.append((point[0]-1, point[1]+1))
    removal_list =[]
    for point in neighbor_list:
        if point[0]<0:
            removal_list.append(point)
        elif point[0]>mapsize:
            removal_list.append(point)
        elif point[1]<0:
            removal_list.append(point)
        elif point[1]>mapsize:
            removal_list.append(point)
    for point in removal_list:
        neighbor_list.remove(point)
    return neighbor_list

#Find player
def find_blue(map):
    for x in range(len(map)):
        for y in range (len(map)):
            if map[x][y].blueplayer == True:
                location =(x,y)
    return location

# Blue player movement function
def move_blueplayer(map,direction, gamestate):
    sounds = gamestate.sounds
    current_location = find_blue(map)
    valid_targets = neighbors(current_location, len(map)-1)
    if direction == "up":
        target_location = (current_location[0], current_location[1]+1) 
    if direction == "down":
        target_location = (current_location[0], current_location[1]-1)
    if direction == "left":
        target_location = (current_location[0]-1, current_location[1])
    if direction == "right":
        target_location = (current_location[0]+1, current_location[1])
    
    if (target_location in valid_targets) == True:
        map[current_location[0]][current_location[1]].blueplayer = False
        map[target_location[0]][target_location[1]].blueplayer = True
        playsound("beep", gamestate)
    else:
        playsound("buzz", gamestate)
     
  


        

def center_image(X,Y,image):
    fix_x, fix_y = image.get_size()[0]/2, image.get_size()[0]/2
    return X-fix_x, Y-fix_y

# Turn ending function                
def end_turn(screen, map, gamestate):
    gamestate.map = map
    update_log(gamestate,"End Turn")
    newcrises = 0
    if gamestate.frame == "virus" or gamestate.frame == "crime-virus":     
        tilebag = refill_bag(len(map))
        crimerate = len(map)-4
        crimerate = 3
        add_crimelevel(map, tilebag, crimerate)
        crisis_list = ["blah"]
        while len(crisis_list)>0:
            crisis_list = crisis_check(map)
            newcrises += len(crisis_list)
            if total_crimelevel(map)< (3*len(map)**2): 
                crisis_pop(map, crisis_list)
            clear_immunity(map)
        for row in reversed(range(len(map))):
            for column in range(len(map[0])):
                if map[column][row].harmlevel > 0  and map[column][row].crimelevel < 3:
                    if random.randint(0,100) < map[column][row].harmlevel*5:
                        map[column][row].crimelevel = map[column][row].crimelevel+1
        
    elif gamestate.frame == "beast" or gamestate.frame == "crime-beast":
        for row in reversed(range(len(map))):
            for column in range(len(map[0])):
                map[column][row].justarrived = False
        boundary = len(map)-1
        for row in reversed(range(len(map))):
            for column in range(len(map[0])):
                if map[column][row].beastlevel > 0  and map[column][row].crimelevel == 3:
                    target_districts = []
                    target_districts = neighbors((column,row),boundary)
                    for target in target_districts:
                        if map[target[0]][target[1]].crimelevel < 4:
                            map[target[0]][target[1]].crimelevel = map[target[0]][target[1]].crimelevel +1
                if map[column][row].beastlevel > 0  and map[column][row].crimelevel<4:
                    map[column][row].crimelevel+=1
                if map[column][row].beastlevel > 0 and map[column][row].justarrived == False:
                    target_districts = []
                    target_districts = neighbors((column,row),boundary)
                    for district in target_districts:
                        if map[district[0]][district[1]].beastlevel > 0:
                            target_districts.remove(district)
                    target_districts.append((column,row))
                    beast_onthemove = map[column][row].beastlevel
                    map[column][row].beastlevel = 0
                    target = random.choice(target_districts)
                    
                    if gamestate.animate != False:
                        animate_beastmove(screen, map, gamestate, beast_onthemove,map[column][row], map[target[0]][target[1]])
                        

                    map[target[0]][target[1]].beastlevel = beast_onthemove
                    map[target[0]][target[1]].justarrived = True
                    pygame.display.update()
                    

    update_crimegraph(screen, map, gamestate)
    pygame.display.update()

        
    return newcrises

def start_turn(screen, map, gamestate):
    playsound("cash", gamestate)
    gamestate.resources = 4
    gamestate.map = map
    update_log(gamestate,"Start Turn")
    pygame.display.update()
    return

    

def animate_beastmove(screen, map, gamestate, beastlevel, src, dst):
    if src != dst:
        if gamestate.frame == "beast":
            playsound("howl", gamestate)
        if gamestate.frame == "crime-beast":
            playsound("hehe", gamestate)
        SIZE = len(map)
        
        scale = gamestate.scale
        WIDTH = int(100 *scale)
        HEIGHT = int(100 *scale)
        MARGIN = int(5 * scale)
        BOTTOM = HEIGHT * SIZE 
        LEFTOFFSET = int(102 *scale)
        images = gamestate.images
        if gamestate.frame == "beast":
            if beastlevel == 1:
                icon = images["beast_wound2"]
            if beastlevel == 2:
                icon = images["beast_wound1"]
            if beastlevel == 3:
                icon = images["beast_wound0"]
        else:
            if beastlevel == 1:
                icon = images["crook_fear2"]
            if beastlevel == 2:
                icon = images["crook_fear1"]
            if beastlevel == 3:
                icon = images["crook_fear0"]
            
        X_src = LEFTOFFSET +(MARGIN + WIDTH) * src.x + MARGIN
        Y_src = BOTTOM - ((MARGIN + HEIGHT) * src.y)  + MARGIN
        X_dst = LEFTOFFSET +(MARGIN + WIDTH) * dst.x + MARGIN
        Y_dst = BOTTOM - ((MARGIN + HEIGHT) * dst.y)  + MARGIN
                
        for i in reversed(range (10)):
            X_step, Y_step = (X_dst-X_src)/(i+1), (Y_dst-Y_src)/(i+1)
            cur_x, cur_y = X_src+X_step, Y_src+Y_step
            draw_map(screen, map, gamestate)
            pygame.display.update()
            screen.blit(icon, [cur_x, cur_y])
            pygame.display.update()
        
        
        
    return
    

# Removes immunity from the map
def clear_immunity(map):
    for precinct in map:
        for district in precinct:
            district.immune = False
          
# Refresh the tilebag
def refill_bag(size):
    bag=[]
    for x in range(size):
        for y in range(size):
            tile = (x,y)
            bag.append(tile)
    return bag

def load_images(gamestate):
    gamestate.images = {}
    scale = gamestate.scale
    for afile in os.listdir(os.path.join("images\\")):
        if afile[-4:] == ".png" or afile[-4:] == ".PNG":
            gamestate.images[afile[:-4]] = pygame.image.load(os.path.join("images\\",afile))
    for key in gamestate.images.keys():
        if key == "citymap":
            x = 630
            y=630
        elif key[-5:] == "small" or key == "selector":
            x = 33
            y= 33
        elif key[-3:] == "big":
            x=107
            y=107
        elif key[:5] == "crook" or key[:5] == "beast":
            x=66
            y=66
        else:
            x = 66
            y = 66
           
        gamestate.images[key] = pygame.transform.scale(gamestate.images[key],(int(x*scale),int(y*scale)))
    return

def load_sounds(gamestate):
    gamestate.sounds = {}
    scale = gamestate.scale
    for afile in os.listdir(os.path.join("sounds\\")):
        if afile[-4:] == ".wav" or afile[-4:] == ".WAV":
            gamestate.sounds[afile[:-4]] = (os.path.join("sounds\\",afile))          
#            gamestate.sounds[afile[:-4]] = pygame.mixer.Sound(os.path.join("sounds\\",afile))
    return
    
def playsound(key, gamestate):
    if gamestate.playsounds == True:
#        gamestate.sounds[key].play()        
        soundpath = gamestate.sounds[key]
        winsound.PlaySound(soundpath, winsound.SND_FILENAME | winsound.SND_ASYNC)

# This is the main drawing function, that puts everything on the screen.
def draw_map(screen, map, gamestate):
    images = gamestate.images
    scale = gamestate.scale
    s = pygame.Surface((int(100*scale),int(100*scale)))  # this is a rectangle for indicating crime/harm level in a district
    s.fill((255, 0, 0))           # this fills the entire surface with red
    
    myfont = pygame.font.Font("freesansbold.ttf",26)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (20, 20, 200)
    DIMGRAY = (105,105,105)
    YELLOW = (255,255,0)
    screen.fill(BLACK)
    SIZE = len(map)
    WIDTH = int(100 *scale)
    HEIGHT = int(100 *scale)
    MARGIN = int(5 * scale)
    BOTTOM = HEIGHT * SIZE 
    LEFTOFFSET = int(102 *scale)
    action_label = myfont.render("Round: "+str(gamestate.current_round)+" Resources:", 1,(255,255,255))
    if gamestate.current_round == gamestate.max_rounds:
            action_label = myfont.render("Round: "+str(gamestate.current_round)+" Resources:", 1,(255,255,255))
    if gamestate.stop_play == True:
        action_label = myfont.render("Game Over", 1,(255,255,255))
    action_label = pygame.transform.scale(action_label,(int(action_label.get_width()*scale),int(action_label.get_height()*scale)))
    screen.blit(action_label, (int(30*scale),int(30*scale)))
    for i in range(gamestate.resources):
        screen.blit(images["resources"],(int(30+action_label.get_width()+int(i*images["resources"].get_width())), int(5*scale)))
    screen.blit(images["citymap"],(int(105*scale),int(77*scale)))
    
    for row in reversed(range(len(map))):
        for column in range(len(map[0])):
            X = LEFTOFFSET +(MARGIN + WIDTH) * column + MARGIN
            Y = BOTTOM - ((MARGIN + HEIGHT) * row)  + MARGIN
            CenterX = X + WIDTH/2
            CenterY = Y + HEIGHT/2
            if map[column][row].blueplayer == True: 
                color = YELLOW
            else:
                color = BLACK
    
            pygame.draw.rect(screen,color, (X,Y,WIDTH,HEIGHT),MARGIN)
            if map[column][row].crimelevel > 0:
                color = RED
                crime_label = myfont.render(str(map[column][row].crimelevel), 1, WHITE)
                s.set_alpha(map[column][row].crimelevel*42)                # alpha level
                screen.blit(s,[X,Y,WIDTH,HEIGHT] )
                
            if map[column][row].harmlevel != 0:
                if map[column][row].harmlevel == 1: 
                    icon = images["damaged_small"]
                elif map[column][row].harmlevel == 2:
                    icon = images["damaged"]
                elif map[column][row].harmlevel == 3:
                    icon = images["damaged_big"]
                elif map[column][row].harmlevel == -1:
                    icon = images["healthy_small"]
                elif map[column][row].harmlevel == -2:
                    icon = images["healthy"]
                elif map[column][row].harmlevel == -3:
                    icon = images["healthy_big"]
                iconX, iconY = center_image(CenterX,CenterY,icon)
                screen.blit(icon,[iconX,iconY])
                    
            if map[column][row].beastlevel != 0:
                if gamestate.frame == "beast" and map[column][row].beastlevel == 1:
                    icon = images["beast_wound2"]
                if gamestate.frame == "beast" and map[column][row].beastlevel == 2:
                    icon = images["beast_wound1"]
                if gamestate.frame == "beast" and map[column][row].beastlevel == 3:
                    icon = images["beast_wound0"]
                if gamestate.frame == "crime-beast" and map[column][row].beastlevel == 1:
                    icon = images["crook_fear2"]
                if gamestate.frame == "crime-beast" and map[column][row].beastlevel == 2:
                    icon = images["crook_fear1"]
                if gamestate.frame == "crime-beast" and map[column][row].beastlevel == 3:
                    icon = images["crook_fear0"]
                
                iconX, iconY = center_image(CenterX,CenterY,icon)
                screen.blit(icon,[iconX,iconY])

#           
    crimegraph = pygame.transform.scale(gamestate.crimegraph,(int(gamestate.crimegraph.get_width()*scale),int(gamestate.crimegraph.get_height()*scale)))
    screen.blit(crimegraph, (int(800*scale),int(60*scale)))
    
    instructions_action_label = myfont.render("Use the Arrow Keys to Select a District", 1,(WHITE))
    all_actions_label = myfont.render("Use the number keys to choose an action:", 1,(WHITE))
    instructions_action_label = pygame.transform.scale(instructions_action_label,(int(instructions_action_label.get_width()*scale),int(instructions_action_label.get_height()*scale)))
    all_actions_label = pygame.transform.scale(all_actions_label,(int(all_actions_label.get_width()*scale),int(all_actions_label.get_height()*scale)))

    if gamestate.frame == "virus":
        enforce_action_label = myfont.render("1. Restrict Travel (Cost 1)            3. Implement Quarrantine (Cost 2)", 1,(WHITE))
    elif gamestate.frame == "crime-virus":
        enforce_action_label = myfont.render("1. Conduct Raids (Cost 1)                   3. Increase Patrols (Cost 2)", 1,(WHITE))
    elif gamestate.frame == "beast":
        enforce_action_label = myfont.render("1. Set Traps (Cost 1)                        3. Send Dog Team (Cost 2)", 1,(WHITE))
    elif gamestate.frame == "crime-beast":
        enforce_action_label = myfont.render("1. Conduct Raids (Cost 1)                  3. Increase Patrols (Cost 2)", 1,(WHITE))
        
    enforce_action_label = pygame.transform.scale(enforce_action_label,(int(enforce_action_label.get_width()*scale),int(enforce_action_label.get_height()*scale)))
    
    if gamestate.frame == "virus":
        prevent_action_label = myfont.render("2. Health Education (Cost 1)      4. Vaccination Clinic (Cost 2)", 1,(WHITE))
    elif gamestate.frame == "crime-virus":
        prevent_action_label = myfont.render("2. Neighborhood Watch (Cost 1)       4. After School Program (Cost 2)", 1,(WHITE))
    elif gamestate.frame == "beast":
        prevent_action_label = myfont.render("2. Post Warning Flyers (Cost 1)    4. Broadcast Safety Warnings (Cost 2)", 1,(WHITE))
    elif gamestate.frame == "crime-beast":
        prevent_action_label = myfont.render("2. Neighborhood Watch (Cost 1)      4. After School Program (Cost 2)", 1,(WHITE))

    prevent_action_label = pygame.transform.scale(prevent_action_label,(int(prevent_action_label.get_width()*scale),int(prevent_action_label.get_height()*scale)))
    
    
    frame_label = myfont.render("Frame: "+gamestate.frame, 1,(BLUE))    
    frame_label = pygame.transform.scale(frame_label,(int(frame_label.get_width()*scale),int(frame_label.get_height()*scale)))

    screen.blit(instructions_action_label, (int(175*scale),int(710*scale)))
    screen.blit(all_actions_label, (int(50*scale),int(775*scale)))
    screen.blit(enforce_action_label, (int(50*scale),int(810*scale)))
    if gamestate.debug == True:
        screen.blit(frame_label, (int(50*scale),int(865*scale)))

    screen.blit(prevent_action_label, (int(50*scale),int(835*scale)))
    
    key_s = pygame.Surface((int(500*scale),int(100*scale)))  # this is a rectangle for indicating crime/harm level in a district
    key_s.fill((169,169,169))           # this fills the entire surface with red
    screen.blit(key_s,[int(1060*scale),int(770*scale)])
    key_label = myfont.render("KEY", 1,(BLACK))
    if gamestate.frame == "beast":
        key_label2 = myfont.render("        BEAST      WOUNDED", 1,(BLACK))
        icon1 = images["beast_wound0"]
        icon2 = images["beast_wound2"]
    elif gamestate.frame == "crime-beast":
        key_label2 = myfont.render("        CROOK         AFRAID", 1,(BLACK))
        icon1 = images["crook_fear0"]
        icon2 = images["crook_fear2"]
    else:
        key_label2 = myfont.render("        SAFE           UNSAFE", 1,(BLACK))
        icon1 = images["healthy"]
        icon2 = images["damaged"]
        
    screen.blit(key_label, (int(1060*scale),int(800*scale)))
    screen.blit(key_label2, (int(1120*scale),int(770*scale)))
    screen.blit(icon1,[int(1210*scale),int(800*scale)])
    screen.blit(icon2,[int(1440*scale),int(800*scale)])
 
    
def update_crimegraph(screen, map, gamestate, update=True):
    plt.pyplot.close('all')
    if update == True:
        gamestate.crimelevelhistory.append(total_crimelevel(map))
    fig = pylab.figure(figsize=[8, 7], # Inches
                   dpi=100,        # 100 dots per inch, so the resulting buffer is 400x400 pixels
                   )
##    fig.ylabel('some numbers')
    if gamestate.frame == "crime-beast" or gamestate.frame == "crime-virus":
        ax = fig.gca(title = "Total Crime Level",xlabel="Day", ylim=(0,60), ylabel = "Crime", xlim =(0,41))
    if gamestate.frame == "beast":
        ax = fig.gca(title = "Total Mayhem Level",xlabel="Day", ylim=(0,60), ylabel = "Mayhem", xlim =(0,41))
    if gamestate.frame == "virus":
        ax = fig.gca(title = "Total Virus Level",xlabel="Day", ylim=(0,60), ylabel = "Virus", xlim =(0,41))
        
    ax.plot(gamestate.crimelevelhistory,linewidth=7.0, color='red')
    if gamestate.frame == "crime-beast" or gamestate.frame == "crime-virus":
        ax.set_title('Total Crime Level',color='yellow', fontdict={'fontsize':24})
        ax.set_xlabel('Time',color='yellow', fontdict={'fontsize':24})
        ax.set_ylabel('Crime',color='yellow', fontdict={'fontsize':24})
    if gamestate.frame == "beast":
        ax.set_title('Total Mayhem Level',color='yellow', fontdict={'fontsize':24})
        ax.set_xlabel('Day',color='yellow', fontdict={'fontsize':24})
        ax.set_ylabel('Mayhem',color='yellow', fontdict={'fontsize':24})
    if gamestate.frame == "virus":
        ax.set_title('Total Virus Level',color='yellow', fontdict={'fontsize':24})
        ax.set_xlabel('Day',color='yellow', fontdict={'fontsize':24})
        ax.set_ylabel('Virus',color='yellow', fontdict={'fontsize':24})
         
    ax.set_fc('black')
    ax.axhline(y=15, xmin=0, xmax=1, color="red")
    
    ax.spines['bottom'].set_color('yellow')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('yellow')
    ax.spines['right'].set_color('yellow')
    ax.grid(color='gray',linestyle='-', linewidth=2)
    
    ax.tick_params(axis='x', colors='yellow', labelsize=16)
    ax.tick_params(axis='y', colors='yellow', labelsize=16)
    ax.xaxis.label.set_color('yellow')
    ax.tick_params(axis='x', colors='yellow')

    plt.pyplot.gcf().set_facecolor('black')

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    gamestate.crimegraph = pygame.image.fromstring(raw_data, size, "RGB")
    
    
def alert(screen,message):
    message = message + "\n\n Press Enter to Continue"
    # Writing an alert message
    myfont = pygame.font.Font("freesansbold.ttf", 24)
    label1 = myfont.render(message, 1, (0,255,255))
    label2 = myfont.render("Press Enter to Continue", 1, (0,255,255))
    my_rect = pygame.Rect(((screen.get_width() / 4), (screen.get_height() / 4), 600,300))
    rendered_text = wraptext.render_textrect(message, myfont, my_rect, (216, 216, 216), (48, 48, 48), 0)
    screen.blit(rendered_text, my_rect.topleft)
    pygame.display.flip()
    # And waiting for acknowledgment
    acknowledged = False
    pygame.event.clear()
    while (acknowledged == False):
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            key = ev.dict['key']
            if key == pygame.K_F12:
                acknowledged = True
            if key == pygame.K_RETURN:
                acknowledged = True
    return 

def end_alert(screen,message):
    # Writing an alert message
    myfont = pygame.font.Font("freesansbold.ttf", 24)
    label1 = myfont.render(message, 1, (0,255,255))
    my_rect = pygame.Rect(((screen.get_width() / 4), (screen.get_height() / 4), 600,300))
    rendered_text = wraptext.render_textrect(message, myfont, my_rect, (216, 216, 216), (48, 48, 48), 0)
    screen.blit(rendered_text, my_rect.topleft)
    pygame.display.flip()
    # And waiting for acknowledgment
    acknowledged = False
    pygame.event.clear()
    while (acknowledged == False):
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            key = ev.dict['key']
            if key == pygame.K_F12:
                acknowledged = True
    return 

def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  out = ""
  display_box(screen, question + ": " + out.join(current_string))
  while 1:
    inkey = get_key()
    if inkey == pygame.K_BACKSPACE:
        if len(current_string)>0:
            current_string = current_string[0:-1]
        else:
            pass
    elif inkey == pygame.K_RETURN:
        break
    elif inkey == pygame.K_MINUS:
        current_string.append("_")
    elif RepresentsInt(chr(inkey)[-1:]) == True:
        current_string.append(chr(inkey).upper())
    display_box(screen, question + ": " + out.join(current_string))
  return out.join(current_string)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def display_box(screen, message):
  "Print a message in a box in the middle of the screen"
  screen.fill((0,0,0))
  pygame.display.flip()
  fontobject = pygame.font.Font("freesansbold.ttf",24)
#  pygame.draw.rect(screen, (0,0,0),
#                   ((screen.get_width() / 2) - 100,
#                    ((screen.get_height() / 3)*2) - 10,
#                    200,24), 0)
#  pygame.draw.rect(screen, (255,255,255),
#                   ((screen.get_width() / 2) - 102,
#                    ((screen.get_height() / 3)*2) - 12,
#                    204,28), 1)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 200, ((screen.get_height() / 3)*2) - 100))
  pygame.display.flip()
  
def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
      return event.key
    else:
      pass
  
def update_log(gamestate,action=""):
    moment = time.time() - gamestate.starttime
    crimelevel = total_crimelevel(gamestate.map)
    beastlevel = total_beastlevel(gamestate.map)
    data = [gamestate.id, gamestate.frame,gamestate.current_round,gamestate.resources,action,moment,crimelevel,beastlevel]
    gamestate.log.append(data)

def gameloop (gamestate, screen):
    
    map = createmap(gamestate.mapsize, gamestate.mapsize)
    initial_crimelevel(map, gamestate)
    gamestate.crimelevelhistory =[]
    update_crimegraph(screen, map, gamestate)

    freemove = True
    gamestate.current_round = 1
    gamestate.resources = 4
    gamestate.stop_play = False
    map[3][3].blueplayer = True
    
    if gamestate.frame == "virus":
        introtext = "A viral pandemic is spreading through the city of Addison. The city manager has chosen you to help manage this problem.  Select neighborhoods and choose how to spend resources. Try to keep the total virus below the red line."
    elif gamestate.frame == "crime-virus" or gamestate.frame == "crime-beast":
        introtext = "Violent crime is now ravaging the city of Addison. The city manager has chosen you to help manage this problem. Select neighborhoods and choose how to spend resources. Try to keep the total crime below the red line."
    elif gamestate.frame == "beast":
        introtext = "Wild beasts are causing mayhem in the city of Addison. The city manager has chosen you to help manage this problem. Select neighborhoods and choose how to spend resources. Try to keep the total mayhem below the red line."

    alert(screen, introtext)
    game_over = False
    while game_over == False:
        gamestate.map = map
        
        for event in pygame.event.get():
            starttime=time.time()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    end_turn(screen, map, gamestate)
                if event.key == pygame.K_UP:
                    move_blueplayer(map,"up", gamestate)
                if event.key == pygame.K_DOWN:
                    move_blueplayer(map,"down", gamestate)
                if event.key == pygame.K_LEFT:
                    move_blueplayer(map,"left", gamestate)
                if event.key == pygame.K_RIGHT:
                    move_blueplayer(map,"right", gamestate)
                            
                if event.key == pygame.K_1:
                    update_log(gamestate,"K1")
                    if gamestate.stop_play == False  and gamestate.resources>0:
                        location = find_blue(map)
                        if gamestate.frame == "virus" or gamestate.frame == "crime-virus":
                            if map[location[0]][location[1]].crimelevel == 0:
                                if gamestate.frame=="virus":
                                    alert(screen,"No virus here.")
                                elif gamestate.frame=="crime-virus":
                                    alert(screen,"No crime here.")
                            else:
                                if map[location[0]][location[1]].harmlevel < 3:
                                    map[location[0]][location[1]].harmlevel +=1
                                if map[location[0]][location[1]].crimelevel > 0:
                                    map[location[0]][location[1]].crimelevel = 0
                                    boundary = len(map)-1
                                    target_districts = []
                                    target_districts = all_neighbors(location,boundary)
                                    for target in target_districts:
                                        if map[target[0]][target[1]].harmlevel < 3:
                                            map[target[0]][target[1]].harmlevel = map[target[0]][target[1]].harmlevel +1
                                    update_crimegraph(screen, map, gamestate)
                                    gamestate.resources -=1
                        if gamestate.frame == "beast" or gamestate.frame == "crime-beast":
                            if map[location[0]][location[1]].beastlevel == 0:
                                if gamestate.frame=="beast":
                                    alert(screen,"No beast here.")
                                elif gamestate.frame=="crime-virus":
                                    alert(screen,"No crime here.")
                            else:
                                if map[location[0]][location[1]].beastlevel > 0:
                                    map[location[0]][location[1]].beastlevel = 0
                                    boundary = len(map)-1
                                    target_districts = []
                                    target_districts = all_neighbors(location,boundary)
                                    for target in target_districts:
                                        if map[target[0]][target[1]].crimelevel < 3:
                                            map[target[0]][target[1]].crimelevel = map[target[0]][target[1]].crimelevel +1
                                update_crimegraph(screen, map, gamestate)
                                gamestate.resources -=1
                            
                if event.key == pygame.K_2:
                    update_log(gamestate,"K2")
                    if gamestate.stop_play == False and gamestate.resources>0:
                        location = find_blue(map)
                        if gamestate.frame == "virus" or gamestate.frame == "crime-virus":
                            if map[location[0]][location[1]].harmlevel > -3:
                                map[location[0]][location[1]].harmlevel = -3
                                update_crimegraph(screen, map, gamestate)
                                gamestate.resources -=1
                            else:
                                if gamestate.frame == "virus": alert(screen, "This district is already a healthy community.")
                                if gamestate.frame == "virus-crime": alert(screen, "This district is already a supportive community")
                        if gamestate.frame == "beast" or gamestate.frame == "crime-beast":
                            if map[location[0]][location[1]].crimelevel > 0:
                                map[location[0]][location[1]].crimelevel = 0
                                update_crimegraph(screen, map, gamestate)
                                gamestate.resources -=1
                            else:
                                 if gamestate.frame == "beast": alert(screen, "This district is already low mayhem.")
                                 if gamestate.frame == "beast-crime": alert(screen, "This district is already low crime.")
                            
                            
                if event.key == pygame.K_3:
                    update_log(gamestate,"K3")
                    if gamestate.stop_play == False and gamestate.resources>1:
                        location = find_blue(map)
                        boundary = len(map)-1
                        target_districts = []
                        target_districts = all_neighbors(location,boundary)
                        target_districts.append(location)
                        if gamestate.frame == "virus" or gamestate.frame == "crime-virus":
                            for target in target_districts:
                                if map[target[0]][target[1]].crimelevel > 0:
                                    map[target[0]][target[1]].crimelevel = map[target[0]][target[1]].crimelevel -1
                                if map[target[0]][target[1]].harmlevel < 3:
                                    map[target[0]][target[1]].harmlevel = map[target[0]][target[1]].harmlevel +1
                        if gamestate.frame == "beast" or gamestate.frame == "crime-beast":
                            for target in target_districts:
                                if map[target[0]][target[1]].beastlevel > 0:
                                    map[target[0]][target[1]].beastlevel = map[target[0]][target[1]].beastlevel -1
                                if map[target[0]][target[1]].crimelevel < 3:
                                    map[target[0]][target[1]].crimelevel = map[target[0]][target[1]].crimelevel +1
                        update_crimegraph(screen, map, gamestate)
                        update_crimegraph(screen, map, gamestate)
                        gamestate.resources -=2
                    else:
                        alert(screen, "Not enough resources.")
                            
                            
                if event.key == pygame.K_4:
                    update_log(gamestate,"K4")
                    if gamestate.stop_play == False and gamestate.resources>1:
                        location = find_blue(map)
                        boundary = len(map)-1
                        target_districts = []
                        target_districts = all_neighbors(location,boundary)
                        target_districts.append(location)
                        if gamestate.frame == "virus" or gamestate.frame == "crime-virus":
                            for target in target_districts:
                                if map[target[0]][target[1]].harmlevel > -3:
                                    map[target[0]][target[1]].harmlevel = map[target[0]][target[1]].harmlevel -1
                        if gamestate.frame == "beast" or gamestate.frame == "crime-beast":
                            for target in target_districts:
                                if map[target[0]][target[1]].crimelevel > 0:
                                    map[target[0]][target[1]].crimelevel = map[target[0]][target[1]].crimelevel -1
                        update_crimegraph(screen, map, gamestate)
                        update_crimegraph(screen, map, gamestate)
                        gamestate.resources -=2
                    else:
                        alert(screen, "Not enough resources.")
                            
#                if event.key == pygame.K_d:
#                    if gamestate.debug == True:
#                        gamestate.debug = False
#                    elif gamestate.debug == False:
#                        gamestate.debug = True
                            
                if event.key == pygame.K_F12:
                    game_over = True

            if gamestate.resources == 0 and gamestate.current_round < gamestate.max_rounds :
                draw_map(screen, map, gamestate)
                alert(screen,"Next Round")
                draw_map(screen, map, gamestate)
                end_turn(screen, map, gamestate)
                start_turn(screen, map, gamestate)
                gamestate.current_round += 1
            elif gamestate.current_round == gamestate.max_rounds and gamestate.resources==0 and gamestate.stop_play == False:
                draw_map(screen, map, gamestate)
                pygame.display.update()
                alert(screen,"Game Over.")
                gamestate.stop_play = True
            if total_crimelevel(map) == 0 and gamestate.stop_play == False:
                alert(screen,"Game Over - Amazing Job!")
                gamestate.current_round = gamestate.max_rounds 
                gamestate.resources = 0
                gamestate.stop_play = True
                
                   
            draw_map(screen, map, gamestate)
            endtime = time.time()
            pygame.display.update()

#            log.write("event = %s, time = %.9f \n"%(event,starttime-endtime))
    
        pygame.display.update()
    return

def savedata(gamestate):
    
    now = time.time()
    formatted_time = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H-%M-%S')
    filename = str(gamestate.id)+"_"+str(formatted_time)+".csv"
    fullpath = os.path.join("data\\",filename)
    
    outfile = open(fullpath,'w')
#    for line in gamestate.log:
#        fout.write(line)
    outfile.close()    
    
    
    with open(fullpath, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(gamestate.log)
#    

    return

def tutorial_loop(gamestate,screen):
    
    pass

def main():            
    # Setting up the game
    cityname = "Addison"
    fullscreen = True
    gamestate = GameState()
    gamestate.animate = True
    gamestate.playsounds = True
    gamestate.debug = False
    gamestate.mapsize = 6  
    gamestate.max_rounds = 8
    gamestate.scale = .75

    load_sounds(gamestate)
    load_images(gamestate)

    condition = 1
     
    if len(argv)>1:
        gamestate.scale = float(argv[1])
    if len(argv)>2:
        condition = int(argv[2])
  
    pygame.init()
    screen = pygame.display.set_mode((int(1600*gamestate.scale),int(900*gamestate.scale)))
    
    if condition == 1:
        condition = "consistent"
    elif condition == 2:
        condition = "inconsistent"

    pygame.display.set_caption(str(cityname))
    gamestate.clock = pygame.time.Clock()

    gamestate.id = ask(screen, "Enter Participant Number")
    screen.fill((0,0,0))
    pygame.display.flip()

    tutorial_loop(gamestate, screen)    
 
    gamestate.log = [["Participant", "Frame", "Round", "Resources", "Action","Time","CrimeLevel","BeastLevel"]]
    gamestate.frame = "beast"
    gamestate.starttime = time.time()
    gameloop (gamestate, screen)
    screen.fill((0,0,0))
    pygame.display.flip()
    
    
    if condition == "consistent":
        gamestate.frame = "crime-beast"
    else:
        gamestate.frame = "crime-virus"
    
    gameloop (gamestate, screen)
    screen.fill((0,0,0))
    pygame.display.flip()
    savedata(gamestate)
    
    end_alert(screen, "\n Let the RA know you are ready to continue.")
                
    pygame.quit()
    return


main()

