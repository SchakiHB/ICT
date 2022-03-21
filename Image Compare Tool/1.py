import cv2
import imutils
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
from pynput.keyboard import Key, Listener

offset_x=0
offset_y=0
img1orig = cv2.imread("images/img1.png")
img2orig = cv2.imread("images/img2.png")
manual_offset = False
stepsize = 10

def create_img1():
    global img1orig
    img1orig = cv2.imread(filedialog.askopenfilename(title='open'))
    img1orig = cv2.cvtColor(img1orig, cv2.COLOR_BGR2RGB)
   #cv2.imshow("img1", img1orig)

def create_img2():
    global img2orig
    img2orig = cv2.imread(filedialog.askopenfilename(title='open'))
    img2orig = cv2.cvtColor(img2orig, cv2.COLOR_BGR2RGB)
   #cv2.imshow("img2", img2orig)

def increase_offset_x(img1,img2):
    global manual_offset, offset_x, stepsize
    manual_offset = True
    offset_x = offset_x+stepsize
    img1 = img1.copy()
    img2 = img2.copy()
    show_combined(img1, img2)

def decrease_offset_x(img1,img2):
    global manual_offset, offset_x, stepsize
    manual_offset = True
    offset_x=offset_x-stepsize
    img1 = img1.copy()
    img2 = img2.copy()
    show_combined(img1, img2)

def increase_offset_y(img1,img2):
    global manual_offset, offset_y, stepsize
    manual_offset = True
    offset_y=offset_y+stepsize
    img1 = img1.copy()
    img2 = img2.copy()
    show_combined(img1, img2)

def decrease_offset_y(img1,img2):
    global manual_offset, offset_y, stepsize
    manual_offset = True
    offset_y=offset_y-stepsize
    img1 = img1.copy()
    img2 = img2.copy()
    show_combined(img1, img2)

def reset_offsets(img1,img2):
    global manual_offset
    manual_offset = False
    global offset_y
    offset_y=0
    global offset_x
    offset_x=0
    img1 = img1.copy()
    img2 = img2.copy()
    show_combined(img1, img2)

def change_stepsize(size):
    global stepsize
    stepsize=size

def resize_and_combine_images(image1, image2):
    global manual_offset
    global offset_x, offset_y

    img1height = image1.shape[0]
    img2height = image2.shape[0]
    img1width = image1.shape[1]
    img2width = image2.shape[1]

    img1 = image1.copy()
    img2 = image2.copy()

    if manual_offset==False:
        if (img1height==img2height and img1width==img2width):

            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)

        else:

            diffheight = img1height-img2height
            diffwidth = img1width-img2width

            if diffheight > 0:
                img2 = cv2.copyMakeBorder(img2, diffheight, 0, 0, diffwidth, cv2.BORDER_REPLICATE)
            else:
                img1 = cv2.copyMakeBorder(img1, diffheight, 0, 0, diffwidth, cv2.BORDER_REPLICATE)

            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)
    else:
        if (img1height == img2height and img1width == img2width):

            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)

        else:

            diffheight = img1height - img2height
            diffwidth = img1width - img2width

            if diffheight > 0:
                img2 = cv2.copyMakeBorder(img2, diffheight-offset_y, offset_y, offset_x, diffwidth-offset_x, cv2.BORDER_REPLICATE)

            else:
                img1 = cv2.copyMakeBorder(img1, diffheight-offset_y, offset_y, diffwidth-offset_x, offset_x, cv2.BORDER_REPLICATE)
                img2 = cv2.copyMakeBorder(img1, offset_y, -offset_y, -offset_x, offset_x, cv2.BORDER_REPLICATE)

            combined = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)


    return img1, img2, combined

def calc_differences(image1, image2):

    resizedimage1, resizedimage2, combined =resize_and_combine_images(image1, image2)

    img1=resizedimage1.copy()
    img2=resizedimage2.copy()

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
    result1=img1.copy()
    result2=img2.copy()

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(result1, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.rectangle(result2, (x, y), (x + w, y + h), (255, 0, 0), 2)

    return img1, img2, combined, thresh, result1, result2

def show_combined(img1, img2):
    global photo1, photo2, photo3, photo4, photo5, photo6

    img1, img2, combined, thresh, result1, result2 = calc_differences(img1, img2)

    height, width, no_channels = combined.shape
    photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img1))
    canvas1 = tk.Canvas(root, width=width, height=height)
    canvas1.create_image(0, 0, image=photo1, anchor=tk.NW)
    canvas1.grid(row=0, column=4, rowspan=3, columnspan=3)
    photo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img2))
    canvas2 = tk.Canvas(root, width=width, height=height)
    canvas2.create_image(0, 0, image=photo2, anchor=tk.NW)
    canvas2.grid(row=0, column=7, rowspan=3, columnspan=3)
    photo3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(combined))
    canvas3 = tk.Canvas(root, width=width, height=height)
    canvas3.create_image(0, 0, image=photo3, anchor=tk.NW)
    canvas3.grid(row=4, column=4, rowspan=3, columnspan=3)
    photo4 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(thresh))
    canvas4 = tk.Canvas(root, width=width, height=height)
    canvas4.create_image(0, 0, image=photo4, anchor=tk.NW)
    canvas4.grid(row=4, column=7, rowspan=3, columnspan=3)
    photo5 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result1))
    canvas5 = tk.Canvas(root, width=width, height=height)
    canvas5.create_image(0, 0, image=photo5, anchor=tk.NW)
    canvas5.grid(row=7, column=4, rowspan=3, columnspan=3)
    photo6 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(result2))
    canvas6 = tk.Canvas(root, width=width, height=height)
    canvas6.create_image(0, 0, image=photo6, anchor=tk.NW)
    canvas6.grid(row=7, column=7, rowspan=3, columnspan=3)

class App(tk.Frame):

    def __init__(self, *args, **kwargs):
        global img1orig
        global img2orig
        tk.Frame.__init__(self, *args, **kwargs)
        btn1 = tk.Button(text='Load image1', command=create_img1)
        btn2 = tk.Button(text='Load image2', command=create_img2)
        btn3 = tk.Button(root, text="show combined", command=lambda *args: show_combined(img1orig, img2orig))
        btnup = tk.Button(text='up', command=lambda *args: increase_offset_y(img1orig, img2orig))
        btndown = tk.Button(text='down', command=lambda *args: decrease_offset_y(img1orig, img2orig))
        btnright = tk.Button(text='right', command=lambda *args: increase_offset_x(img1orig, img2orig))
        btnleft = tk.Button(text='left', command=lambda *args: decrease_offset_x(img1orig, img2orig))
        btnreset = tk.Button(text='reset', command=lambda *args: reset_offsets(img1orig, img2orig))
        btnstep1 = tk.Button(text='Stepsize 1', command=lambda *args: change_stepsize(1))
        btnstep5 = tk.Button(text='Stepsize 5', command=lambda *args: change_stepsize(5))
        btnstep10 = tk.Button(text='Stepsize 10', command=lambda *args: change_stepsize(10))

        btn1.config(width=20, height=2)
        btn2.config(width=20, height=2)
        btn3.config(width=20, height=2)
        btnup.config(width=5, height=2)
        btndown.config(width=5, height=2)
        btnleft.config(width=5, height=2)
        btnright.config(width=5, height=2)
        btnreset.config(width=5, height=2)
        btnstep1.config(width=20, height=2)
        btnstep5.config(width=20, height=2)
        btnstep10.config(width=20, height=2)

        btn1.grid(row=0, column=1, columnspan=3)
        btn2.grid(row=1, column=1, columnspan=3)
        btn3.grid(row=2, column=1, columnspan=3)
        btnstep1.grid(row=7, column=2)
        btnstep5.grid(row=8, column=2)
        btnstep10.grid(row=9, column=2)
        btnup.grid(row=4, column=2)
        btndown.grid(row=6, column=2)
        btnleft.grid(row=5, column=1)
        btnright.grid(row=5, column=3)
        btnreset.grid(row=5, column=2)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1800x1000+300+150")
    root.title("Image Comparing Tool")
    root.resizable(width=True, height=True)
    app = App(root)
    root.mainloop()



















