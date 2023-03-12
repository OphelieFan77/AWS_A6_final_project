
import boto3
import csv
from math import exp

s3 = boto3.client('s3')
bucket_name = 'test-bucket-for-josef'
file_name = 'parameters1.csv'

def lambda_handler(event, context):

    # Parse input values from API Gateway endpoint
    sqm = float(event.get('queryStringParameters', {}).get('sqm', 0))
    n_bathrooms = float(event.get('queryStringParameters', {}).get('n_bathrooms', 0))
    is_new_dev = int(event.get('queryStringParameters', {}).get('is_new_dev', 0))
    has_central_heating = int(event.get('queryStringParameters', {}).get('has_central_heating', 0))
    has_lift = int(event.get('queryStringParameters', {}).get('has_lift', 0))
    has_parking = int(event.get('queryStringParameters', {}).get('has_parking', 0))
    downtown = int(event.get('queryStringParameters', {}).get('downtown', 0))
    
    # Load file with coefficients from S3
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    data = response['Body'].read().decode('utf-8').splitlines()
    
    # Parse CSV file
    reader = csv.reader(data)
    next(reader) # skip header row
    
    # Create dictionary to store coefficients
    coefficients = {}
    for row in reader:
        feature, coefficient = row[0], float(row[1])
        coefficients[feature] = coefficient
    
    # Calculate predicted price using coefficients and input values
    predicted_price = (
        coefficients['Intercept'] +
        coefficients['sq_mt_built'] * sqm +
        coefficients['n_bathrooms'] * n_bathrooms +
        coefficients['is_new_development'] * is_new_dev +
        coefficients['has_central_heating'] * has_central_heating +
        coefficients['has_lift'] * has_lift +
        coefficients['has_parking'] * has_parking +
        coefficients['downtown'] * has_parking * downtown)
    
    #take the exponetial of the predicted price (due to log linear regression)
    pred_normal = exp(predicted_price)
    
    
    #format response in html format and allow user to input values on website
    return {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'text/html',
    },
    'body': f'''
        <html>
            <head>
                <title>Price Prediction Results</title>
            </head>
            <body>
                <h1>Price Prediction Results</h1>
                <p>The price of your house is: {round(pred_normal, 2)}</p>
                <h2>Please input your housing details below for an estimate:</h2>
                <form method="GET" action="/pred">
                    <label>Square meters:</label>
                    <input type="number" name="sqm"><br><br>
                    <label>Number of bathrooms:</label>
                    <input type="number" name="n_bathrooms"><br><br>
                    <label>Is new development:</label>
                    <select name="is_new_dev">
                        <option value="1">Yes</option>
                        <option value="0">No</option>
                    </select><br><br>
                    <label>Has central heating:</label>
                    <select name="has_central_heating">
                        <option value="1">Yes</option>
                        <option value="0">No</option>
                    </select><br><br>
                    <label>Has lift:</label>
                    <select name="has_lift">
                        <option value="1">Yes</option>
                        <option value="0">No</option>
                    </select><br><br>
                    <label>Has parking:</label>
                    <select name="has_parking">
                        <option value="1">Yes</option>
                        <option value="0">No</option>
                    </select><br><br>
                    <label>Downtown:</label>
                    <select name="downtown">
                        <option value="1">Yes</option>
                        <option value="0">No</option>
                    </select><br><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
    '''
}



