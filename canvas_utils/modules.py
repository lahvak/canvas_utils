"""
Module for handling Canvas modules and module items
"""

import datetime
from calendar import month_name
from number_parser import parse_ordinal
from num2words import num2words
import canvas

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
