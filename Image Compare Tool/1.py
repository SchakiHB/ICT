import cv2
import imutils
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
from functools import partial
# from pynput.keyboard import Key, Listener
zoom=1
offset_x=0
offset_y=0
matchthreshold = 0.7
manual_offset = False
stepsize = 10
matched=False
matchtext="not matched"
img1matched=cv2.imread("images/img1.png")
img2matched=cv2.imread("images/img1.png")

global img1orig
global img2orig


def create_img1():
    global img1orig
    img1orig = cv2.imread(filedialog.askopenfilename(title='open'))
    img1orig = cv2.cvtColor(img1orig, cv2.COLOR_BGR2RGB)


def create_img2():
    global img2orig
    img2orig = cv2.imread(filedialog.askopenfilename(title='open'))
    img2orig = cv2.cvtColor(img2orig, cv2.COLOR_BGR2RGB)


class ScrollbarFrame(tk.Frame):
    """
    Extends class tk.Frame to support a scrollable Frame
    This class is independent from the widgets to be scrolled and
    can be used to replace a standard tk.Frame
    """
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        # The Scrollbar, layout to the right
        vsb = tk.Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)

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

    def __init__(self, *args, **kwargs):
        global img1orig,img2orig, matchthreshold, matchthresholdslider, matchtext, matchstatus

        # tk.Frame.__init__(self, *args, **kwargs)
        super().__init__()

        sbf = ScrollbarFrame(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        sbf.grid(row=0, column=0, sticky='nsew')
        # sbf.pack(side="top", fill="both", expand=True)
        self.title("Image Compare Tool")
        # Some data, layout into the sbf.scrolled_frame
        frame = sbf.scrolled_frame

        btn1 = tk.Button(frame, text='Load image1', command=create_img1)
        btn2 = tk.Button(frame, text='Load image2', command=create_img2)
        btn3 = tk.Button(frame, text="show combined", command=lambda *args: App.show_combined_unmatch(self,img1orig, img2orig,frame))
        btnup = tk.Button(frame, text='up', command=lambda *args: App.increase_offset_y(self,img1orig, img2orig, frame))
        btndown = tk.Button(frame, text='down', command=lambda *args: App.decrease_offset_y(self,img1orig, img2orig, frame))
        btnright = tk.Button(frame, text='right', command=lambda *args: App.increase_offset_x(self,img1orig, img2orig, frame))
        btnleft = tk.Button(frame, text='left', command=lambda *args: App.decrease_offset_x(self,img1orig, img2orig, frame))
        btnreset = tk.Button(frame, text='reset', command=lambda *args: App.reset_offsets(self,img1orig, img2orig, frame))
        btnstep1 = tk.Button(frame, text='Stepsize 1', command=lambda *args: App.change_stepsize(self,1))
        btnstep5 = tk.Button(frame, text='Stepsize 5', command=lambda *args: App.change_stepsize(self,5))
        btnstep10 = tk.Button(frame, text='Stepsize 10', command=lambda *args: App.change_stepsize(self,10))
        btnzoomin = tk.Button(frame, text='Zoom in', command=lambda *args: App.zoom_in(self,img1orig, img2orig, frame))
        btnzoomout = tk.Button(frame, text='Zoom out', command=lambda *args: App.zoom_out(self,img1orig, img2orig, frame))
        btnmatch = tk.Button(frame, text='Match', command=lambda *args: App.match(self, img1orig, img2orig, frame))
        matchthresholdslider = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL)
        matchthresholdslider.set(80)
        matchthreshold = matchthresholdslider.get()/100
        matchstatus = tk.Text(frame, height=1, width=15)

        btn1.config(width=20, height=2)
        btn2.config(width=20, height=2)
        btn3.config(width=20, height=2)
        btnup.config(width=5, height=2)
        btndown.config(width=5, height=2)
        btnleft.config(width=5, height=2)
        btnright.config(width=5, height=2)
        btnreset.config(width=5, height=2)
        btnstep1.config(width=8, height=2)
        btnstep5.config(width=8, height=2)
        btnstep10.config(width=8, height=2)
        btnzoomin.config(width=8, height=2)
        btnzoomout.config(width=8, height=2)
        btnmatch.config(width=8, height=2)
        matchthresholdslider.config(width=10)
        matchstatus.insert(tk.END, matchtext)

        btn1.grid(row=0, column=1, columnspan=3)
        btn2.grid(row=1, column=1, columnspan=3)
        btn3.grid(row=2, column=1, columnspan=3)
        btnstep1.grid(row=6, column=1)
        btnstep5.grid(row=6, column=2)
        btnstep10.grid(row=6, column=3)
        btnup.grid(row=3, column=2)
        btndown.grid(row=5, column=2)
        btnleft.grid(row=4, column=1)
        btnright.grid(row=4, column=3)
        btnreset.grid(row=4, column=2)
        btnzoomin.grid(row=7, column=1)
        btnzoomout.grid(row=7, column=3)
        matchthresholdslider.grid(row=8, column=2)
        btnmatch.grid(row=9, column=2)
        matchstatus.grid(row=10, column=2)

    def increase_offset_x(self,img1, img2, frame):
        global manual_offset, offset_x, stepsize
        manual_offset = True
        offset_x = offset_x + stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def decrease_offset_x(self,img1, img2, frame):
        global manual_offset, offset_x, stepsize
        manual_offset = True
        offset_x = offset_x - stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def increase_offset_y(self,img1, img2, frame):
        global manual_offset, offset_y, stepsize
        manual_offset = True
        offset_y = offset_y + stepsize
        img1 = img1.copy()
        img2 = img2.copy()
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self, img1, img2, frame)

    def decrease_offset_y(self,img1, img2, frame):
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
        img1 = img1.copy()
        img2 = img2.copy()
        App.show_combined(self,img1, img2, frame)

    def change_stepsize(self,size):
        global stepsize
        stepsize = size

    def zoom_in(self,img1, img2, frame):
        global zoom
        zoom = zoom * 1.1
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def zoom_out(self,img1, img2, frame):
        global zoom, img1matched, img2matched
        zoom = zoom / 1.1
        if matched:
            App.show_combined(self, img1matched, img2matched, frame)
        else:
            App.show_combined(self,img1, img2, frame)

    def resize_and_combine_images(self, image1, image2, frame):
        global manual_offset
        global offset_x, offset_y

        image1height = image1.shape[0]
        image2height = image2.shape[0]
        image1width = image1.shape[1]
        image2width = image2.shape[1]

        img1 = image1.copy()
        img2 = image2.copy()

        diffheight = image1height - image2height
        diffwidth = image1width - image2width

        if diffheight > 0:
            img2 = cv2.copyMakeBorder(img2, diffheight, 0, 0, 0, cv2.BORDER_REPLICATE)
        else:
            img1 = cv2.copyMakeBorder(img1, abs(diffheight), 0, 0, 0, cv2.BORDER_REPLICATE)
        if diffwidth > 0:
            img2 = cv2.copyMakeBorder(img2, 0, 0, diffwidth, 0, cv2.BORDER_REPLICATE)
        else:
            img1 = cv2.copyMakeBorder(img1, 0, 0, abs(diffwidth), 0, cv2.BORDER_REPLICATE)

        imgheight = img1.shape[0]
        imgwidth = img1.shape[1]

        # cv2.imshow("img1", img1)
        # cv2.imshow("img2", img2)

        if offset_x == 0 and offset_y == 0:
            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)

        else:


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

            # cv2.imshow("img1resized", img1)
            # cv2.imshow("img2resized", img2)

            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)


        return img1, img2, combined

    def calc_differences(self,image1, image2, frame):

        resizedimage1, resizedimage2, combined = App.resize_and_combine_images(self,image1, image2, frame)

        img1 = resizedimage1.copy()
        img2 = resizedimage2.copy()

        # convert to gray

        gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

        # Find difference

        diff = cv2.absdiff(gray1, gray2)

        # Threshold

        ret, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY)

        # contour-search

        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # Loop over contours for drawing rectangles
        result1 = img1.copy()
        result2 = img2.copy()

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result1, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.rectangle(result2, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return img1, img2, combined, thresh, result1, result2

    def show_combined_unmatch(self, img1, img2, frame):
        global matched
        matched=False
        App.show_combined(self, img1, img2, frame)

    def show_combined(self,img1, img2, frame):
        global photo1, photo2, photo3, photo4, photo5, photo6, zoom
        dimx = img1.shape[1]
        dimy = img1.shape[0]
        dimx = int(dimx * zoom)
        dimy = int(dimy * zoom)

        newdim = (dimx, dimy)

        img1, img2, combined, thresh, result1, result2 = App.calc_differences(self,img1, img2, frame)
        img1 = cv2.resize(img1, newdim)
        img2 = cv2.resize(img2, newdim)
        combined = cv2.resize(combined, newdim)
        thresh = cv2.resize(thresh, newdim)
        result1 = cv2.resize(result1, newdim)
        result2 = cv2.resize(result2, newdim)

        height, width, no_channels = combined.shape
        width = 250
        height = 250
        photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(combined))
        canvas1 = tk.Canvas(frame)
        canvas1.create_image(0, 0, image=photo1, anchor=tk.NW)
        canvas1.grid(row=0, column=4, rowspan=6, columnspan=8)
        photo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(thresh))
        canvas2 = tk.Canvas(frame)
        canvas2.create_image(0, 0, image=photo2, anchor=tk.NW)
        canvas2.grid(row=0, column=12, rowspan=6, columnspan=8)
        photo3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result1))
        canvas3 = tk.Canvas(frame)
        canvas3.create_image(0, 0, image=photo3, anchor=tk.NW)
        canvas3.grid(row=6, column=4, rowspan=6, columnspan=8)
        photo4 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result2))
        canvas4 = tk.Canvas(frame)
        canvas4.create_image(0, 0, image=photo4, anchor=tk.NW)
        canvas4.grid(row=6, column=12, rowspan=6, columnspan=8)
        # photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result1))
        # canvas5 = tk.Canvas(frame)
        # canvas5.create_image(0, 0, image=photo5, anchor=tk.NW)
        # canvas5.grid(row=7, column=4, rowspan=3, columnspan=3)
        # photo6 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result2))
        # canvas6 = tk.Canvas(frame)
        # canvas6.create_image(0, 0, image=photo6, anchor=tk.NW)
        # canvas6.grid(row=7, column=7, rowspan=3, columnspan=3)

    def get_Matchthresh(self):
        global matchthresholdslider, matchthreshold
        matchthreshold = matchthresholdslider.get()/100

    def set_matchtext(self, text):
        global matchstatus
        matchstatus.delete(1.0, "end")
        matchstatus.insert(1.0, text)

    def match(self, image1, image2, frame):

        global matchthreshold, photo5, photo6, matched, img1matched, img2matched, matchtext
        App.reset_offsets(self, img1orig, img2orig, frame)
        App.get_Matchthresh(self)

        image1height = image1.shape[0]
        image2height = image2.shape[0]
        image1width = image1.shape[1]
        image2width = image2.shape[1]

        img1matched = image1.copy()
        img2matched = image2.copy()

        img1area = image1height*image1width
        img2area = image2height*image2width

        if img1area>img2area:

            result = cv2.matchTemplate(img1matched, img2matched, cv2.TM_CCOEFF_NORMED)

        else:

            result = cv2.matchTemplate(img2matched, img1matched, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print('Best match top left position: %s' % str(max_loc))
        print('Best match confidence: %s' % max_val)

        if max_val >= matchthreshold:

            print('Match')
            matchtext='Match'

            top_left = max_loc

            if img1area > img2area:

                bottom_right = (top_left[0] + image2width, top_left[1] + image2height)
                #cv2.rectangle(img1, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)
                #cv2.imshow("img1rect",img1)
                img1matched = img1matched[top_left[1]:top_left[1]+image2height, top_left[0]:top_left[0]+image2width]

                photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img1matched))

            else:
                bottom_right = (top_left[0] + image1width, top_left[1] + image1height)
                #cv2.rectangle(img2, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)
                #cv2.imshow("img2rect", img2)
                img2matched = img2matched[top_left[1]:top_left[1] + image1height, top_left[0]:top_left[0] + image1width]


                photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img2matched))

            matched=True

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



















