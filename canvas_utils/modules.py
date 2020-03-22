"""
Module for handling Canvas modules and module items
"""

import datetime
from calendar import month_name
import canvas


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
    resp = canvas.create_module(classid, "{} {}".format(mname, day), None)

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

    return "Week of {} {}".format(mmonth, mday)


def get_module_id(classid, name):
    """
    Gets the module id of a first module matching the given name, or None
    if none exists.
    """

    mlist = canvas.list_modules(classid, name)

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
