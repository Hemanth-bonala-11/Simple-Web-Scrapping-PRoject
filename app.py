from flask import Flask, render_template, request, jsonify
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs
import requests
from flask_cors import CORS, cross_origin
import pandas as pd
app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    try:
        return render_template("index.html")
    except Exception as e:
        return render_template("error.html")


@app.route('/review', methods=['GET', 'POST'])
@cross_origin()
def index():
    if request.method == "POST":
        try:
            search_string = request.form['productName']
            search_string=search_string.replace(" ","")
            flipkart_url = "https://flipkart.com/search?q=" + search_string
            uClient = uReq(flipkart_url)
            flipkart_html_code = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_html_code, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            product_url = "http://flipkart.com" + box.div.div.div.a["href"]
            product_result = requests.get(product_url)
            # product_result.encoding('utf-8')
            product_html = bs(product_result.text, "html.parser")
            comment_boxes = product_html.find_all('div', {'class': "_16PBlm"})
            filename = search_string + ".csv"
            # fp = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            # fp.write(headers)
            reviews = []
            for commentbox in comment_boxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except Exception as e:
                    name = "anonymous"
                try:
                    rating = commentbox.div.div.div.find_all('div', {'class': '_3LWZlK _1BLPMq'})[0].text
                except Exception as e:
                    rating = "No rating"
                try:
                    comment_heading = commentbox.div.div.find_all('p', {'class': '_2-N8zT'})[0].text
                except Exception as e:
                    comment_heading = "No heading"
                try:
                    cust_comment = commentbox.div.div.find_all('div', {'class': 't-ZTKy'})[0].text
                except Exception as e:
                    cust_comment = "No comment"

                my_dict = {"product": search_string, "name": name, "rating": rating,
                           "heading": comment_heading, "comment": cust_comment}
                reviews.append(my_dict)
                df=pd.DataFrame(reviews)
                df.to_csv(filename,index=False)

            return render_template('result.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            return render_template('error.html')
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
