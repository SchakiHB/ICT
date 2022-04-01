import cv2
import imutils   #contour
import tkinter as tk    #gui
from tkinter import filedialog    #fileloader in gui
import PIL.Image, PIL.ImageTk    #image view in gui
import keyboard    #keyboard inputs

from functools import partial
# from pynput.keyboard import Key, Listener

zoom = 1
offset_x = 0
offset_y = 0
matchthreshold = 0.7
manual_offset = False
stepsize = 10
imagefactor = 1
matched = False
matchtext = "not matched"
img1matched = cv2.imread("images/img1.png")
img2matched = cv2.imread("images/img1.png")
global img1orig
global img2orig
img1orig = cv2.imread("images/img1.png")
img2orig = cv2.imread("images/img1.png")


def create_img1():
    global img1orig
    img1orig = cv2.imread(tk.filedialog.askopenfilename(title='open'))
    img1orig = cv2.cvtColor(img1orig, cv2.COLOR_BGR2RGB)


def create_img2():
    global img2orig
    img2orig = cv2.imread(tk.filedialog.askopenfilename(title='open'))
    img2orig = cv2.cvtColor(img2orig, cv2.COLOR_BGR2RGB)


class ScrollbarFrame(tk.Frame):

    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        # create Scrollbars
        vsb = tk.Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(self, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hsb.set)
        hsb.configure(command=self.canvas.xview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = tk.Frame(self.canvas, background=self.canvas.cget('bg'))
        self.canvas.create_window((4, 4), window=self.scrolled_frame, anchor="nw")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class App(tk.Tk):

    class ScrollableImage(tk.Frame):
        def __init__(self, master=None, **kw):
            self.image = kw.pop('image', None)
            sw = kw.pop('scrollbarwidth', 10)
            label = kw.pop('Label', "Label")
            super(App.ScrollableImage, self).__init__(master=master, **kw)
            self.cnvs = tk.Canvas(self, highlightthickness=0, **kw)
            self.cnvs.create_image(0, 0, anchor='nw', image=self.image)

            # Vertical and Horizontal scrollbars
            self.v_scroll = tk.Scrollbar(self, orient='vertical', width=sw)
            self.h_scroll = tk.Scrollbar(self, orient='horizontal', width=sw)

            self.label = tk.Label(self, text=label)
            self.label.grid(row=0, column=0, sticky='nw', padx=2, pady=2)

            # Grid and configure weight.
            self.cnvs.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
            self.h_scroll.grid(row=1, column=0, sticky='ew', padx=2, pady=2)
            self.v_scroll.grid(row=0, column=1, sticky='ns', padx=2, pady=2)
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)

            # Set the scrollbars to the canvas
            self.cnvs.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
            # Set canvas view to the scrollbars
            self.v_scroll.config(command=self.cnvs.yview)
            self.h_scroll.config(command=self.cnvs.xview)

            # Assign the region to be scrolled
            self.cnvs.config(scrollregion=self.cnvs.bbox('all'))
            self.cnvs.bind_class(self.cnvs, "<MouseWheel>", self.mouse_scroll)

        def mouse_scroll(self, evt):
            if evt.state == 0:
                self.cnvs.yview_scroll(int(-1 * (evt.delta / 120)), 'units')
            if evt.state == 1:
                self.cnvs.xview_scroll(int(-1 * (evt.delta / 120)), 'units')

    def __init__(self, *args, **kwargs):
        global img1orig,img2orig, matchthreshold, matchthresholdslider, matchtext, matchstatus, image1_window, image2_window, image3_window, image4_window, keyboard_active

        super().__init__()
        sbf = ScrollbarFrame(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        sbf.grid(row=0, column=0, sticky='nsew')
        self.title("Image Compare Tool")

        #creates scrollable Frame for the App
        frame = sbf.scrolled_frame
        keyboard_active = tk.BooleanVar(frame)
    #create Buttons and such

        #loading Images
        btn1 = tk.Button(frame, text='Load first Image', command=create_img1)
        btn2 = tk.Button(frame, text='Load second Image', command=create_img2)
        btn3 = tk.Button(frame, text="Show combined", command=lambda *args: App.show_combined_unmatch(self,img1orig, img2orig,frame))

        #movement
        btnup = tk.Button(frame, text='Up', command=lambda *args: App.increase_offset_y(self,img1orig, img2orig, frame))
        btndown = tk.Button(frame, text='Down', command=lambda *args: App.decrease_offset_y(self,img1orig, img2orig, frame))
        btnright = tk.Button(frame, text='Right', command=lambda *args: App.increase_offset_x(self,img1orig, img2orig, frame))
        btnleft = tk.Button(frame, text='Left', command=lambda *args: App.decrease_offset_x(self,img1orig, img2orig, frame))
        btnreset = tk.Button(frame, text='Reset', command=lambda *args: App.reset_offsets(self,img1orig, img2orig, frame))
        keyboarduse = tk.Checkbutton(frame, text="activate Keys", variable=keyboard_active, onvalue=True, offvalue=False, command=lambda *args: App.activate_keys(self,img1orig, img2orig, frame))

        #stepsize buttons
        btnstep1 = tk.Button(frame, text='Stepsize 1', command=lambda *args: App.change_stepsize(self,1))
        btnstep10 = tk.Button(frame, text='Stepsize 10', command=lambda *args: App.change_stepsize(self,10))
        btnstep25 = tk.Button(frame, text='Stepsize 25', command=lambda *args: App.change_stepsize(self,25))
        # btnstep50 = tk.Button(frame, text='Stepsize 50', command=lambda *args: App.change_stepsize(self, 50))

        #zoom buttons
        btnzoomin = tk.Button(frame, text='Zoom in', command=lambda *args: App.zoom_in(self,img1orig, img2orig, frame))
        btnzoomout = tk.Button(frame, text='Zoom out', command=lambda *args: App.zoom_out(self,img1orig, img2orig, frame))
        btnresetzoom = tk.Button(frame, text='Reset', command=lambda *args: App.zoom_reset(self, img1orig, img2orig, frame))

        #match button + slider + text
        btnmatch = tk.Button(frame, text='Automatic Matching', command=lambda *args: App.match(self, img1orig, img2orig, frame))
        matchthresholdslider = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL)
        thresh_label = tk.Label(frame, text="Similarity:")
        matchthresholdslider.set(80)
        matchthreshold = matchthresholdslider.get()/100
        matchstatus = tk.Text(frame, height=1, width=20)
        btnbigger = tk.Button(frame, text='Bigger', command=lambda *args: App.increase_imagesize(self,img1orig, img2orig, frame))
        btnsmaller = tk.Button(frame, text='Smaller', command=lambda *args: App.decrease_imagesize(self,img1orig, img2orig, frame))
        btnresetsize = tk.Button(frame, text='Reset', command=lambda *args: App.reset_imagesize(self, img1orig, img2orig, frame))

        #button settings
        btn1.config(width=20, height=2)
        btn2.config(width=20, height=2)
        btn3.config(width=20, height=2)
        btnup.config(width=5, height=2)
        btndown.config(width=5, height=2)
        btnleft.config(width=5, height=2)
        btnright.config(width=5, height=2)
        btnreset.config(width=5, height=2)
        btnstep1.config(width=8, height=2)
        btnstep10.config(width=8, height=2)
        btnstep25.config(width=8, height=2)
        btnzoomin.config(width=8, height=2)
        btnzoomout.config(width=8, height=2)
        btnresetzoom.config(width=8, height=2)
        btnmatch.config(width=20, height=2)
        matchthresholdslider.config(width=10)
        matchstatus.insert(tk.END, matchtext)
        btnbigger.config(width=8, height=2)
        btnsmaller.config(width=8, height=2)
        btnresetsize.config(width=8, height=2)

        #button locations
        btn1.grid(row=0, column=0, columnspan=3)
        btn2.grid(row=1, column=0, columnspan=3)
        btn3.grid(row=2, column=0, columnspan=3)
        btnstep1.grid(row=6, column=0)
        btnstep10.grid(row=6, column=1)
        btnstep25.grid(row=6, column=2)
 #       btnstep50.grid(row=6, column=3)
        btnup.grid(row=3, column=1)
        btndown.grid(row=5, column=1)
        btnleft.grid(row=4, column=0)
        btnright.grid(row=4, column=2)
        btnreset.grid(row=4, column=1)
        btnzoomin.grid(row=7, column=0)
        btnzoomout.grid(row=7, column=2)
        btnresetzoom.grid(row=7, column=1)
        thresh_label.grid(row=8, column=0)
        matchthresholdslider.grid(row=8, column=1,columnspan=2)
        btnmatch.grid(row=9, column=0, columnspan=3)
        matchstatus.grid(row=10, column=0, columnspan=3)
        btnbigger.grid(row=11, column=0)
        btnsmaller.grid(row=11, column=2)
        btnresetsize.grid(row=11, column=1)
        keyboarduse.grid(row=12, column=0, columnspan=3)

    def activate_keys(self, img1, img2, frame):
        #keyboard hotkeys assign
        if keyboard_active.get():
            keyboard.add_hotkey('+', lambda *args: App.zoom_in(self,img1orig, img2orig, frame))
            keyboard.add_hotkey('-', lambda *args: App.zoom_out(self, img1orig, img2orig, frame))
            keyboard.add_hotkey('a', lambda *args: App.decrease_offset_x(self,img1orig, img2orig, frame))
            keyboard.add_hotkey('d', lambda *args: App.increase_offset_x(self,img1orig, img2orig, frame))
            keyboard.add_hotkey('s', lambda *args: App.decrease_offset_y(self,img1orig, img2orig, frame))
            keyboard.add_hotkey('w', lambda *args: App.increase_offset_y(self,img1orig, img2orig, frame))
        else:
            keyboard.clear_all_hotkeys()

        print(keyboard_active.get())

    def increase_offset_x(self, img1, img2, frame):
        global manual_offset, offset_x, stepsize
        manual_offset = True
        offset_x = offset_x + stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def decrease_offset_x(self, img1, img2, frame):
        global manual_offset, offset_x, stepsize
        manual_offset = True
        offset_x = offset_x - stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def increase_offset_y(self, img1, img2, frame):
        global manual_offset, offset_y, stepsize
        manual_offset = True
        offset_y = offset_y + stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def decrease_offset_y(self, img1, img2, frame):
        global manual_offset, offset_y, stepsize
        manual_offset = True
        offset_y = offset_y - stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def reset_offsets(self,img1, img2, frame):
        global manual_offset
        manual_offset = False
        global offset_y
        offset_y = 0
        global offset_x
        offset_x = 0
        global matched
        matched = False
        img1 = img1.copy()
        img2 = img2.copy()
        App.show_combined(self,img1, img2, frame)

    def change_stepsize(self, size):
        global stepsize
        stepsize = size

    def zoom_in(self, img1, img2, frame):
        global zoom
        zoom = zoom * 1.1
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def zoom_out(self, img1, img2, frame):
        global zoom, img1matched, img2matched
        zoom = zoom / 1.1
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def zoom_reset(self, img1, img2, frame):
        global zoom
        zoom = 1
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def increase_imagesize(self, img1, img2, frame):
        global imagefactor
        imagefactor = imagefactor * 1.1

        image1_window.destroy()
        image2_window.destroy()
        image3_window.destroy()
        image4_window.destroy()

        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def decrease_imagesize(self, img1, img2, frame):
        global imagefactor
        imagefactor = imagefactor / 1.1

        image1_window.destroy()
        image2_window.destroy()
        image3_window.destroy()
        image4_window.destroy()

        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def reset_imagesize(self, img1, img2, frame):
        global imagefactor
        imagefactor = 1

        image1_window.destroy()
        image2_window.destroy()
        image3_window.destroy()
        image4_window.destroy()

        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def resize_and_combine_images(self, image1, image2, frame):
        global manual_offset
        global offset_x, offset_y

        #calc image dimensions
        image1height = image1.shape[0]
        image2height = image2.shape[0]
        image1width = image1.shape[1]
        image2width = image2.shape[1]

        diffheight = image1height - image2height
        diffwidth = image1width - image2width

        img1 = image1.copy()
        img2 = image2.copy()


        #bring images to same size
        if diffheight > 0:
            img2 = cv2.copyMakeBorder(img2, 0, diffheight, 0, 0, cv2.BORDER_REPLICATE)
        else:
            img1 = cv2.copyMakeBorder(img1, 0, abs(diffheight), 0, 0, cv2.BORDER_REPLICATE)
        if diffwidth > 0:
            img2 = cv2.copyMakeBorder(img2, 0, 0, 0, diffwidth, cv2.BORDER_REPLICATE)
        else:
            img1 = cv2.copyMakeBorder(img1, 0, 0, 0, abs(diffwidth), cv2.BORDER_REPLICATE)

        imgheight = img1.shape[0]
        imgwidth = img1.shape[1]

        # cv2.imshow("img1", img1)
        # cv2.imshow("img2", img2)

        #create combined half transparent image

        if offset_x == 0 and offset_y == 0:
            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)

        else:

            img1origheight = img1orig.shape[0]
            img2origheight = img2orig.shape[0]
            img1origwidth = img1orig.shape[0]
            img2origwidth = img2orig.shape[0]

            img1origarea = img1origheight * img1origwidth
            img2origarea = img2origheight * img2origwidth

            if img1origarea > img2origarea:

                if offset_x > 0:
                    img2 = img2[0:imgheight, 0:imgwidth-offset_x]

                    img2 = cv2.copyMakeBorder(img2, 0, 0, offset_x, 0, cv2.BORDER_REPLICATE)
                else:
                    img2 = img2[0:imgheight, abs(offset_x):imgwidth ]

                    img2 = cv2.copyMakeBorder(img2, 0, 0, 0, abs(offset_x), cv2.BORDER_REPLICATE)

                if offset_y > 0:
                    img2 = img2[offset_y:imgheight, 0:imgwidth]

                    img2 = cv2.copyMakeBorder(img2, 0, offset_y, 0, 0, cv2.BORDER_REPLICATE)
                else:
                    img2 = img2[0:imgheight-abs(offset_y), 0:imgwidth]

                    img2 = cv2.copyMakeBorder(img2, abs(offset_y), 0, 0, 0, cv2.BORDER_REPLICATE)

                # cv2.imshow("img1grö0er", img1)
                # cv2.imshow("img2kleiner", img2)

            else:

                if offset_x > 0:
                    img1 = img1[0:imgheight, 0:imgwidth - offset_x]

                    img1 = cv2.copyMakeBorder(img1, 0, 0, offset_x, 0, cv2.BORDER_REPLICATE)
                else:
                    img1 = img1[0:imgheight, abs(offset_x):imgwidth]

                    img1 = cv2.copyMakeBorder(img1, 0, 0, 0, abs(offset_x), cv2.BORDER_REPLICATE)

                if offset_y > 0:
                    img1 = img1[offset_y:imgheight, 0:imgwidth]

                    img1 = cv2.copyMakeBorder(img1, 0, offset_y, 0, 0, cv2.BORDER_REPLICATE)
                else:
                    img1 = img1[0:imgheight - abs(offset_y), 0:imgwidth]

                    img1 = cv2.copyMakeBorder(img1, abs(offset_y), 0, 0, 0, cv2.BORDER_REPLICATE)

                # cv2.imshow("img1kleiner", img1)
                # cv2.imshow("img2größer", img2)

            # cv2.imshow("img1resized", img1)
            # cv2.imshow("img2resized", img2)

            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)



        return img1, img2, combined

    def calc_differences(self, image1, image2, frame):

        resizedimage1, resizedimage2, combined = App.resize_and_combine_images(self,image1, image2, frame)

        img1 = resizedimage1.copy()
        img2 = resizedimage2.copy()

        # convert to gray

        gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

        # find difference

        diff = cv2.absdiff(gray1, gray2)

        # create threshold image

        ret, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY)

        # contour-search

        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # loop over contours for drawing rectangles

        result1 = img1.copy()
        result2 = img2.copy()

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result1, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.rectangle(result2, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return img1, img2, combined, thresh, result1, result2

    def show_combined_unmatch(self, img1, img2, frame):
        global matched, matchtext
        matched=False
        matchtext = "not matched yet"
        App.show_combined(self, img1, img2, frame)

    def show_combined(self, img1, img2, frame):
        global photo1, photo2, photo3, photo4, photo5, photo6, zoom, image1_window, image2_window, image3_window, image4_window, matchtext

        App.set_matchtext(self, matchtext)
        img1, img2, combined = App.resize_and_combine_images(self,img1,img2, frame)

        #change dimension by zoom setting
        dimx = img1.shape[1]
        dimy = img1.shape[0]

        dimx = int(dimx * zoom)
        dimy = int(dimy * zoom)

        newdim = (dimx, dimy)

        #create the 4 different images to be viewed
        img1, img2, combined, thresh, result1, result2 = App.calc_differences(self,img1, img2, frame)

        combined = cv2.resize(combined, newdim)
        thresh = cv2.resize(thresh, newdim)
        result1 = cv2.resize(result1, newdim)
        result2 = cv2.resize(result2, newdim)

        #convert cv2image to photoimage for gui display

        photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(combined))
        photo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(thresh))
        photo3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result1))
        photo4 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result2))

        #create scrollable images

        # def multiple_yview(*args):
        #     image1_window.cnvs.yview(*args)
        #     image2_window.cnvs.yview(*args)
        #     image3_window.cnvs.yview(*args)
        #     image4_window.cnvs.yview(*args)
        #
        # def multiple_xview(*args):
        #     image1_window.cnvs.xview(*args)
        #     image2_window.cnvs.xview(*args)
        #     image3_window.cnvs.xview(*args)
        #     image4_window.cnvs.xview(*args)

        image1_window = App.ScrollableImage(frame, image=photo1, scrollbarwidth=6, width=400*imagefactor, height=300*imagefactor, Label="Combined")
        image1_window.grid(row=0, column=4, rowspan=6, columnspan=8)

        image2_window = App.ScrollableImage(frame, image=photo2, scrollbarwidth=6, width=400*imagefactor, height=300*imagefactor, Label="Binarised diff")
        image2_window.grid(row=0, column=12, rowspan=6, columnspan=8)

        image3_window = App.ScrollableImage(frame, image=photo3, scrollbarwidth=6, width=400*imagefactor, height=300*imagefactor, Label="Diff in Image 1")
        image3_window.grid(row=6, column=4, rowspan=6, columnspan=8)

        image4_window = App.ScrollableImage(frame, image=photo4, scrollbarwidth=6, width=400*imagefactor, height=300*imagefactor, Label="Diff in Image 2")
        image4_window.grid(row=6, column=12, rowspan=6, columnspan=8)

        # image1_window.cnvs.create_image(0, 0, anchor='nw', image=image1_window.image)
        # image1_window.v_scroll = tk.Scrollbar(image1_window, orient='vertical', width=10)
        # image1_window.h_scroll = tk.Scrollbar(image1_window, orient='horizontal', width=10)
        # image1_window.cnvs.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        # image1_window.h_scroll.grid(row=1, column=0, sticky='ew', padx=2, pady=2)
        # image1_window.v_scroll.grid(row=0, column=1, sticky='ns', padx=2, pady=2)
        # image1_window.cnvs.config(xscrollcommand=image1_window.h_scroll.set, yscrollcommand=image1_window.v_scroll.set)
        # image1_window.v_scroll.config(command=image1_window.cnvs.yview())
        # image1_window.h_scroll.config(command=image1_window.cnvs.xview())
        # image1_window.cnvs.config(scrollregion=image1_window.cnvs.bbox('all'))



        # image2_window.cnvs.config(xscrollcommand=image1_window.h_scroll.set, yscrollcommand=image1_window.v_scroll.set)
        # image3_window.cnvs.config(xscrollcommand=image1_window.h_scroll.set, yscrollcommand=image1_window.v_scroll.set)
        # image4_window.cnvs.config(xscrollcommand=image1_window.h_scroll.set, yscrollcommand=image1_window.v_scroll.set)


        # image2_window.v_scroll.config(command=multiple_yview())
        # image2_window.h_scroll.config(command=multiple_xview())
        # image3_window.v_scroll.config(command=multiple_yview())
        # image3_window.h_scroll.config(command=multiple_xview())
        # image4_window.v_scroll.config(command=multiple_yview())
        # image4_window.h_scroll.config(command=multiple_xview())

    def get_Matchthresh(self):
        global matchthresholdslider, matchthreshold
        matchthreshold = matchthresholdslider.get()/100

    def set_matchtext(self, text):
        global matchstatus
        matchstatus.delete(1.0, "end")
        matchstatus.insert(1.0, text)

    def match(self, image1, image2, frame):

        global matchthreshold, photo5, photo6, matched, img1matched, img2matched, matchtext
        match = False
        App.reset_offsets(self, img1orig, img2orig, frame)
        App.get_Matchthresh(self)

        #calc image dimensions
        image1height = image1.shape[0]
        image2height = image2.shape[0]
        image1width = image1.shape[1]
        image2width = image2.shape[1]

        img1matched = image1.copy()
        img2matched = image2.copy()

        img1area = image1height*image1width
        img2area = image2height*image2width

        #check if one image is smaller in both dimensions and then match the smaller image into the bigger one

        if img1area>img2area:

            if image2width<image1width and image2height<image1height:
                result = cv2.matchTemplate(img1matched, img2matched, cv2.TM_CCOEFF_NORMED)
                match = True
            else:
                print('Not matched, Images do not fit')
                matchtext = 'Image 2 not fitting'
                match = False
        else:
            if image1width<image2width and image1height<image2height:
                result = cv2.matchTemplate(img2matched, img1matched, cv2.TM_CCOEFF_NORMED)
                match = True
            else:
                print('Not matched, Images do not fit')
                matchtext = 'Image 1 not fitting'
                match = False

        if match:

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print('Best match top left position: %s' % str(max_loc))
            print('Best match confidence: %s' % max_val)

            if max_val >= matchthreshold:

                print('Match')
                matchtext = 'Match with', str(round(max_val*100, 1)), '%'
                matched = True
                top_left = max_loc

                if img1area > img2area:

                    #bottom_right = (top_left[0] + image2width, top_left[1] + image2height)
                    #cv2.rectangle(img1, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)
                    #cv2.imshow("img1rect",img1)

                    img1matched = img1matched[top_left[1]:top_left[1]+image2height, top_left[0]:top_left[0]+image2width]

                    photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img1matched))

                else:
                    #bottom_right = (top_left[0] + image1width, top_left[1] + image1height)
                    #cv2.rectangle(img2, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)
                    #cv2.imshow("img2rect", img2)

                    img2matched = img2matched[top_left[1]:top_left[1] + image1height, top_left[0]:top_left[0] + image1width]

                    photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img2matched))

                App.show_combined(self, img1matched, img2matched, frame)


            else:
                print('No match')
                matchtext = 'No match'

        App.set_matchtext(self, matchtext)

        # photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img1))
        # canvas5 = tk.Canvas(frame)
        # canvas5.create_image(0, 0, image=photo5, anchor=tk.NW)
        # canvas5.grid(row=12, column=4, rowspan=6, columnspan=8)
        # photo6 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img1))
        # canvas6 = tk.Canvas(frame)
        # canvas6.create_image(0, 0, image=photo6, anchor=tk.NW)
        # canvas6.grid(row=12, column=12, rowspan=6, columnspan=8)

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.geometry("1200x800+300+150")
#     root.title("Image Comparing Tool")
#     root.resizable(width=True, height=True)
#     app = App(root)
#     root.mainloop()


if __name__ == "__main__":

    App().mainloop()



















