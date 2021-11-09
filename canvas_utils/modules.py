"""
Module for handling Canvas modules and module items
"""

import datetime
from calendar import month_name
from number_parser import parse_ordinal
from num2words import num2words
import canvas

# Module items

WWURL = "https://webwork.svsu.edu/webwork2/{}/{}"


class ModuleItem:
    def __init__(self, title, indent=0):
        self.title = title
        self.indent = indent

    def create(self, course, module):
        print("Plain ModuleItem cannot be created!")


class ItemHeader(ModuleItem):
    def create(self, course, module):
        canvas.create_module_item(course, module, self.title, None,
                                  "SubHeader", indent=self.indent)


class ItemFile(ModuleItem):
    def __init__(self, title, fname, indent=0):
        super().__init__(title, indent)
        self.fname = fname

    def create(self, course, module):
        resp = canvas.list_files(course, self.fname)

        # This is really stoopid, it just takes the first file that was found,
        # so if there is more files with the same name, be careful.  Eventually
        # there should be a way to specify a folder TODO

        if not resp:
            print("Creating file item: file ain't there!")
        else:
            fileid = resp[0]['id']
            canvas.create_module_item(course, module, self.title, None,
                                      "File", indent=self.indent,
                                      content=fileid)


class ItemLocalFile(ModuleItem):
    def __init__(self, title, local_file, remote_path,
                 remote_name=None, indent=0):
        super().__init__(title, indent)
        self.local_file = local_file
        self.remote_path = remote_path
        self.remote_name = remote_name

    def create(self, course, module):
        resp = canvas.upload_file_to_course(course, self.local_file,
                                            self.remote_path,
                                            self.remote_name)

        fileid = resp.json()['id']

        canvas.create_module_item(course, module, self.title, None,
                                  "File", indent=self.indent,
                                  content=fileid)


class ItemAssignment(ModuleItem):
    def __init__(self, title, name=None, indent=0):
        super().__init__(title, indent)
        if name is None:
            self.name = title
        else:
            self.name = name

    def create(self, course, module):
        resp = canvas.get_assignments(course, self.name)

        # This is really stoopid, it just takes the first assignment that was
        # found, so if there is more assignments with the same name, ...

        if not resp:
            print("Creating assignment item: assignment ain't there!")
        else:
            assid = resp[0]['id']
            canvas.create_module_item(course, module, self.title, None,
                                      "Assignment", indent=self.indent,
                                      content=assid)


class ItemAssignmentCreate(ModuleItem):
    def __init__(self, title, name=None, markdown_description="",
                 points=0, due_at=None, group=None,
                 submission_types="on_paper", allowed_extensions=None,
                 peer_reviews=False, auto_peer_reviews=False,
                 ext_tool_url=None, ext_tool_new_tab=True,
                 indent=0):
        super().__init__(title, indent)
        if name is None:
            self.name = title
        else:
            self.name = name

        self.markdown_description = markdown_description
        self.points = points
        self.due_at = due_at
        self.group = group
        self.submission_types = submission_types
        self.allowed_extensions = allowed_extensions
        self.peer_reviews = peer_reviews
        self.auto_peer_reviews = auto_peer_reviews
        self.ext_tool_url = ext_tool_url
        self.ext_tool_new_tab = ext_tool_new_tab

    def create(self, course, module):

        groups = canvas.get_assignment_groups(course)
        groupid = groups[0]['id']
        if self.group is not None:
            for group in groups:
                if group['name'] == self.group:
                    groupid = group['id']
                    break

        resp = canvas.create_assignment(
            course, self.name,
            self.markdown_description, self.points,
            self.due_at, groupid,
            submission_types=self.submission_types,
            allowed_extensions=self.allowed_extensions,
            peer_reviews=self.peer_reviews,
            auto_peer_reviews=self.auto_peer_reviews,
            ext_tool_url=self.ext_tool_url,
            ext_tool_new_tab=self.ext_tool_new_tab)

        resp.raise_for_status()
        assid = resp.json()['id']
        canvas.create_module_item(course, module, self.title, None,
                                  "Assignment", indent=self.indent,
                                  content=assid)


class ItemWebworkSet(ModuleItem):
    def __init__(self, title, wwclass, wwset, points, deadline, group=None,
                 name=None, announcement=None, indent=0):
        super().__init__(title, indent)
        self.wwclass = wwclass
        self.wwset = wwset
        self.points = points
        self.deadline = deadline
        self.group = group
        self.announcement = announcement
        if name is None:
            self.name = wwset.replace("_", " ")
        else:
            self.name = name

    def create(self, course, module):
        url = WWURL.format(self.wwclass, self.wwset)

        groups = canvas.get_assignment_groups(course)
        groupid = groups[0]['id']
        if self.group is not None:
            for group in groups:
                if group['name'] == self.group:
                    groupid = group['id']
                    break

        ass = canvas.create_assignment(course, self.name, "WeBWorK",
                                       self.points, self.deadline, groupid,
                                       submission_types="external_tool",
                                       ext_tool_url=url, ext_tool_new_tab=True)
        ass.raise_for_status()
        assid = ass.json()["id"]

        canvas.create_module_item(course, module, self.title, None,
                                  "Assignment", indent=self.indent,
                                  content=assid)

        if self.announcement is not None:
            date = datetime.datetime.strptime(
                self.deadline, "%Y-%m-%dT%H:%M:%S"
            )
            canvas.post_announcement_from_markdown(
                course,
                "Assignment {} posted".format(self.name),
                self.announcement + date.strftime(
                    "\n\n__Due %m/%d/%y at %H:%M__"
                )
            )


class ItemURL(ModuleItem):
    def __init__(self, title, url, indent=0, new_tab=False):
        super().__init__(title, indent)
        self.url = url
        self.new_tab = new_tab

    def create(self, course, module):
        canvas.create_module_item(course, module, self.title, None,
                                  "ExternalUrl", indent=self.indent,
                                  external_url=self.url, new_tab=self.new_tab)


class ItemUtoob(ItemURL):
    def __init__(self, title, movieid, indent=0):
        super().__init__(title, "https://youtu.be/" + movieid,
                         indent=indent, new_tab=True)


class ItemTool(ModuleItem):
    def __init__(self, title, url, indent=0, new_tab=False):
        super().__init__(title, indent)
        self.url = url
        self.new_tab = new_tab

    def create(self, course, module):
        canvas.create_module_item(course, module, self.title, None,
                                  "ExternalTool", indent=self.indent,
                                  external_url=self.url, new_tab=self.new_tab)


# Weekly modules


WEEKLY_MODULE_NAME_FORMAT = "Week of {} {}"


def create_weekly_module(classid, year, month, day):
    """
    Generate a module name from date (must be Monday!) and create the module
    on Canvas.
    """

    if isinstance(month, str):
        mnum = list(month_name).index(month)  # Python hait!
    else:
        mnum = month
    date = datetime.date(year, mnum, day)

    assert date.weekday() == 0, "create_weekly_module: date is not a Monday."

    mname = month_name[mnum]

    # It looks like specifying position as None place the module at the end
    resp = canvas.create_module(classid,
                                WEEKLY_MODULE_NAME_FORMAT.format(mname, day),
                                None)

    resp.raise_for_status()

    return resp.json()['id']


def module_name(year, month, day):
    """
    Generate module name from date.  Modules are named like
    "Week of Month day", where the date is always Monday
    """

    if isinstance(month, str):
        mnum = list(month_name).index(month)  # Python hait!
    else:
        mnum = month
    date = datetime.date(year, mnum, day)
    monday = date - datetime.timedelta(days=date.weekday())

    mday = monday.day
    mmonth = month_name[monday.month]

    return WEEKLY_MODULE_NAME_FORMAT.format(mmonth, mday)


# Ordinal modules ("First class", ...)

def drop_last_iter(lst):
    """Keep removing last item from l while it is nonempty"""
    while lst:
        yield lst
        lst = lst[0:-1]


def get_ordinal_from_name(name):
    """Gets a name like 'Second class' and translates it into int"""

    words = name.split()

    for sublist in drop_last_iter(words):
        parsed = parse_ordinal(" ".join(sublist))
        if not (parsed is None):
            return parsed

    return None


def get_last_ordinal_module_number(classid):
    """
    Returns the number corresponding to the last ordinal module.
    """

    mlist = canvas.list_modules(classid)

    numbers = [n for n in (get_ordinal_from_name(mod['name']) for mod in mlist)
               if not (n is None)]

    if numbers:
        return max(numbers)

    return 0


def ordinal_module_name(number, suffix="class"):
    """
    Generates a name of an ordinal module, given its number.
    """

    return num2words(number, "ordinal").capitalize() + " " + suffix


def create_next_ordinal_module(classid, suffix="class"):
    """
    Generate a module name for the next ordinal module in class and create the
    module on Canvas.  Returns the module id.
    """

    lastmod = get_last_ordinal_module_number(classid)

    name = ordinal_module_name(lastmod + 1, suffix=suffix)

    # It looks like specifying position as None place the module at the end
    resp = canvas.create_module(classid, name, None)

    resp.raise_for_status()

    return resp.json()['id']


def get_module_id(classid, name):
    """
    Gets the module id of a first module matching the given name, or None
    if none exists.
    """

    mlist = canvas.list_modules(classid, search=name)

    if mlist:
        return mlist[0]['id']

    return None


def find_item_position(classid, module, partial_name):
    """
    Gets the position of a first item matching the given name, or
    the total number of items in the module, if there is no match.
    """

    itlist = canvas.list_module_items(classid, module, search=partial_name)

    if not itlist:
        return len(canvas.list_module_items(classid, module))

    return itlist[0]['position']


def add_text_header(classid, module, text, position=None, indent=0):
    """
    Add a quick text header.
    """

    resp = canvas.create_module_item(classid, module, text, position,
                                     "SubHeader", indent)

    resp.raise_for_status()

    return resp.json()
