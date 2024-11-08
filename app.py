from flask import Flask, render_template, request, jsonify
import requests
import json


app = Flask(__name__)
apikey = "5f9a3694"
def searchfilms(search_text , page=1):
    url = "https://www.omdbapi.com/?s=" + search_text +"&page=" +str( page)+ "&apikey=" + apikey ##todos los urls tienn eso?
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None
    
def getmoviedetails(movie):
    url = "https://www.omdbapi.com/?i=" + movie["imdbID"] + "&apikey=" + apikey
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None

def get_country_flag(fullname):

    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if country_data:
            return country_data[0].get("flags", {}).get("svg", None)
    print(f"Failed to retrieve flag for country code: {fullname}")
    return None

def merge_data_with_flags(filter,page=1):

    filmssearch = searchfilms(filter,page)
    if filmssearch == None:
        return [],0
    moviesdetailswithflags = []
    total=int(filmssearch.get("totalResults", 0))
    print(filmssearch["Search"])
    for movie in filmssearch["Search"]:
         moviedetails = getmoviedetails(movie)
         countriesNames = moviedetails["Country"].split(",")
         countries = []
         print(countriesNames)
         for country in countriesNames:
            countrywithflag = {
                "name": country.strip(),
                "flag": get_country_flag(country.strip())
            }
            countries.append(countrywithflag)
         moviewithflags = {
            "title": moviedetails["Title"],
            "year": moviedetails["Year"],
            "countries": countries
         }
         moviesdetailswithflags.append(moviewithflags)

    return moviesdetailswithflags,total

@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    page = int(request.args.get("page", 1))
    moviess, total= merge_data_with_flags(filter)
    total_pages = (total + 9) // 10
    return render_template("index.html", movies=moviess, filter=filter, current_page=page, total_pages=total_pages)

@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))    

if __name__ == "__main__":
    app.run(debug=True)

