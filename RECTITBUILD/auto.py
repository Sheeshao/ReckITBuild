import json
import random
import time
import os
import threading
from datetime import datetime
from http.client import HTTPSConnection

DATA_FILE = "data.json"
threads = {}

def get_timestamp():
    return "[" + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "]"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                pass
    return {"instances": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_instance_time(instance_id, delay):
    data = load_data()
    for instance in data["instances"]:
        if instance["id"] == instance_id:
            instance["next_task_time"] = int(time.time() + delay)
            break
    save_data(data)

def send_message(conn, channel_id, message_data, header_data):
    try:
        conn.request("POST", f"/api/v6/channels/{channel_id}/messages", message_data, header_data)
        resp = conn.getresponse()
        data = resp.read()
        print(f"{get_timestamp()} Sent to {channel_id}: {resp.status} - {data.decode() if data else 'No Body'}")
    except Exception as e:
        print(f"{get_timestamp()} Error: {e}")

def get_connection():
    return HTTPSConnection("discordapp.com", 443)

def run_instance(instance_id):
    print(f"{get_timestamp()} Starting instance {instance_id}")
    while True:
        data = load_data()
        instance = next((i for i in data.get("instances", []) if i["id"] == instance_id), None)
        
        if not instance or not instance.get("running", False):
            print(f"{get_timestamp()} Stopping instance {instance_id}")
            break

        header_data = {
            "content-type": "application/json",
            "user-id": str(instance["user_id"]),
            "authorization": str(instance["token"]),
            "host": "discordapp.com"
        }
        
        delay = int(instance.get("delay", 60))
        
        # Perform all target sends "at the same time" (quickly in sequence)
        for target in instance["targets"]:
            channel_id = str(target["channel_id"])
            for message in instance["messages"]:
                # Re-check running status inside inner loops
                data = load_data()
                inst = next((i for i in data["instances"] if i["id"] == instance_id), None)
                if not inst or not inst.get("running", False): return

                message_data = json.dumps({"content": str(message)})
                conn = get_connection()
                send_message(conn, channel_id, message_data, header_data)
                conn.close()
                
        # Sleep once AFTER processing all targets and messages
        sleep_duration = delay + random.randint(1, 5)
        update_instance_time(instance_id, sleep_duration)
        
        print(f"{get_timestamp()} Instance {instance_id} finished cycle, sleeping for {sleep_duration}s")
        for _ in range(sleep_duration):
            time.sleep(1)
            # Dynamic check to stop immediately if toggled off
            data = load_data()
            inst = next((i for i in data["instances"] if i["id"] == instance_id), None)
            if not inst or not inst.get("running", False): return

def main():
    print(f"{get_timestamp()} Monitor started.")
    while True:
        data = load_data()
        for instance in data.get("instances", []):
            instance_id = instance["id"]
            if instance.get("running", False):
                if instance_id not in threads or not threads[instance_id].is_alive():
                    t = threading.Thread(target=run_instance, args=(instance_id,), daemon=True)
                    t.start()
                    threads[instance_id] = t
            else:
                # Thread will naturally exit on next check because running=False
                pass
        
        time.sleep(5)

if __name__ == "__main__":
    main()
