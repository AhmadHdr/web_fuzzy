# Struktur Proyek:
# fuzzy_web_app/
#   ├── app.py
#   ├── fuzzy_mamdani.py
#   ├── templates/
#   │   └── index.html
#   └── static/
#       └── styles.css

# app.py - Aplikasi Flask Utama
from flask import Flask, render_template, request, jsonify
from fuzzy_mamdani import FuzzyMamdani
import plot
import plotly.graph_objs as go
import json

app = Flask(__name__)

class FuzzyWebApp:
    def __init__(self):
        self.fuzzy_model = FuzzyMamdani()

    def generate_membership_plot(self, variable_type):
        """Membuat plot keanggotaan fuzzy"""
        if variable_type == 'input1':
            x_values = self.fuzzy_model.input1_range
            memberships = self.fuzzy_model.calculate_input1_membership()
        elif variable_type == 'input2':
            x_values = self.fuzzy_model.input2_range
            memberships = self.fuzzy_model.calculate_input2_membership()
        else:
            x_values = self.fuzzy_model.output_range
            memberships = self.fuzzy_model.calculate_output_membership()

        # Membuat plot Plotly
        traces = []
        for label, membership in memberships.items():
            trace = go.Scatter(
                x=x_values, 
                y=membership, 
                mode='lines', 
                name=label
            )
            traces.append(trace)

        layout = go.Layout(
            title=f'Fungsi Keanggotaan {variable_type}',
            xaxis={'title': 'Nilai'},
            yaxis={'title': 'Derajat Keanggotaan'}
        )

        return json.dumps({"data": traces, "layout": layout}, cls=plot.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    fuzzy_app = FuzzyWebApp()
    
    # Plot keanggotaan default
    input1_plot = fuzzy_app.generate_membership_plot('input1')
    input2_plot = fuzzy_app.generate_membership_plot('input2')
    output_plot = fuzzy_app.generate_membership_plot('output')

    return render_template('index.html', 
                           input1_plot=input1_plot,
                           input2_plot=input2_plot,
                           output_plot=output_plot)

@app.route('/calculate', methods=['POST'])
def calculate():
    fuzzy_app = FuzzyWebApp()
    data = request.json
    
    # Proses perhitungan fuzzy
    input1 = data.get('input1')
    input2 = data.get('input2')
    
    # Lakukan inferensi fuzzy
    result = fuzzy_app.fuzzy_model.defuzzification(input1, input2)

    return jsonify({
        'result': result,
        'fuzzy_steps': fuzzy_app.fuzzy_model.get_inference_steps()
    })

if __name__ == '__main__':
    app.run(debug=True)

