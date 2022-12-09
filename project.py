from tkinter import *
import tkinter.filedialog

import numpy as np
import cv2

window=Tk()

# Get the picture's loc 
def prompt_file():
    global image_loc
    image_loc = tkinter.filedialog.askopenfilename(parent=window, filetypes=[("Jpg Files", "*.jpg")])

# Main counting and processing to output
def process_image():
    global image_loc

    # If no image is selected yet, ask user to select one
    while image_loc == '':
        prompt_file()

    image = cv2.imread(image_loc)
    
    # Covering the micrometer
    start_point = (3376,1970)
    end_point = (3730, 2070)
    image = cv2.rectangle(image, start_point, end_point, (255,255,255), -1)

    # Adjusting brightness and contast
    contrast = 1.083
    brightness = 0 
    image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

    output = image.copy()
    
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

    # Dark Pollens
    lower_dark = np.array([44,44,44])
    upper_dark = np.array([85,85,85])

    dark_mask=cv2.inRange(img_rgb,lower_dark,upper_dark)
    dark_kern = np.ones((1, 1), "uint8")

    dark_part = cv2.dilate(dark_mask, dark_kern)
    
    # Improve the edges
    dark_part = cv2.medianBlur(dark_part,1)

    # Count the dark pollens
    dark_circles = cv2.HoughCircles(dark_part,cv2.HOUGH_GRADIENT,1,40,
                        param1=40,param2=13,minRadius=25,maxRadius=50)
    
    count_dark_pollens = len(dark_circles[0])

    # All Pollens
    all_circles = cv2.HoughCircles(img_hsv,cv2.HOUGH_GRADIENT,1,45,
                        param1=55,param2=14,minRadius=25,maxRadius=50)

    # [DEBUG] Uncomment this part to display all the pollens found
    # all_circles = np.uint16(np.around(all_circles))
    # for i in all_circles[0,:]:
    #     # draw the outer circle
    #     cv2.circle(output,(i[0],i[1]),i[2],(0,255,0),2)
    #     # draw the center of the circle
    #     cv2.circle(output,(i[0],i[1]),2,(0,0,255),3)
    # cv2.imwrite("target.jpg", output)

    count_all_pollens = len(all_circles[0])
    count_light_pollens = count_all_pollens-count_dark_pollens

    # Displaying Results in a new window
    new= Toplevel(window)
    new.geometry("300x150")
    new.title("Results")
    Label(new, text="Dark Pollens: "+str(count_dark_pollens)+"\nLight Pollens: "+str(count_light_pollens), font=('Helvetica 17 bold')).pack(pady=30)
    outputbtn = Button(new, text="Output to Txt File", fg='red', command=output_prep(count_light_pollens,count_dark_pollens))
    outputbtn.place(x=80, y=100)


def output_prep(light,dark):
    
    file = open('output.txt', 'w')
    file.writelines("Light Pollens: "+str(light)+"\nDark Pollens: "+str(dark))
    file.close()

# UI Things

window.title('CMSC 165 - Group 4: Team Work')
window.geometry("300x200+10+20")

btn=Button(window, text="Select Picture", fg='blue', command=prompt_file)
btn.place(x=80, y=50)


btn2=Button(window, text="Count Pollens", fg='red', command=process_image)
btn2.place(x=80, y=100)

global image_loc
image_loc = ''

window.mainloop()