from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from random import choice
import requests
import json
import os

app = Flask(__name__)
Bootstrap(app)


def get_place_id(api_key, address):
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/" \
          "json?input={}&inputtype=textquery&fields=place_id&key={}"
    request_url = url.format(address, api_key)
    res = requests.get(request_url)
    res_dict = json.loads(res.text)
    if "candidates" in res_dict:
        return res_dict["candidates"][0]["place_id"]
    else:
        print("Could not find a place id.")
        return None


def get_place_details(api_key, place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/" \
          "json?place_id={}&fields=formatted_address,name,url,editorial_summary,photo&key={}"
    request_url = url.format(place_id, api_key)
    res = requests.get(request_url)
    res_dict = json.loads(res.text)
    if "result" in res_dict:
        return res_dict["result"]
    else:
        print("Could not find place details.")
        return None


def get_image(api_key, photo_ref, max_width=400):
    url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth={}&photoreference={}&key={}"
    request_url = url.format(max_width, photo_ref, api_key)
    return request_url  # This is an URL from which the photo can be downloaded


def format_phone_number(phone_number):
    cleaned = ''.join(filter(str.isdigit, phone_number))
    formatted = "({}) {}-{}".format(cleaned[0:3], cleaned[3:6], cleaned[6:])
    return formatted


api_key = os.environ.get("SECRET_KEY")
random_endpoint = "https://api.openbrewerydb.org/v1/breweries/random"
random_image = [
    "carlos-blanco-WzPdP9pn7go-unsplash.jpg",
    "nick-hillier-xBXF9pr6LQo-unsplash.jpg",
    "alexander-kovacs-kufY1HyGEO8-unsplash.jpg",
    "growth-co-3LRGswD7hD4-unsplash.jpg",
    "louis-hansel-JeHC4yA5PNw-unsplash.jpg",
    "patrick-tomasso-GXXYkSwndP4-unsplash.jpg",
]


@app.route("/")
def home():
    getting_location = True
    while getting_location:
        call = requests.get(random_endpoint)
        response = call.json()[0]
        try:
            clean_phone = format_phone_number(response["phone"])
        except TypeError:
            clean_phone = None
        address = f"{response['name']} {response['address_1']} {response['city']}, {response['state_province']} " \
                  f"{response['postal_code']}"
        image_url = f"/static/{choice(random_image)}"
        try:
            place_id = get_place_id(api_key, address)
        except IndexError:
            pass
        else:
            getting_location = False
            editorial_summary = ""
            google_url = None
            if place_id:
                details = get_place_details(api_key, place_id)
                if details and "photos" in details:
                    if "editorial_summary" in details:
                        editorial_summary = details['editorial_summary']['overview']
                    photo_ref = details["photos"][0]["photo_reference"]
                    image_url = get_image(api_key, photo_ref)
                    if "url" in details:
                        google_url = details['url']
    return render_template("index.html", brewery=response, image=image_url, description=editorial_summary,
                           url=google_url, phone=clean_phone)


if __name__ == "__main__":
    app.run(debug=True)
