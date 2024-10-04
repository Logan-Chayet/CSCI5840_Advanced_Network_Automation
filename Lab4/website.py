from flask import Flask,render_template,request
import yaml
import playbookCreation
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/edge_config", methods=['GET','POST'])
def edge_config():
    if request.method == 'POST':
        yaml_output = playbookCreation.createEdge() 
        print(yaml_output)
        
        os.system("ansible-playbook ANSIBLE/site.yaml --tags edge")
        
        config_output = playbookCreation.sendConfig()

        return f"<pre>{config_output}</pre>"

    return render_template('edge_config.html')

@app.route("/core_config", methods=['GET','POST'])
def core_config():
    if request.method == 'POST':
        yaml_output = playbookCreation.createCore()
        print(yaml_output)

        os.system("ansible-playbook ANSIBLE/site.yaml --tags core")

        config_output = playbookCreation.sendConfig()

        return f"<pre>{config_output}</pre>"

    return render_template('core_config.html')

@app.route("/access_config", methods=['GET','POST'])
def access_config():
    if request.method == 'POST':
        yaml_output = playbookCreation.createAccess()
        print(yaml_output)

        os.system("ansible-playbook ANSIBLE/site.yaml --tags access")

        config_output = playbookCreation.sendConfig()

        return f"<pre>{config_output}</pre>"

    return render_template('access_config.html')

@app.route("/get_golden_configs", methods=['GET','POST'])
def get_golden_configs():
    if request.method == 'POST':
        configs = playbookCreation.getGoldenConfig()
        return f"<pre>{configs}</pre>"

    return render_template('get_golden_configs.html')

