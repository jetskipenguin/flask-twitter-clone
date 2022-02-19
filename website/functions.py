from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
import os

# checks to see if file is valid and returns valid filename if needed
def allowed_image(filename, filesize, filepath, replace=False):
    # create filepath if it doesn't exist
    if not os.path.exists(filepath):
        print("Filepath does not exist")
        print("Creating...", filepath)
        os.mkdir(filepath)

    # Check if filename is empty
    if filename == "":
        flash("Invalid filetype")
        return None

    # Check if valid file
    if '.' not in filename:
        flash("Invalid file")
        return None

    # Check if valid file type
    N = filename.find('.')
    filetype = filename[N :]
    if filetype not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        flash("Not an allowed filetype")
        return None

    # Check if valid filesize
    if int(filesize) > current_app.config['ALLOWED_IMAGE_SIZE']:
        flash("Filesize too large")
        return None

    # Check for duplicate file names
    if replace == False:
        revised_filename = filename
        count = 1

        # TODO: this doesnt work correctly with long file names
        directory_contents = os.listdir(filepath)
        if filename in directory_contents:
                while revised_filename in directory_contents:
                    N = filename.find('.')
                    revised_filename = filename[ : N] + '({})'.format(count) + filename[N :]
                    count += 1        
        return revised_filename

    else:
        return filename

def save_image(directory, filename, image):
    image.save(os.path.join(directory, filename))