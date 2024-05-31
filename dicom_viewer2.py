import tkinter as tk
from tkinter import ttk, filedialog
import os
import pydicom
from PIL import Image, ImageTk

class DICOMApp:
    def __init__(self, master):
        self.master = master
        self.master.title("DICOM Viewer")
        self.master.geometry("1200x1000")
        self.current_folder = ''  # Initialize the current folder path

        # Create top pane for open folder button
        self.top_frame = ttk.Frame(self.master)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.open_folder_btn = ttk.Button(self.top_frame, text="Open Folder", command=self.open_folder)
        self.open_folder_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Create left pane for treeview with scrollbar
        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.folder_tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set, selectmode="browse")
        self.folder_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.folder_tree.yview)
        self.folder_tree.bind('<<TreeviewSelect>>', self.show_image)

        # Create right pane for displaying DICOM images on a canvas and metadata
        self.image_frame = ttk.Frame(self.master)
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.image_frame, bg='black')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.metadata_label = ttk.Label(self.image_frame, text="", wraplength=500)
        self.metadata_label.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

    def open_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.current_folder = folder_selected  # Store the selected folder path
            self.populate_treeview(folder_selected)

    def populate_treeview(self, folder_path):
        self.folder_tree.delete(*self.folder_tree.get_children())
        for root, dirs, files in os.walk(folder_path):
            rel_path = os.path.relpath(root, folder_path)
            parent = '' if rel_path == '.' else self.folder_tree.insert('', 'end', text=rel_path, open=True)
            for file in files:
                if file.endswith('.dcm'):
                    self.folder_tree.insert(parent, 'end', text=file, open=False)

    def show_image(self, event):
        try:
            selected_item = self.folder_tree.selection()[0]
            rel_path = self.folder_tree.item(selected_item, 'text')
            file_path = os.path.join(self.current_folder, rel_path)  # Corrected file path
            dicom_file = pydicom.dcmread(file_path)
            image_data = dicom_file.pixel_array

            # Adjust these values or extract from DICOM metadata if available
            window_width = getattr(dicom_file, 'WindowWidth', 400)
            window_center = getattr(dicom_file, 'WindowCenter', 200)

            image_data_windowed = self.apply_windowing(image_data, window_width, window_center)
            pil_image = Image.fromarray(image_data_windowed)
            self.display_image(pil_image)

            # Display metadata
            metadata = f"Patient Name: {dicom_file.PatientName}\nID: {dicom_file.PatientID}\nStudy Date: {dicom_file.StudyDate}\nModality: {dicom_file.Modality}"
            self.metadata_label.config(text=metadata)
        except Exception as e:
            print(f"Error displaying DICOM image: {e}")
            self.metadata_label.config(text="Error displaying DICOM image.")

    def apply_windowing(self, image_data, window_width, window_center):
        lower_bound = window_center - window_width / 2
        upper_bound = window_center + window_width / 2
        image_data = (image_data - lower_bound) / (upper_bound - lower_bound) * 255.0
        image_data[image_data < 0] = 0
        image_data[image_data > 255] = 255
        return image_data.astype('uint8')

    def display_image(self, image):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

def main():
    root = tk.Tk()
    app = DICOMApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    

    
