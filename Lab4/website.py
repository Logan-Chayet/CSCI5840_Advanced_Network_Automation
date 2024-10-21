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
    config_output = None
    if request.method == 'POST':
        yaml_output = playbookCreation.createEdge() 
        print(yaml_output)
        
        os.system("ansible-playbook ANSIBLE/site.yaml --tags edge")
        
        config_output = playbookCreation.sendConfig()

        #return f"<pre>{config_output}</pre>"

    return render_template('edge_config.html', output=config_output)

@app.route("/core_config", methods=['GET','POST'])
def core_config():
    config_output = None
    if request.method == 'POST':
        yaml_output = playbookCreation.createCore()
        print(yaml_output)

        os.system("ansible-playbook ANSIBLE/site.yaml --tags core")

        config_output = playbookCreation.sendConfig()

        #return f"<pre>{config_output}</pre>"

    return render_template('core_config.html', output=config_output)

@app.route("/access_config", methods=['GET','POST'])
def access_config():
    config_output = None
    if request.method == 'POST':
        yaml_output = playbookCreation.createAccess()
        print(yaml_output)

        os.system("ansible-playbook ANSIBLE/site.yaml --tags access")

        config_output = playbookCreation.sendConfig()

        #return f"<pre>{config_output}</pre>"

    return render_template('access_config.html', output=config_output)

@app.route("/get_golden_configs", methods=['GET','POST'])
def get_golden_configs():
    if request.method == 'POST':
        configs = playbookCreation.getGoldenConfig()
        return f"<pre>{configs}</pre>"

    return render_template('get_golden_configs.html')

@app.route("/health_check")
def health_check():
    return render_template('health_check.html')

@app.route("/config")
def config():
    return render_template('config.html')

@app.route("/neighborships", methods=['GET','POST'])
def neighborships():
    output = None
    if request.method == 'POST':
        output = playbookCreation.get_neighborships()

    return render_template('neighborships.html', output=output)

@app.route("/cpu", methods=['GET','POST'])
def cpu():
    output = None
    if request.method == 'POST':
        output = playbookCreation.get_cpu()

    return render_template('cpu.html', output=output)

@app.route("/route_table", methods=['GET','POST'])
def route_table():
    output = None
    if request.method == 'POST':
        output = playbookCreation.get_route_table()

    return render_template('route_table.html', output=output)

@app.route("/ip_connectivity", methods=['GET','POST'])
def ip_connectivity():
    output = None
    if request.method == 'POST':
        output = playbookCreation.get_ip_connectivity()

    return render_template('ip_connectivity.html', output=output)

if __name__ == "__main__":
    app.run(debug=True)