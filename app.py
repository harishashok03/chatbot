from flask import Flask, render_template, request, jsonify
import csv
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Load data from your dataset 
def load_dataset(file_path):
    dataset = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            country_name = row['Countryname']
            dataset[country_name.lower()] = {key.lower(): value for key, value in row.items()}
    return dataset

csv_file_path = 'countries.csv'

dataset = load_dataset(csv_file_path)

valid_fields = dataset[next(iter(dataset))].keys()

def find_matching_country(user_input, dataset):
    country_name_scores = {country: fuzz.partial_ratio(user_input, country) for country in dataset.keys()}
    best_match = max(country_name_scores, key=country_name_scores.get)
    return best_match

def extract_country_and_field(user_input):
    for field in valid_fields:
        if field in user_input:
            country_name = user_input.replace(field, '').strip()
            return country_name, field
    return None, None

def generate_country_info_response(user_input, dataset, valid_fields):
    if any(greeting in user_input.lower() for greeting in ['hi', 'hello', 'hey', 'hai']):
        response = "Hello! How can I help you? Please provide the country name and required data"
    elif "who are you" in user_input.lower():
        response = "I'm the Country Bot. Ask me about Population, Gdp, Literacy, Birthrate, Deathrate, Area, Currency, Capital."
    else:
        country_name, field = extract_country_and_field(user_input)

        if country_name and field:
            country_name = find_matching_country(country_name.lower(), dataset)
            if country_name in dataset:
                field = field.lower()
                if field in valid_fields:
                    value = dataset[country_name][field]
                    response = f"The {field} of {country_name} is {value}."
                else:
                    response = f"I don't have information for {field}. Valid fields are: {', '.join(valid_fields)}"
            else:
                response = f"I don't have information for {country_name}. Please enter a valid country name."
        else:
            response = "You can ask me about Population, Gdp, Literacy, Birthrate, Deathrate, Area, Currency, Capital."

    return response

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    response = generate_country_info_response(user_input, dataset, valid_fields)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run()
