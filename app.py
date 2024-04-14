from flask import Flask, render_template, request

import model
import pandas as pd




app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def login():
    # https://realpython.com/introduction-to-flask-part-2-creating-a-login-page/
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'alaska' or request.form['password'] != 'university':
            error = 'Invalid Credentials. Please try again.'
        else:
            return render_template('dashboard.html')
    return render_template('index.html', error=error)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the values from the form
        gre = float(request.form.get('gre'))
        cgpa = float(request.form.get('cgpa'))
        sop = float(request.form.get('sop'))


        # Scale the values
        scores = (gre, cgpa, sop)
        sc_scores = model.sc.transform([scores])


        # Use the model to make a prediction
        prediction = model.log_model.predict(sc_scores)
        if prediction[0] == 0:
            prediction = 'Reject'
        else:
            prediction = 'Admit'
        probability = model.log_model.predict_proba(sc_scores)

        # Return the prediction
        return f'DECISION = {prediction} - Rating: {probability[0][1] * 100:.2f}% chance'
    else:
        # Render the form
        return render_template('predict.html')



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from the request
        file = request.files['applicants']

        # create dataframe and segment variables
        new_data = pd.read_csv(file)
        X = new_data.drop(columns=['applicant no.'])

        # scale independent variables
        X = pd.DataFrame(model.sc.transform(X))

        # apply logistic regression model and insert decisions into dataframe
        decisions = model.log_model.predict(X)
        new_data.insert(4, 'decision', decisions)
        results = new_data.to_html(index=False, classes='table table-stripped', header=True, escape=False)


        # Return table with decisions
        return results
    else:
        # Render the form
        return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
