import sys
import os
import locale
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from quart import Quart, render_template, request
import aiohttp
from config import API_URL


app = Quart(__name__, template_folder='.', static_url_path='/media', static_folder='media')

@app.route('/profile')
async def profile():
    username = request.args.get('username')
    token = request.args.get('token')

    print(username, token)

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_URL}user/@{username}", headers={"Authorization": f"Bearer {token}"}
        ) as response:
            if response.status == 200:
                user_data = await response.json()
                locale.setlocale(locale.LC_TIME, 'Russian')
                created_at = user_data["created_at"]
                date_object  = datetime.fromisoformat(created_at)
                user_data["created_at"] = date_object.strftime("%d %B %Yг.")
                return await render_template('index.html', user=user_data)
            else:
                return {"error": "User not found"}, response.status

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)