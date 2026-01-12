from flask import Flask, render_template, request, redirect, url_for
import json
import os
import time
import uuid

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                if "instances" not in data: data["instances"] = []
                return data
            except:
                pass
    return {"instances": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/dashboard")
def dashboard():
    data = load_data()
    return render_template("dashboard.html", data=data)

@app.route("/")
def index():
    data = load_data()
    edit_id = request.args.get("edit_id")
    edit_instance = None
    if edit_id:
        edit_instance = next((i for i in data["instances"] if i["id"] == edit_id), None)
    return render_template("index.html", data=data, edit_instance=edit_instance)

@app.route("/edit_instance/<instance_id>")
def edit_instance(instance_id):
    return redirect(url_for("index", edit_id=instance_id))

@app.route("/configure", methods=["POST"])
def configure():
    data = load_data()
    
    # Extract data from form
    edit_id = request.form.get("edit_id")
    name = request.form.get("name")
    user_id = request.form.get("user_id")
    token = request.form.get("token")
    
    server_ids = request.form.getlist("server_id[]")
    server_labels = request.form.getlist("server_label[]")
    channel_ids = request.form.getlist("channel_id[]")
    
    targets = []
    for i in range(len(channel_ids)):
        if channel_ids[i].strip():
            targets.append({
                "server_id": server_ids[i] if i < len(server_ids) else "",
                "server_label": server_labels[i] if i < len(server_labels) else "",
                "channel_id": channel_ids[i]
            })

    messages = request.form.getlist("messages[]")
    delay = request.form.get("delay")

    instance_data = {
        "name": name or "New Instance",
        "user_id": user_id,
        "token": token,
        "targets": targets,
        "messages": [m for m in messages if m.strip()],
        "delay": int(delay or 60),
    }

    if edit_id:
        for i in data["instances"]:
            if i["id"] == edit_id:
                i.update(instance_data)
                break
    else:
        # Check if an instance with same user_id AND token AND target channels already exists
        duplicate = False
        new_channel_ids = sorted([t["channel_id"] for t in instance_data["targets"]])
        for i in data["instances"]:
            if (i["user_id"] == instance_data["user_id"] and 
                i["token"] == instance_data["token"]):
                
                existing_channel_ids = sorted([t["channel_id"] for t in i["targets"]])
                if existing_channel_ids == new_channel_ids:
                    duplicate = True
                    break
        
        if not duplicate:
            instance = {
                "id": str(uuid.uuid4()),
                "running": False,
                "next_task_time": 0,
                **instance_data
            }
            data["instances"].append(instance)
    
    save_data(data)
    return redirect(url_for("dashboard"))

@app.route("/toggle_instance/<instance_id>", methods=["POST"])
def toggle_instance(instance_id):
    data = load_data()
    for instance in data["instances"]:
        if instance["id"] == instance_id:
            instance["running"] = not instance.get("running", False)
            if not instance["running"]:
                instance["next_task_time"] = 0
            break
    save_data(data)
    return redirect(url_for("dashboard"))

@app.route("/delete_instance/<instance_id>")
def delete_instance(instance_id):
    data = load_data()
    data["instances"] = [i for i in data["instances"] if i["id"] != instance_id]
    save_data(data)
    return redirect(url_for("dashboard"))

@app.route("/api/status")
def api_status():
    return load_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
