try:
    from Tkinter import Label, Tk, Canvas, Button, Frame
    from ttk import Style
    from tkFont import Font, nametofont
except ImportError:
    from tkinter import Label, Tk, Canvas, Button, Frame
    from tkinter.ttk import Style
    from tkinter.font import Font, nametofont
import numpy as np
from imageio.v3 import imread
from PIL import Image, ImageTk

NUMTOOLS = 8
PALETTE = 'sprites/palette.png'
SIZE = 555
BGCOLOR = '#FBFCFB'  #'#010001'

class mynvspaint:
	def __init__(self, root):
		self.root = root
		self.root.resizable(False, False)
		self.root.title('mynvspaint')
		self.root.iconbitmap('sprites/icon.ico')
		self.root.configure(bg='#757575')
		winw = SIZE
		winh = SIZE+72
		x_ = (self.root.winfo_screenwidth()- winw)//2
		y_ = (self.root.winfo_screenheight()- winw)//2
		self.root.geometry(f'{winw}x{winh}+{x_}+{y_}')
		self.bg_color = BGCOLOR

		self.canvas = Canvas(root, cursor='ul_angle', width=winw,height=winw, bg=self.bg_color, borderwidth=0,highlightthickness=0,bd=0)
		self.canvas.grid(row=0, column=0, columnspan=NUMTOOLS+1)
		self.canvas.bind('<Button-1>', self.start_drawing)
		self.canvas.bind('<B1-Motion>', self.draw)
		self.canvas.bind('<ButtonRelease-1>', self.stop_drawing)
		self.drawn_objects = []

		# Tool icons
		icons_png = imread('sprites/tools.png')
		H = icons_png.shape[0]//3
		self.icon_list = []
		self.iconhover_list = []
		self.iconselected_list = []

		# Generate tool buttons
		self.buttons = []
		for i in range(NUMTOOLS):
			self.icon_list.append(ImageTk.PhotoImage(Image.fromarray( icons_png[0:1*H, H*i:H*(i+1)] )))
			self.iconhover_list.append(ImageTk.PhotoImage(Image.fromarray( icons_png[H:2*H, H*i:H*(i+1)] )))
			self.iconselected_list.append(ImageTk.PhotoImage(Image.fromarray( icons_png[2*H:3*H, H*i:H*(i+1)] )))
			if i == 0:
				self.buttons.append(Button(root, image=self.icon_list[i], command=self.clear, bd=0,borderwidth=0,highlightthickness=0))
			elif i == 1:
				self.buttons.append(Button(root, image=self.icon_list[i], command=self.undo, bd=0,borderwidth=0,highlightthickness=0))
			else:
				self.buttons.append(Button(root, image=self.icon_list[i], command=lambda tid=i:self.set_tool(tid), bd=0,borderwidth=0,highlightthickness=0))
			self.buttons[i].grid(row=1+(i+1)%2, column=i//2+1, columnspan=1)

			self.buttons[i].bind('<Enter>', lambda event, tid=i: self.on_enter(event, tid))
			self.buttons[i].bind('<Leave>', lambda event, tid=i: self.on_leave(event, tid))

		# Initialize default tool
		self.start_x = None
		self.start_y = None
		self.selected_color = '#000000'
		self.selected_tool = 2
		self.buttons[2].config(image=self.iconselected_list[2])
		self.brush_width = 1

		# Convert the palette image to a list of RGB hex code strings
		color_palette = imread(PALETTE, mode='L', pilmode='RGB')

		rgb_list = []
		for y in range(color_palette.shape[0]):
			for x in range(color_palette.shape[1]):
				rgb = '#%02x%02x%02x'%tuple(color_palette[y, x])
				rgb_list.append(rgb)

		# Color selector
		self.colors_frame = Frame(root)
		self.colors_frame.grid(row=1, column=NUMTOOLS, columnspan=color_palette.shape[1], rowspan=2)

		# Create buttons out of colors
		row = 0
		column = 0
		for color in rgb_list:
			color_button = Button(self.colors_frame, bg=color, width=2, command=lambda c=color: self.select_color(c), borderwidth=0, highlightthickness=0, bd=2)
			color_button.grid(row=row, column=column)
			column += 1
			if column == color_palette.shape[1]:
				column = 0
				row += 1

	def set_tool(self, tid):
		self.selected_tool = tid
		self.buttons[tid].config(image=self.iconselected_list[tid])
		for i in sorted(list(set(range(NUMTOOLS)) - {tid, self.selected_tool})):
			self.buttons[i].config(image=self.icon_list[i])
		# self.canvas.config(cursor=tcursor)

	def on_enter(self, event, tid):
		if self.selected_tool == tid:
			self.buttons[tid].config(image=self.iconselected_list[tid])
		else:
			self.buttons[tid].config(image=self.iconhover_list[tid])

	def on_leave(self, event, tid):
		if self.selected_tool == tid:
			self.buttons[tid].config(image=self.iconselected_list[tid])
		else:
			self.buttons[tid].config(image=self.icon_list[tid])

	def select_color(self, color):
		self.selected_color = color

	def clear(self):
		for obj in self.drawn_objects:
			self.canvas.delete(obj)
		self.drawn_objects = []

	def undo(self):
		for _ in range(100):
			if self.drawn_objects:
				last_object = self.drawn_objects.pop()
				self.canvas.delete(last_object)

	def start_drawing(self, event):
		self.start_x = event.x
		self.start_y = event.y
	def stop_drawing(self, event):
		self.start_x = None
		self.start_y = None
	def draw(self, event):
		cur_x = event.x
		cur_y = event.y
		if self.selected_tool == 2:
			self.brush_width = 1
			line = self.canvas.create_line(self.start_x, self.start_y, cur_x, cur_y, fill=self.selected_color, width=self.brush_width)
			self.drawn_objects.append(line)
			self.start_y, self.start_x = cur_y, cur_x
		elif self.selected_tool == 3:
			self.brush_width = 12
			line = self.canvas.create_line(self.start_x, self.start_y, cur_x, cur_y, fill=self.selected_color, width=self.brush_width)
			self.drawn_objects.append(line)
			self.start_y, self.start_x = cur_y, cur_x
		elif self.selected_tool == 4:
			pass
		elif self.selected_tool == 5:
			self.brush_width = 1
			line = self.canvas.create_line(self.start_x, self.start_y, cur_x, cur_y, fill=self.selected_color, width=self.brush_width)
			self.drawn_objects.append(line)
		elif self.selected_tool == 6:
			self.brush_width = 12
			line = self.canvas.create_line(self.start_x, self.start_y, cur_x, cur_y, fill=self.selected_color, width=self.brush_width)
			self.drawn_objects.append(line)
			# self.flood_fill(self.start_x, self.start_y, self.selected_color)

	def save_canvas(self):
		x = self.canvas.winfo_rootx()
		y = self.canvas.winfo_rooty()
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()

		image = Image.new('RGB', (width, height), BGCOLOR)
		draw = ImageDraw.Draw(image)

		# Iterate over the drawn objects and draw them on the image
		for obj in self.drawn_objects:
			coords = self.canvas.coords(obj)
			color = self.canvas.itemcget(obj, "fill")
			width = int(self.canvas.itemcget(obj, "width"))
			draw.line(coords, fill=color, width=width)

		# Save the image as a PNG file
		image.save("canvas.png", "PNG")
		print("Canvas saved as canvas.png")

root = Tk()
app = mynvspaint(root)
root.mainloop()
