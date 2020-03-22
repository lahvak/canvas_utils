"""
This module deals with uploading files to Canvas.
"""

import os.path
import canvas


def upload_file(classid, module, fname, directory, title, position, indent=1):
    """
    Uploads file to Canvas to class given by classid in the given directory.
    Adds a link to the file as an item in the given module, at the given
    position with the given title.
    """

    resp = canvas.upload_file_to_course(classid, fname, directory)
    resp.raise_for_status()

    file_id = resp.json()['id']

    resp = canvas.create_module_item(classid, module, title, position, "File",
                                     indent=indent, content=file_id)
    resp.raise_for_status()

    return resp.json()


def upload_files_from_dict(classid, module, pos, fdict):
    """
    Takes a dict of files info: {filename: [directory, title]} and
    uploads them to Canvas.  Adds links to the module.  Returns dict of
    created items indexed by filenames.
    """

    items = {}

    for fname, props in fdict.items():
        if os.path.isfile(fname):
            items[fname] = [upload_file(classid, module, fname,
                                        props[0], props[1], pos)]
            if not pos is None:
                pos += 1
        else:
            print(fname + " not found")

    return items
