import urllib.parse, urllib.request, urllib.error, json, sys
from flask import Flask
from flask import render_template, request
from jinja2 import Environment, FileSystemLoader

#TODO:
#   - Secure user token for pushing to GitHub

# BEGIN DISCOGS METHODS (borrowed from HW5 mostly)
import discogs as discogs
user_token = discogs.token

def album_info(search_term):
    base_url = "https://api.discogs.com/database/search?"
    end_params = urllib.parse.urlencode({"q": search_term, "token": user_token})
    req_url = base_url + end_params

    try:
        album_data_str = urllib.request.urlopen(req_url)
        album_data = json.load(album_data_str)
        print("GET album {} from DISCOGS".format(search_term))
        album_data["price_data"] = price_info(album_data["results"][0]["id"])
        return album_data
    except urllib.error.HTTPError as e:
        print("The designated server could not fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We could not reach a server successfully.")
        print("Reason: ", e.reason)

# Print lowest price for a given Discogs Release ID
def price_info(release_id):
    base_url = "https://api.discogs.com/marketplace/stats/" + str(release_id)
    end_params = urllib.parse.urlencode({"curr_abbr": "USD"})
    req_url = base_url + "?" + end_params

    try:
        price_data_str = urllib.request.urlopen(req_url)
        price_data = json.load(price_data_str)
        print("GET {} price from DISCOGS".format(release_id))
        return price_data
    except urllib.error.HTTPError as e:
        raise urllib.error.HTTPError
        #print("The designated server could not fulfill the request.")
        #print("Error code: ", e.code)
    except urllib.error.URLError as e:
        raise urllib.error.URLError
        #print("We could not reach a server successfully.")
        #print("Reason: ", e.reason)

# BEGIN FLASK METHODS
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        form = request.form
        if form['search'].strip() != '':
            try:
                data = album_info(form['search'])
                return render_template('results.html', title=data["results"][0]["title"], year=data["results"][0]["year"],
                    country=data["results"][0]["country"], sale_count=data["price_data"]["num_for_sale"],
                    price=data["price_data"]["lowest_price"]["value"], currency=data["price_data"]["lowest_price"]["currency"],
                    main_url=data["results"][0]["uri"], label=data["results"][0]["label"][0],
                    image_url=data["results"][0]["cover_image"])
            except urllib.error.HTTPError as e:
                return render_template('err.html', msg=str(e))
            except urllib.error.URLError as e:
                return render_template('err.html', msg=str(e))
        else:
            return render_template('err.html', msg="Please enter a search term")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)