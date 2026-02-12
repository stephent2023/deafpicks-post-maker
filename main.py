""" Module for generating DP instagram posts """

import json
import os
import webbrowser
import tkinter as tk
from tkinter import colorchooser, messagebox
import requests
import pandas
import ttkbootstrap as ttk
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk, UnidentifiedImageError
from ttkbootstrap.constants import TOP, BOTTOM, LEFT, RIGHT, HORIZONTAL, X, YES, NO, END

# vars
REVIEWERS = ('James', 'Ewan', 'Sam', 'Joe', 'Ollie', 'Steve', 'Will', 'Bert', 'Fin', 'Serafina', 'Adam')
TITLE_FONT_FILE = 'fonts/cambriab.ttf'
REGULAR_FONT = 'fonts/cambria_with_emojis.ttf'
COVER_SIZE = 3000
SSL_ENABLED = True

# main
class DPPostmaker(ttk.Frame):
    """ Postmaker run class"""

    def __init__(self, master, **kwargs):
        super().__init__(master, padding=10, **kwargs)

        # init vars
        self.name_holder = ttk.StringVar(value="Select a name to start!")
        self.text_reviews = [""] * len(REVIEWERS)
        self.score_reviews = [""] * len(REVIEWERS)
        self.rgb_code = (255,255,255)
        self.image_url = ""
        self.get_new_image = ""
        self.image_blurred = ""

        # create the main screen
        self.create_screen()


    def create_screen(self):
        """ Creates the UI """

        # title
        self.title = ttk.Label(text="DP Post Generator 0.93", font=('TkDefaultFixed', 30), justify='left')
        self.title.pack(side= TOP, pady=0)

        # header separator
        self.header_separator = ttk.Separator(orient=HORIZONTAL)
        self.header_separator.pack(side=TOP, fill=X, pady=5)

        # album entry and image frame
        self.top_container = ttk.Frame()
        self.top_container.pack(side=TOP, pady=0)

        # album image slot - start with placeholder square
        img = Image.new('RGB', (200, 200), color = 'Gray')
        draw = ImageDraw.Draw(img)
        draw.rectangle((1,1,198,198),fill='white')

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
        self.names_button = tk.Button(master=self.top_container, text="Get cover!",padx = 10,bd = 2,command=self.get_cover_pressed)
        self.names_button.pack(side=TOP, pady=10)

        # open cover image
        self.open_cover_button = tk.Button(master=self.top_container,text="Open cover!",padx = 10,bd = 2,command=self.open_cover_pressed)
        self.open_cover_button.pack(side=TOP, expand=NO)
        self.open_cover_button.config(state=tk.DISABLED)

        # get color button
        self.get_color_button = tk.Button(master=self.top_container, text="Text colour",padx = 10,bd = 2,command=self.color_picker)
        self.get_color_button.pack(pady=10)

        # second seperator
        self.center_separator = ttk.Separator(orient=HORIZONTAL)
        self.center_separator.pack(side=TOP, fill=X, pady=10)

        # names button
        # ensure never only 1 or 2 buttons alone on a line
        self.max_length = 8
        if len(REVIEWERS)%8 == (1 or 2):
            self.max_length = 6
        # loop through all names and create buttons for each
        for i, reviewer in enumerate(REVIEWERS):
            # create new line (frame) when on a multiple of max length
            if i % self.max_length == 0:
                self.names_container = tk.Frame()
                self.names_container.pack(side=TOP, pady=5)
            # create button
            self.names_button = tk.Button(
                master=self.names_container,
                text=reviewer,
                padx = 10,
                bd = 1,
                command=lambda x=reviewer: self.name_pressed(x)
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
        self.gen_button_container = ttk.Frame()
        self.gen_button_container.pack(side=BOTTOM, pady=5, fill=X)
        # create post button
        self.generate_button = tk.Button(master=self.gen_button_container,text="Create post!",padx = 10,bd = 2,command=self.generate_post)
        self.generate_button.pack(side=RIGHT, padx=20)

        # review entry box
        self.review_entry = tk.Text()
        self.review_entry['state'] = 'disabled'
        self.review_entry.pack(side=TOP, pady= 5, padx=20, fill=X)

    def save_csv(self):
        """ Saves inputs to a CSV file which can be loade later """

        artist_name = (str(self.artist_name_entry.get()))
        album_name = str(self.album_name_entry.get())

        if album_name != "":
            if artist_name != "":
                folder = album_name + " - " + artist_name
                # create folder for slides
                if not os.path.exists(folder):
                    os.makedirs(folder)

                # create dataframe for reviews and export to csv
                reviews_dataframe = pandas.DataFrame(data={"Name": REVIEWERS, "Review": self.text_reviews, "Score": self.score_reviews})
                reviews_dataframe.to_csv("./" + folder + "/" + album_name + " data.csv", sep=',',index=False)


    def open_csv(self):
        """ Looks for pre existing CSV file for album and loads it if found """

        artist_name = (str(self.artist_name_entry.get()))
        album_name = str(self.album_name_entry.get())

        # if the user has entered both an album and an artist
        if album_name != "":
            if artist_name != "":
                folder = album_name + " - " + artist_name
                if os.path.exists("./" + folder + "/" + album_name + " data.csv"):

                    # import pre-existing csv back into dataframe
                    reviews_dataframe = pandas.read_csv("./" + folder + "/" + album_name + " data.csv")
                    csv_names = reviews_dataframe['Name'].fillna("").to_list()
                    csv_reviews = reviews_dataframe['Review'].fillna("").to_list()
                    csv_scores = reviews_dataframe['Score'].fillna("").to_list()
                    # csv_scores = [str(x).split('.')[0] for x in csv_scores]
                    csv_scores = [str(int(x)) if x != "" else "" for x in csv_scores]

                    j = 0
                    for name in REVIEWERS:
                        if name in csv_names:
                            csv_index = csv_names.index(name)
                            self.text_reviews[j] = csv_reviews[csv_index]
                            self.score_reviews[j] = csv_scores[csv_index]

                            j += 1


    def color_picker(self):
        """ Opens the OS color picker UI and sets rgb code to the user selection """

        color_code = colorchooser.askcolor(title ="Choose color")
        print(color_code[1])
        hex_code = color_code[1].lstrip('#')
        self.rgb_code = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))


    def name_pressed(self, name=''):
        """ Saves input review data and loads data of name just clicked """

        # if the box was previously clicked
        if self.name_holder.get() in REVIEWERS:

            # save previously entered review and score to lists
            person_index = REVIEWERS.index(self.name_holder.get())
            self.text_reviews[person_index] = (self.review_entry.get('1.0', 'end')).strip("\n")
            self.score_reviews[person_index] = self.score_entry.get()

        else:

            self.review_entry['state'] = 'normal'

        # allow no name to be input
        if name != '':
            # set name_holder to selected name
            self.name_holder.set(name)

            # clear contents of review box
            self.review_entry.delete('1.0', END)
            self.score_entry.delete(0, 'end')

            # insert review and score of newly clicked person into box
            new_index = REVIEWERS.index(name)
            self.review_entry.insert('1.0',str(self.text_reviews[new_index]))
            self.score_entry.insert(0,str(self.score_reviews[new_index]))

        # save input to CSV
        self.save_csv()


    def get_album_info(self, album_name, artist_name):
        ''' Take an input of album name and artist name, and returns itunes album details '''

        found_artistid = None

        # send initial request to itunes searching for artist name
        request_url = 'https://itunes.apple.com/search?term=' + artist_name + '&entity=musicArtist'
        itunes_response = json.loads((
            requests.get(request_url, verify=SSL_ENABLED, timeout=10)).text)

        # compare found names to results, set found_artistid to matching one
        for item in itunes_response['results']:
            if artist_name.lower().replace("+"," ") == (item['artistName']).lower():
                found_artistid = item['artistId']
                break

        # if cant find anything, send error, print found artists and return
        if found_artistid is None:
            print('\n----------')
            print('ERROR, artist not found')
            print('with following link: https://itunes.apple.com/search?term=' + artist_name + '&entity=musicArtist')
            if len(itunes_response['results']) > 0:
                print("Found the following similar artists:")
                for item in itunes_response['results']:
                    print(item['artistName'])
                    print(item['artistLinkUrl'])
                    print('-')
            else:
                print('No similar artists found! Check spelling')
            return ''

        # send request getting list of collections for found artist
        request_url = 'https://itunes.apple.com/lookup?id=' + str(found_artistid) + '&entity=album'
        itunes_response = json.loads((requests.get(request_url, verify=SSL_ENABLED, timeout=10)).text)

        # loop through all returned items
        for item in itunes_response['results']:
            # only if its an album and the album name matches the input one
            if 'collectionName' in item and album_name.lower() in (item['collectionName']).lower():
                # get artworkURL
                return item

        # if can't find anything matching, error out
        print("\n----------")
        print('ERROR! Unable to find artwork!')
        print('with following link: https://itunes.apple.com/lookup?id=' + str(found_artistid) + '&entity=album')
        # if the response has results, list out possible ones
        if len(itunes_response['results']) > 0:
            print('Found the following albums for artist ' + artist_name)
            for item in itunes_response['results']:
                if 'collectionName' in item:
                    print(item['collectionName'])
                    print('-')
        else:
            print('No albums found for artist ' + artist_name)

        return ''


    def get_uncompressed_cover_image(self, artwork_url):
        """ Takes itunes artwork url and returns a PIL image at the highest available quality """

        cover_image = None

        # try to getting uncompressed artwork from a1 server
        try:
            split_url = artwork_url.split("/")
            self.image_url = "https://a1.mzstatic.com/us/r1000/063/"+"/".join(split_url[5:12])
            cover_image = (Image.open(requests.get(self.image_url, stream=True, verify=SSL_ENABLED, timeout=10).raw))

        except UnidentifiedImageError:

            # try getting compressed artwork - older albums dont have uncompressed
            try:
                lowq_image = artwork_url.split("/")[0:-1]
                lowq_image.append("100000x100000-999.jpg")
                self.image_url = "/".join(lowq_image)
                cover_image = (Image.open(
                    requests.get(self.image_url, stream=True, verify=SSL_ENABLED, timeout=10).raw)).resize((200, 200))

            except UnidentifiedImageError:

                print("No cover found at " + self.image_url)

                return cover_image

        return cover_image


    def get_cover_pressed(self):
        """ Uses the artist name and album name inputs to try and find album art """

        # get artist name (replace " " with "+") and album name
        artist_name = (str(self.artist_name_entry.get())).replace(" ","+")
        album_name = str(self.album_name_entry.get())

        # catch album name!
        if album_name == "":
            messagebox.showinfo("Error!",  "Enter an album name!")
            return

        # catch artist name!
        if artist_name == "":
            messagebox.showinfo("Error!",  "Enter an artist name!")
            return

        # get album info
        album_info = self.get_album_info(album_name, artist_name)

        # if no info found, return
        if album_info == '':
            return

        # get uncompressed image
        self.get_new_image = self.get_uncompressed_cover_image(album_info['artworkUrl100'])

        # shrink cover for thumbnail
        thumbnail_image = (self.get_new_image).resize((200,200))
        # open image in Tk variable
        new_image_format = ImageTk.PhotoImage(thumbnail_image)
        # set picture on page to new image - seem to need both commands
        self.logo_label.configure(image=new_image_format)
        self.logo_label.image = new_image_format

        # open csv
        self.open_csv()
        self.open_cover_button.config(state=tk.NORMAL)


    def open_cover_pressed(self):
        """ Opens the current album cover in the user's browser """

        # putting this in a function removes the need for lambda
        webbrowser.open(self.image_url, new=0, autoraise=True)


    def generate_average_slide(self):
        """ Generates a slide with blurred album art in the background and average score out of 100 """

        # get average score
        slide2 = self.image_blurred.copy()
        score_ints = [int(n) for n in self.score_reviews if n]
        average = int(round(sum(score_ints)/len(score_ints),0))
        # font def
        average_font_size = COVER_SIZE / 5
        font = ImageFont.truetype(TITLE_FONT_FILE, average_font_size)
        # start draw
        draw = ImageDraw.Draw(slide2)
        # get font text size
        _, _, text_w, text_h = draw.textbbox((0,0),str(average)+'/100',font=font)
        # place text
        draw.text(((COVER_SIZE-text_w)/2, (COVER_SIZE-text_h)/2),str(average)+'/100',self.rgb_code,font=font)

        # export
        return slide2


    def print_title(self, slide, title):
        """ Places title of up to 2 lines on the page """

        # start draw
        draw = ImageDraw.Draw(slide)

        title_list = title.split()

        side_border_size = COVER_SIZE / 21
        text_height_offset  = COVER_SIZE / 16
        title_size = COVER_SIZE / 5

        # keep looping until title is printed
        printing_title = True
        while printing_title is True:

            # set font
            font = ImageFont.truetype(TITLE_FONT_FILE, title_size)
            # get title size
            _, _, title_text_w, title_text_h = draw.textbbox((0,0),title,font=font)

            # if title is within maximum allowed width
            if title_text_w <= ( COVER_SIZE - (2 * side_border_size) ):

                # don't let the title be too small... if it is, try going bigger
                if title_text_w < ( COVER_SIZE / 2 ) - side_border_size and title_text_h < ( COVER_SIZE / 3 ):

                    title_size = title_size * 1.03

                else:

                    # calculate title offset - text does not start at 0 height
                    text_height_offset -= (title_size / 3.34)

                    # draw title
                    draw.text((side_border_size,text_height_offset),title,self.rgb_code,font=font)

                    # escape while loop
                    printing_title = False

            # if not
            else:

                # if more than one word title and two lines is shorter than max height
                if len(title_list) > 1 and ( title_text_h * 2 ) < ( COVER_SIZE / 3 ):

                    # figure out where to start new line
                    # keep adding words to title first line until it is too big
                    # then add all remaining words to the second line
                    title_line_1 = []
                    title_line_2 = title_list.copy()

                    calculating_first_line = True

                    # keep looping until title can be printed
                    while calculating_first_line is True:

                        title_line_1.append(title_line_2[0])

                        # get width of current first line
                        _, _, title_text_w, title_text_h = draw.textbbox((0,0)," ".join(title_line_1),font=font)

                        # if width is more than title max_width
                        if title_text_w > ( COVER_SIZE - (2 * side_border_size) ):

                            # remove newly added word from list
                            title_line_1.pop(-1)

                            calculating_first_line = False

                        else:

                            # remove word from line 2
                            title_line_2.pop(0)

                    # now check length of second line
                    _, _, title_text_w, title_text_h = draw.textbbox((0,0)," ".join(title_line_2),font=font)

                    # if second line fits on screen
                    if title_text_w < ( COVER_SIZE - (2 * side_border_size) ):

                        # print
                        _, _, title_text_w, title_text_h = draw.textbbox((0,0)," ".join(title_line_1),font=font)
                        text_height_offset -= (title_size / 3.34)

                        # draw first line
                        draw.text((side_border_size,text_height_offset)," ".join(title_line_1),self.rgb_code,font=font)

                        # calculate second line offset
                        text_height_offset += (title_size * 0.9)

                        # get second line stuff
                        _, _, title_text_w, title_text_h = draw.textbbox((0,0)," ".join(title_line_2),font=font)

                        # draw second line
                        draw.text((side_border_size,text_height_offset)," ".join(title_line_2),self.rgb_code,font=font)

                        # end title loop
                        printing_title = False

                    # if not, smaller size and loop
                    else:

                        title_size = title_size * 0.97

                # if not, smaller size and loop
                else:

                    title_size = title_size * 0.97


        # calculate new offset
        text_height_offset += title_text_h

        return slide, text_height_offset, title_size


    def print_lines(self, slide, lines_list, height_offset, text_size):
        """ Prints lines from lines_list onto page, starting from the height offset to the bottom """

        # calculate remaining height
        remaining_height = COVER_SIZE - height_offset
        border_size = COVER_SIZE / 21

        # start draw
        draw = ImageDraw.Draw(slide)

        printing_names = True
        while printing_names is True:

            # set font size
            font = ImageFont.truetype(TITLE_FONT_FILE, text_size)

            # calculate text space required for the amount of people
            text_space_required = (( text_size -  ( text_size / 3.34 ) ) * len(lines_list))

            # calculate blank space required
            blank_space_required = (( text_size / 3 ) * ( len(lines_list) )) + border_size

            # total space required
            total_space_required = text_space_required + blank_space_required

            # if enough space for names
            if total_space_required < remaining_height:

                # calculate how much gap between names
                names_spacing = (remaining_height - text_space_required - border_size) / (len(lines_list))

                # loop through slides and print
                for review in lines_list:

                    # add spacing
                    height_offset +=  names_spacing - ( text_size / 3.34 )

                    # print line at offset
                    draw.text((border_size,height_offset),review,self.rgb_code,font=font)

                    # add a little more offset
                    height_offset += text_size

                printing_names = False

            # else try smaller size
            else:

                text_size = text_size * 0.97

        return slide


    def generate_scores_slide(self, album_name):
        """ Generates a slide with blurred album art in the background and every persons score """

        slide3 = self.image_blurred.copy()

        # print title onto slide
        slide3, height_offset, title_size = self.print_title(slide3, album_name)

        # init storage list
        slide3_reviewers_and_scores = []
        # loop through REVIEWERS
        for i, reviewer in enumerate(REVIEWERS):
            # if they have a score, add to list
            if self.score_reviews[i] != "":
                slide3_reviewers_and_scores.append(reviewer + " - " + self.score_reviews[i])

        # ensure reviews are always a bit smaller than the title
        paragraph_starting_size = title_size * 0.8

        # print scores on slide
        slide3 = self.print_lines(slide3, slide3_reviewers_and_scores, height_offset, paragraph_starting_size)

        # return
        return slide3


    def generate_reviews_slides(self):
        """ Generates several slides with all the input reviews listed out """

        reviews_slides = []

        # define dimensions
        review_font_size = COVER_SIZE / 37.5
        text_box_size = 3000 * (13/15)
        text_box_border = COVER_SIZE / 60

        # calculate maximum text area
        max_line_pixels = text_box_size - (2 * text_box_border)
        # calculate text starting points
        text_starting_x = ((COVER_SIZE - text_box_size)/2)+text_box_border
        text_starting_y = ((COVER_SIZE - text_box_size)/2)+ text_box_border/2
        # caculate size of 1 line
        line_size = round((review_font_size * 1.33),0) - 10
        # calculate maximum number of lines for textbox and text size
        max_lines_per_page = (text_box_size - text_box_border * 2) // line_size

        # set font
        font = ImageFont.truetype(REGULAR_FONT, review_font_size)
        # make working image
        working_image = self.image_blurred.copy()

        # calculate and draw full white box
        white_box_border = (COVER_SIZE - text_box_size) / 2
        white_box_opposite_border = COVER_SIZE - white_box_border
        draw = ImageDraw.Draw(working_image)
        draw.rectangle((white_box_border,white_box_border,white_box_opposite_border,white_box_opposite_border),fill='white')
        # get font text size

        # init storage vars
        reviewer_number = 0
        people_who_reviewed = []
        review_listlist_hyperobject = []

        #loop over all REVIEWERS
        for reviewer_name in REVIEWERS:

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
                    _, _, text_w, _ = draw.textbbox((0,0),person_review_formatted[line_number],font=font)

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

        # reset reviewer number var
        # initialise variables
        reviewer_number = 0
        pages_mega_list_list = []
        current_page_list = []
        page_metadata_tracker = []
        metadata_mega_list_list = []

        # loop through REVIEWERS
        for _ in people_who_reviewed:

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
        # for i in range(len(pages_mega_list_list)):
        for i, _ in enumerate(pages_mega_list_list):

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
            working_image = self.image_blurred.copy()
            # load font
            font = ImageFont.truetype(REGULAR_FONT, review_font_size)

            # draw white box
            draw = ImageDraw.Draw(working_image)
            draw.rectangle((white_box_border,white_box_border,(COVER_SIZE - white_box_border),(COVER_SIZE - white_box_border)),fill='white')

            # reset line offset
            text_starting_y = ((COVER_SIZE - text_box_size)/2)+ text_box_border/2

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
                    _, _, word_width, _ = draw.textbbox((0,0),current_reviewer_name + ' ',font=font)
                    word_start_offset += word_width

                    # remove first word from line
                    line = line.replace(current_reviewer_name + ' ','')

                    # set font back to regular text
                    font = ImageFont.truetype(REGULAR_FONT, review_font_size)

                # if line is non justified, draw text normally
                if 'non-justified' in metadata_mega_list_list[page_counter][page_line_counter]:

                    draw.text(((text_starting_x + word_start_offset),text_starting_y),line,(0,0,0),font=font)

                # if not, justify
                else:

                    line_word_list = line.split()

                    # calculate size of line without spaces, then calculate how much space needed between each word
                    _, _, no_spaces_width, _ = draw.textbbox((0,0),"".join(line_word_list),font=font)

                    required_space_width = (max_line_pixels - no_spaces_width - word_start_offset) / (len(line_word_list) - 1)

                    # justify text - cycle through each word
                    for line_word in line_word_list:
                        # draw word
                        draw.text(((text_starting_x + word_start_offset),text_starting_y),line_word,(0,0,0),font=font,)
                        # calculate that words width
                        _, _, word_width, _ = draw.textbbox((0,0),line_word,font=font)
                        # add width to offset
                        word_start_offset += word_width + required_space_width


                # after all words add height of font to starting y position
                text_starting_y += round((review_font_size * 1.33),0) - 10

                # increase line counter
                page_line_counter += 1

            # draw blurred box to crop white box
            #replace_box_height = int(text_starting_y - (round((review_font_size * 1.33),0) - 10 ) + text_box_border)
            replace_box_height = int(text_starting_y + text_box_border)
            replace_box = (0,replace_box_height,COVER_SIZE,COVER_SIZE)
            replace_image = self.image_blurred.copy()
            replace_region = replace_image.crop(replace_box)
            working_image.paste(replace_region,replace_box)

            # save slide
            reviews_slides.append(working_image)
            page_counter += 1

        return reviews_slides


    def generate_post(self):
        """ Generates all slides required for the post """

        # init slides list
        slides = []

        # run name_pressed to ensure most recent data is stored
        self.name_pressed()

        # get both album and artist names
        artist_name = str(self.artist_name_entry.get())
        album_name = str(self.album_name_entry.get())

        # popup and exit if album cover hasn't been selected yet
        try:
            if self.get_new_image == "":
                messagebox.showinfo("Error!",  "Please get album cover!")
                return
        except AttributeError:
            messagebox.showinfo("Error!",  "Please get album cover!")
            return


        # resize cover to correct dimensions
        resized_image = self.get_new_image.resize((COVER_SIZE,COVER_SIZE))
        # blur image
        self.image_blurred = resized_image.filter(ImageFilter.GaussianBlur(radius = 50))

        ## slide1
        slide1 = resized_image.copy()
        # export
        slides.append(slide1)

        # only generate slide 2 and 3 if there are score reviews
        for score in self.score_reviews:
            if score != '':
                # slide 2
                slides.append(self.generate_average_slide())
                # slide 3
                slides.append(self.generate_scores_slide(album_name))
                break

        # only generate slide 4 if there are text reviews
        for review in self.text_reviews:
            if review != '':
                # ### slide 4+
                slides += self.generate_reviews_slides()
                break

        ###  export
        # create folder for slides
        folder = album_name + " - " + artist_name
        if not os.path.exists(folder):
            os.makedirs(folder)

        # init slide number
        slide_number = 1

        # loop over slides, save to folder
        for slide in slides:
            slide.save(folder + '/slide' + str(slide_number) + '.png')
            slide_number += 1

        # save blurred image
        self.image_blurred.save(folder + '/blurred.png')

################################

if __name__ == "__main__":

    app = ttk.Window(
        title="DP Postmaker",
        themename="cerculean",
        size=(800, 900),
        resizable=(True, True),
    )
    DPPostmaker(app)
    app.mainloop()
