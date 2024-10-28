
import locale
from datetime import datetime
import os

import roman
from quart import Quart, render_template, request, send_from_directory

from response import get_user, get_groups, get_group, get_students, get_duties
from utils import formatted_full_name

app = Quart(__name__, template_folder='./templates', static_url_path='/static', static_folder='static')
MEDIA_FOLDER = os.path.join(app.root_path, 'media')

@app.route('/profile')
async def profile():
    username = request.args.get('username')
    token = request.args.get('token')
    
    status, user = await get_user(username, token)

    locale.setlocale(locale.LC_TIME, 'Russian')
    created_at = user["created_at"]
    date_object  = datetime.fromisoformat(created_at)
    user["created_at"] = date_object.strftime("%d %B %Yг.")

    context = {
        "user": user,
    }

    if user["group_id"]:
        status, group = await get_group(token)
        group["course_number_roman"] = roman.toRoman(group["course_number"])
        created_at = group["created_at"]
        date_object  = datetime.fromisoformat(created_at)
        group["created_at"] = date_object.strftime("%d %B %Yг.")
        context["group"] = group

    if user["role"] == "Студент":
        status, duties = await get_duties(token)
        context["duties"] = duties

    elif user["role"] == "Староста":
        status, students = await get_students(token)
        context["students"] = students

    elif user["role"] == "Администратор":
        status, groups = await get_groups(token)
        context["groups"] = groups
        groups_list = []
        for group in groups:
            created_at = group["created_at"]
            date_object  = datetime.fromisoformat(created_at)
            group["created_at"] = date_object.strftime("%d %B %Yг.")
            group["creator"] = await formatted_full_name(group["creator"]["full_name"])
            groups_list.append(group)
        groups = groups_list

    templates = {
        "Администратор": "adminProfile.html",
        "Староста": "elderProfile.html",
        "Студент": "studentProfile.html"
    }

    return await render_template(templates[user["role"]], **context)

@app.route('/media/<path:filename>')
async def media(filename):
    return await send_from_directory(MEDIA_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)