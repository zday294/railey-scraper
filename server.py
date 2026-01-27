from flask import Flask, jsonify, request
from report_reader import find_report

app = Flask(__name__)


# brady report endpoint
@app.route('/brady-report', methods=['GET'])
def get_brady_report():
    return find_report("cabin-report-brady.html")

@app.route('/report')
def get_report():
    return find_report("cabin-report.html")

@app.route('/abridged-report')
def get_abridged_report():
    return find_report('cabin-report-no-brady.html')

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello, World!")

app.run(port=8000, debug=True)