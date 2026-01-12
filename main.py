import requests
import json
import os
import pandas
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk
from ttkbootstrap.constants import *
from fontTools.merge import Merger

# vars
reviewers = ('James', 'Ewan', 'Sam', 'Joe', 'Ollie', 'Steve', 'Will', 'Bert', 'Fin', 'Serafina', 'Adam')

logo_offset_value = 100
average_font_size = 650
individual_scores_title = 575
individual_scores_font_size = 220
individual_scores_border = 130
individual_scores_title_border = 110
logo_file = 'apple badge.png'
font_file = 'C:/Windows/Fonts/Cambria/cambriab.ttf'
review_font_size = 80
desired_line_length = 70
max_line_length = 72
text_box_size = 2600
cover_size = 3000
text_box_border = 50
regular_font = ('cambria.ttf')
bold_font = ('C:/Windows/Fonts/cambriab.ttf')


# main
class DP_Postmaker(ttk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, padding=10, **kwargs)

        self.name_holder = ttk.StringVar(value="Select a name to start!")
        self.first_click = True
        self.album_name = ""
        self.artist_name = ""
        self.text_reviews = [""] * len(reviewers)
        self.score_reviews = [""] * len(reviewers)
        self.uncompressed = ""
        self.rgb_code = (0,0,0)

        self.create_screen()

    def create_screen(self):

        # title
        self.title = ttk.Label(text="DP Post Generator 0.9", font=('TkDefaultFixed', 30), justify='left')
        self.title.pack(side= TOP, pady=0)

        # header separator
        self.header_separator = ttk.Separator(orient=HORIZONTAL)
        self.header_separator.pack(side=TOP, fill=X, pady=5)   

        # album entry and image frame
        self.top_container = ttk.Frame()
        self.top_container.pack(side=TOP, pady=0)

        # image
        img = Image.open(logo_file)
        img = img.resize((200, 200))
        logo = ImageTk.PhotoImage(img)
        self.logo_label = tk.Label(image=logo, master=self.top_container)
        self.logo_label.image = logo
        self.logo_label.pack(side=RIGHT, padx=30)

        # album name input 
        # album name frame
        self.album_text_container = tk.Frame(master=self.top_container)
        self.album_text_container.pack(side=TOP, pady=10, fill=X)
        # album name text
        self.album_text_label = ttk.Label(master=self.album_text_container, justify=LEFT, text="Album:")
        self.album_text_label.pack(side=LEFT, padx=5)
        # album name entry
        self.album_name_entry = ttk.Entry(master=self.top_container)
        self.album_name_entry.pack(side=TOP, padx=5, fill=X, expand=YES)

        # artist name input
        # artist name frame
        self.artist_text_container = tk.Frame(master=self.top_container)
        self.artist_text_container.pack(side=TOP, pady=10, fill=X)
        # artist name text
        self.artist_text_label = ttk.Label(master=self.artist_text_container, text="Artist:")
        self.artist_text_label.pack(side=LEFT, padx=5)
        # artist name entry
        self.artist_name_entry = ttk.Entry(master=self.top_container)
        self.artist_name_entry.pack(side=TOP, padx=5, fill=X, expand=YES)

        # get cover button
        self.names_button = tk.Button(master=self.top_container, text="Get cover!",padx = 10,bd = 2,command=lambda : self.get_cover_pressed())
        self.names_button.pack(side=TOP, pady=20)

        # logo location and color box
        self.logo_loc_color_container = tk.Frame(master=self.top_container)
        self.logo_loc_color_container.pack(side=TOP, pady=10, fill=X)

        # get color button
        self.get_color_button = tk.Button(master=self.logo_loc_color_container, text="Text colour",padx = 10,bd = 2,command=lambda : self.color_picker())
        self.get_color_button.pack(pady=0)

        # second seperator
        self.center_separator = ttk.Separator(orient=HORIZONTAL)
        self.center_separator.pack(side=TOP, fill=X, pady=10) 

        # names button
        # ensure never only 1 or 2 buttons alone on a line
        self.max_length = 8
        if len(reviewers)%8 == (1 or 2):
            self.max_length = 6
        # loop through all names and create buttons for each
        for i in range(len(reviewers)):
            # create new line (frame) when on a multiple of max length
            if i % self.max_length == 0:
                self.names_container = tk.Frame()
                self.names_container.pack(side=TOP, pady=5)
            # create button
            self.names_button = tk.Button(
                master=self.names_container,
                text=reviewers[i],
                padx = 10,
                bd = 1,
                command=lambda x=reviewers[i]: self.name_pressed(x)
            )
            self.names_button.pack(side=LEFT, padx=5)

        # name title
        self.name_visual = tk.Label(textvariable = self.name_holder, font=('TkDefaultFixed', 10))
        self.name_visual.pack(side=TOP)

        # score entry box
        # score container
        self.score_container = ttk.Frame()
        self.score_container.pack(side=TOP, pady=10)
        # score label
        self.score_label = ttk.Label(master=self.score_container, text="Score:")
        self.score_label.pack(side=LEFT, padx=5)
        # score entry
        self.score_entry = tk.Entry(master=self.score_container)
        self.score_entry.pack(side=LEFT, padx=5)

        # post container container
        self.generate_button_container = ttk.Frame()
        self.generate_button_container.pack(side=BOTTOM, pady=5, fill=X)
        # create post button
        self.generate_button = tk.Button(master=self.generate_button_container,text="Create post!",padx = 10,bd = 2,command=lambda : self.generate_post())
        self.generate_button.pack(side=RIGHT, padx=20)

        # review entry box
        self.review_entry = tk.Text()
        self.review_entry['state'] = 'disabled'
        self.review_entry.pack(side=TOP, pady= 5, padx=20, fill=X)

    def save_csv(self):

        self.artist_name = (str(self.artist_name_entry.get()))
        self.album_name = str(self.album_name_entry.get())

        if (self.album_name != ""):
            if (self.artist_name != ""):
                folder = self.album_name + " - " + self.artist_name
                # create folder for slides
                if not os.path.exists(folder):
                    os.makedirs(folder)

                # create dataframe for reviews and export to csv
                reviews_dataframe = pandas.DataFrame(data={"Name": reviewers, "Review": self.text_reviews, "Score": self.score_reviews})
                reviews_dataframe.to_csv("./" + folder + "/" + self.album_name + " data.csv", sep=',',index=False)


    def open_csv(self):

        self.artist_name = (str(self.artist_name_entry.get()))
        self.album_name = str(self.album_name_entry.get())

        # if the user has entered both an album and an artist
        if (self.album_name != ""):
            if (self.artist_name != ""):
                folder = self.album_name + " - " + self.artist_name
                if os.path.exists("./" + folder + "/" + self.album_name + " data.csv"):

                    # import pre-existing csv back into dataframe
                    reviews_dataframe = pandas.read_csv("./" + folder + "/" + self.album_name + " data.csv")
                    csv_names = reviews_dataframe['Name'].fillna("").to_list()
                    csv_reviews = reviews_dataframe['Review'].fillna("").to_list()
                    csv_scores = reviews_dataframe['Score'].fillna("").to_list()
                    # csv_scores = [str(x).split('.')[0] for x in csv_scores]
                    csv_scores = [str(int(x)) if x != "" else "" for x in csv_scores]

                    j = 0
                    for name in reviewers:
                        if name in csv_names:
                            csv_index = csv_names.index(name)
                            self.text_reviews[j] = csv_reviews[csv_index]
                            self.score_reviews[j] = csv_scores[csv_index]

                            j += 1


    def color_picker(self):

        color_code = tk.colorchooser.askcolor(title ="Choose color") 
        print(color_code[1])
        hex_code = color_code[1].lstrip('#')
        self.rgb_code = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        

    def name_pressed(self, name):
        # unlock box

        if self.first_click == True:

            self.review_entry['state'] = 'normal'

            # change first click to false for next time
            self.first_click = False

        else:

            # store latest click in previous index
            self.previous_index = reviewers.index(self.clicked_name)
            # set current contents of review box as contents of previous entry
            self.text_reviews[self.previous_index] = (self.review_entry.get('1.0', 'end')).strip("\n")
            self.score_reviews[self.previous_index] = (self.score_entry.get())


        # set name_holder to selected name
        self.name_holder.set(name)

        # clear contents of review box
        self.review_entry.delete('1.0', END)
        self.score_entry.delete(0, 'end')

        # get latest click, set contents of box to index of that person
        self.clicked_name = name
        new_index = reviewers.index(self.clicked_name)
        self.review_entry.insert('1.0',str(self.text_reviews[new_index]))
        self.score_entry.insert(0,str(self.score_reviews[new_index]))

        # save input to CSV
        self.save_csv()


    def get_cover_pressed(self):
        # get artist name (replace " " with "+") and album name
        self.artist_name = str(self.artist_name_entry.get())
        self.album_name = str(self.album_name_entry.get())

        artist_name_with_plus = self.artist_name.replace(" ","+")

        # don't proceed if artist name or album name box empty
        if (self.artist_name == "") or (self.album_name == ""):

            # if not, give popup and leave section
            tk.messagebox.showinfo("Error!",  "Please enter album and artist names!")
            return()

        # open csv
        self.open_csv()

        # search for artist
        itunes_response = json.loads((requests.get('https://itunes.apple.com/search?term=' + artist_name_with_plus + '&entity=musicArtist')).text)

        # error if no artists were found
        if len(itunes_response['results']) == 0:
            tk.messagebox.showinfo("Error!","Artist " + self.artist_name + " not found!")
            return()

        self.found_artistid = ""

        # go through results, matching name input to actual names
        for item in itunes_response['results']:
            if self.artist_name.lower() == (item['artistName']).lower():
                # if found, get artistid
                self.found_artistid = item['artistId']
                break

        # if not found, error out
        if self.found_artistid == "":
            tk.messagebox.showinfo("Error!",  "Artist " + self.artist_name + " not found!")
            return()

        # get all albums from artistid found above
        itunes_response = json.loads((requests.get('https://itunes.apple.com/lookup?id=' + str(self.found_artistid) + '&entity=album')).text)
        # , verify=False

        # exit if no albums found
        if len(itunes_response['results']) == 0:
            tk.messagebox.showinfo("Error!", "Album " + self.album_name + " not found!")
            return()

        self.uncompressed = ""

        # go through albums
        for item in itunes_response['results']:
            if 'collectionName' in item:
                if self.album_name.lower().replace(" ","") in (item['collectionName']).lower().replace(" ",""):
                    # if album name matching entered name is found, save artist url
                    artworkURL = item['artworkUrl100']
                    splitURL = artworkURL.split("/")
                    self.uncompressed = "https://a1.mzstatic.com/us/r1000/063/"+"/".join(splitURL[5:12])
                    break

        if self.uncompressed == "":
            tk.messagebox.showinfo("Error!",  "Album " + self.album_name + " not found!")
            return()

        # save image using Image and resize to 200x200
        try:
            self.get_new_image = Image.open(requests.get(self.uncompressed, stream=True).raw)
        except requests.exceptions.SSLError:
            self.get_new_image = Image.open(requests.get(self.uncompressed, stream=True, verify=False).raw)
        

        # shrink cover for thumbnail
        thumbnail_image = (self.get_new_image).resize((200,200))
        # open image in Tk variable
        new_image_format = ImageTk.PhotoImage(thumbnail_image)
        # set picture on page to new image
        self.logo_label.configure(image=new_image_format)
        self.logo_label.image = new_image_format


    def generate_post(self):

        # init slides list
        slides = []

        # save current data to csv
        self.save_csv()

        # get both album and artist names
        self.artist_name = (str(self.artist_name_entry.get())).replace(" ","+")
        self.album_name = str(self.album_name_entry.get())

        # popup and exit if album cover hasn't been selected yet
        try:
            if self.get_new_image == "":
                tk.messagebox.showinfo("Error!",  "Please get album cover!")
                return()
        except AttributeError:
            tk.messagebox.showinfo("Error!",  "Please get album cover!")
            return()

        # run name_pressed to ensure most recent data is stored
        self.name_pressed(self.clicked_name)

        # resize cover to correct dimensions
        resized_image = self.get_new_image.resize((cover_size,cover_size))
        # blur image
        image_blurred = resized_image.filter(ImageFilter.GaussianBlur(radius = 50))

        ### slide1
        slide1 = resized_image.copy()
        # export
        slides.append(slide1)

        ### slide2
        # get average score
        slide2 = image_blurred.copy()
        score_ints = [int(n) for n in self.score_reviews if n]
        average = int(round(sum(score_ints)/len(score_ints),0))
        # font def
        font = ImageFont.truetype(font_file, average_font_size)
        # start draw
        draw = ImageDraw.Draw(slide2)
        # get font text size
        _, _, text_w, text_h = draw.textbbox((0,0),str(average)+'/100',font=font)
        # place text
        draw.text(((cover_size-text_w)/2, (cover_size-text_h)/2),str(average)+'/100',self.rgb_code,font=font)
        # export
        slides.append(slide2)

        ### slide3

        # loop over reviewers
        slide3_reviewers_and_scores = ""
        i = 0
        for name in reviewers:
            # if they have a score, add to string
            if self.score_reviews[i] != "":
                slide3_reviewers_and_scores += (reviewers[i] + " - " + self.score_reviews[i] + "\n")
            i += 1

        # remove additional \n
        slide3_reviewers_and_scores = slide3_reviewers_and_scores.removesuffix('\n')

        # create copy of blurred image
        slide3 = image_blurred.copy()

        # start draw
        draw = ImageDraw.Draw(slide3)

        self.drawing_title = True
        self.scores_title_current = individual_scores_title

        while self.drawing_title == True:

            # set title font
            font = ImageFont.truetype(font_file, self.scores_title_current)
            # get title size
            _, _, title_text_w, title_text_h = draw.textbbox((0,0),self.album_name,font=font)

            # if enough space, draw title - black 0,0,0 white 255,255,255
            if (title_text_w + (2 * individual_scores_border)) < cover_size:
                draw.text((individual_scores_border,(individual_scores_border/2)),self.album_name,self.rgb_code,font=font)

                # get remaining height pixels
                remaining_page_height = cover_size - title_text_h - (individual_scores_border * 2)

                self.drawing_title = False
            # if not, shrink font down and try again
            else:
                if self.scores_title_current <= ((individual_scores_title + individual_scores_font_size)/2):
                    if (title_text_w + (4 * individual_scores_border))/2 < cover_size:
                        print("two liner!")

                        album_name_list = self.album_name.split(' ')

                        album_name_second_line = []

                        for i in range (len(album_name_list)):
                            
                            album_name_second_line.insert(0, album_name_list[-1])
                            album_name_list.pop(-1)

                            print(album_name_second_line)

                            font = ImageFont.truetype(font_file, self.scores_title_current)
                            _, _, title_text_w, title_text_h = draw.textbbox((0,0)," ".join(album_name_list),font=font)

                            if (title_text_w + (2 * individual_scores_border)) < cover_size:

                                draw.text((individual_scores_border,(individual_scores_border/2))," ".join(album_name_list),self.rgb_code,font=font)
                                draw.text((individual_scores_border,(individual_scores_border/2) + title_text_h)," ".join(album_name_second_line),self.rgb_code,font=font)

                                # get remaining height pixels
                                remaining_page_height = cover_size - (title_text_h * 2) - (individual_scores_border * 2)

                                break

                        self.drawing_title = False


                print("Too big! width = " + str(title_text_w))
                self.scores_title_current -= 20


            # set font
            font = ImageFont.truetype(font_file, individual_scores_font_size)

            # get review list size
            _, _, text_w, text_h = draw.textbbox((0,0),slide3_reviewers_and_scores,font=font)

            # if enough space for all names
            if text_h < (cover_size - title_text_h - (individual_scores_border * 2)):

                # split lines into list
                slide3_reviewers_and_scores_list = slide3_reviewers_and_scores.split('\n')

                # get height of one line
                _, _, single_line_text_w, single_line_text_h = draw.textbbox((0,0),slide3_reviewers_and_scores_list[0],font=font)

                # calculate size of all lines combined
                total_reviewers_height = single_line_text_h * len(slide3_reviewers_and_scores_list)

                # calculate required spacing between lines
                if len(slide3_reviewers_and_scores_list) > 1:

                    line_spacing_pixels = (remaining_page_height - total_reviewers_height)/(len(slide3_reviewers_and_scores_list) - 1)

                    y_offset = cover_size - remaining_page_height - individual_scores_border

                    # loop over reviewers adding to page each time
                    for reviewer_line in slide3_reviewers_and_scores_list:

                        # white 255,255,255,  black 0,0,0
                        draw.text((individual_scores_border,y_offset),reviewer_line,self.rgb_code,font=font)

                        y_offset += (line_spacing_pixels + single_line_text_h)


            slides.append(slide3)

            ### slide 4+
            # create emoji font if it doesnt exist
            if not os.path.isfile('merged_font.ttf'):
                emoji_font = 'seguiemj.ttf'
                # Merge the fonts
                merger = Merger()
                new_font = merger.merge([regular_font, emoji_font])
                # Save the merged font
                new_font.save("merged_font.ttf")

            # calculate maximum text area
            max_line_pixels = text_box_size - (2 * text_box_border)
            # calculate text starting points
            text_starting_x = ((cover_size - text_box_size)/2)+text_box_border
            text_starting_y = ((cover_size - text_box_size)/2)+ text_box_border/2
            # caculate size of 1 line
            line_size = round((review_font_size * 1.33),0) - 10
            # calculate maximum number of lines for textbox and text size
            max_lines_per_page = ((text_box_size - text_box_border * 2) // line_size)

            # set font
            font = ImageFont.truetype('merged_font.ttf', review_font_size)
            # make working image
            working_image = image_blurred.copy()

            # calculate and draw full white box
            white_box_border = (cover_size - text_box_size) / 2
            draw = ImageDraw.Draw(working_image)
            draw.rectangle((white_box_border,white_box_border,(cover_size - white_box_border),(cover_size - white_box_border)),fill='white')
            # get font text size

            # init storage vars
            reviewer_number = 0 
            people_who_reviewed = []
            review_listlist_hyperobject = []

            #loop over all reviewers
            for reviewer_name in reviewers:

                # only go in if person has review
                if self.text_reviews[reviewer_number] != "":

                    # collect names of people who reviewed
                    people_who_reviewed.append(reviewer_name)
                    # review = name + persons review
                    person_full_review = (reviewer_name + ' - ' + self.text_reviews[reviewer_number]).replace("\n"," \n ")
                    # get review as list
                    person_review_list = person_full_review.split(" ")
                    # init finalised review list
                    person_review_formatted = [""]
                    # reset line counter
                    line_number = 0

                    # loop through every word in persons review
                    for word in person_review_list:

                        # current what line looks like before word added
                        current_line_holder = person_review_formatted[line_number]
                        # add word
                        person_review_formatted[line_number] += word
                        # draw line with new word
                        _, _, text_w, text_h = draw.textbbox((0,0),person_review_formatted[line_number],font=font)

                        # see if line is too long
                        if text_w > max_line_pixels:

                            # put line back to what it was if too long
                            person_review_formatted[line_number] = current_line_holder
                            # move to next line
                            line_number += 1
                            # create space for new line in list
                            person_review_formatted.append('')
                            # add word to new line
                            person_review_formatted[line_number] += word

                        # add a space after word
                        person_review_formatted[line_number] += ' '

                        # if word is \n or has \n
                        if '\n' in word:
                            # move to next line
                            line_number += 1
                            # create space for next line in list
                            person_review_formatted.append("")

                    # once complete, add list to list of lists
                    review_listlist_hyperobject.append(person_review_formatted)

                # move to next person
                reviewer_number += 1

            # init page length counter
            current_page_length = 0
            # reset reviewer number var

            # initialise variables
            reviewer_number = 0
            pages_mega_list_list = []
            current_page_list = []
            page_metadata_tracker = []
            metadata_mega_list_list = []

            # loop through reviewers
            for reviewer in people_who_reviewed:
                
                # extract current review
                current_review = review_listlist_hyperobject[reviewer_number]
                # reset current review line counter
                current_review_line_counter = 0
                # keep looping through lines of review

                # before adding review to page, if there is less than 1/2 page left start new one
                if (max_lines_per_page - len(current_page_list)) < (1/2 * max_lines_per_page):

                    pages_mega_list_list.append(current_page_list)
                    metadata_mega_list_list.append(page_metadata_tracker)
                    page_metadata_tracker = []
                    current_page_list = []

                # loop through lines of review
                for review_line in current_review:

                    # if page is full, start new one
                    if len(current_page_list) >= max_lines_per_page:

                        pages_mega_list_list.append(current_page_list)
                        metadata_mega_list_list.append(page_metadata_tracker)
                        page_metadata_tracker = []
                        current_page_list = []

                    # add line to page list and add a metadata line for line
                    current_page_list.append(review_line)
                    page_metadata_tracker.append('')

                    # add metadata

                    # track starting line for bold name
                    if current_review_line_counter == 0:

                        page_metadata_tracker[-1] += 'first-line'

                    # track new lines for non-justified
                    if ('\n' in review_line) or (current_review_line_counter == (len(current_review)-1)):

                        page_metadata_tracker[-1] += 'non-justified'

                    # count up line counter
                    current_review_line_counter += 1

                # 
                if len(current_page_list) < max_lines_per_page:

                    current_page_list.append('')
                    page_metadata_tracker.append('')
                    page_metadata_tracker[-1] += 'non-justified'
                
                # count up reviewer number
                reviewer_number += 1

            # add final review page to list list
            pages_mega_list_list.append(current_page_list)
            metadata_mega_list_list.append(page_metadata_tracker)


            # remove empty lines at end of lists
            for i in range(len(pages_mega_list_list)):

                if pages_mega_list_list[i][-1] == '':
                    pages_mega_list_list[i].pop(-1)
                    metadata_mega_list_list[i].pop(-1)

            # set page counter
            page_counter = 0

            # for each page list
            for final_page_list in pages_mega_list_list:

                # reset line counter
                page_line_counter = 0

                # create copy image to work on
                working_image = image_blurred.copy()
                # load font
                font = ImageFont.truetype('merged_font.ttf', review_font_size)

                # 
                # if final_page_list[-1] == '':
                #     final_page_list.pop(-1)

                # draw white box
                draw = ImageDraw.Draw(working_image)
                draw.rectangle((white_box_border,white_box_border,(cover_size - white_box_border),(cover_size - white_box_border)),fill='white')

                # reset line offset 
                text_starting_y = ((cover_size - text_box_size)/2)+ text_box_border/2

                # for each line in page list
                for line in final_page_list:

                    # set word start offset to 0
                    word_start_offset = 0

                    # if first line, draw name in bold
                    if 'first-line' in metadata_mega_list_list[page_counter][page_line_counter]:

                        # get first word of line
                        current_reviewer_name = (line.split(' '))[0]

                        # load bold font
                        font = ImageFont.truetype('C:/Windows/Fonts/Cambria/cambriab.ttf', review_font_size)
                        # draw name
                        draw.text((text_starting_x,text_starting_y),current_reviewer_name + ' ',(0,0,0),font=font)
                        # append pixel length of this text to word start x value
                        _, _, word_width, word_height = draw.textbbox((0,0),current_reviewer_name + ' ',font=font)
                        word_start_offset += word_width

                        # remove first word from line
                        line = line.replace(current_reviewer_name + ' ','')

                        # set font back to regular text
                        font = ImageFont.truetype('merged_font.ttf', review_font_size)
                    
                    # if line is non justified, draw text normally
                    if 'non-justified' in metadata_mega_list_list[page_counter][page_line_counter]:

                        draw.text(((text_starting_x + word_start_offset),text_starting_y),line,(0,0,0),font=font)

                    # if not, justify
                    else:

                        line_word_list = line.split()

                        # calculate size of line without spaces, then calculate how much space needed between each word
                        _, _, no_spaces_width, no_spaces_height = draw.textbbox((0,0),"".join(line_word_list),font=font)

                        required_space_width = (max_line_pixels - no_spaces_width - word_start_offset) / (len(line_word_list) - 1)

                        # justify text - cycle through each word
                        for line_word in line_word_list:
                            # draw word
                            draw.text(((text_starting_x + word_start_offset),text_starting_y),line_word,(0,0,0),font=font,)
                            # calculate that words width
                            _, _, word_width, word_height = draw.textbbox((0,0),line_word,font=font)
                            # add width to offset
                            word_start_offset += word_width + required_space_width  


                    # after all words add height of font to starting y position
                    text_starting_y += round((review_font_size * 1.33),0) - 10 

                    # increase line counter
                    page_line_counter += 1

                # draw blurred box to crop white box
                #replace_box_height = int(text_starting_y - (round((review_font_size * 1.33),0) - 10 ) + text_box_border)
                replace_box_height = int(text_starting_y + text_box_border)
                replace_box = (0,replace_box_height,cover_size,cover_size)
                replace_image = image_blurred.copy()
                replace_region = replace_image.crop(replace_box)
                working_image.paste(replace_region,replace_box)                        

                # save slide
                slides.append(working_image)
                page_counter += 1


            ###  export
            # create folder for slides
            folder = self.album_name + " - " + self.artist_name
            if not os.path.exists(folder):
                os.makedirs(folder)

            # init slide number
            slide_number = 1

            # loop over slides, save to folder
            for slide in slides:
                slide.save(folder + '/slide' + str(slide_number) + '.png')

                slide_number += 1

            # save blurred image
            image_blurred.save(folder + '/blurred.png')


################################

if __name__ == "__main__":

    app = ttk.Window(
        title="DP_Postmaker",
        themename="cerculean",
        size=(800, 900),
        resizable=(True, True),
    )
    DP_Postmaker(app)
    app.mainloop()