import os
from flask import Flask, request
import threading

import requests
import json

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def startFlaskServer():
    app.run(debug=False)

def getUserInput():
    os.system('clear')
    print("Once communication channel is active, you must kill the tasks to terminate. This can be done with Ctrl + C")

    setup = False
    info = {}


    with open("settings.json", "r") as data:
        info = json.load(data)
        setup = info["setup"]

    if setup:
        setup = input("Would you like to use the cached info? (Y/N)").lower != "y"

    if not setup:
        email = input("please enter an email to communicate to")
        site = input("please enter a ngrok port to send to. (this should be the other person's port)")+"/upload"

        info["email"] = email
        info["destination"] = site
        info["setup"] = True
        with open("settings.json", "w") as settings:
            json.dump(info, settings, indent=4)

        print("Settings has been updated...")

    
    while True:
        message = input()
        with open("output.txt", "w") as out:
            out.write(message)

        os.system("gpg --encrypt --sign --armor -r " + info["email"] + " ./output.txt")
        os.system("curl -X POST -F \"file=@output.txt.asc\" " + info["destination"])

app = Flask(__name__)

stopFlag = threading.Event()

receiverThread = threading.Thread(target=startFlaskServer)
senderThread = threading.Thread(target=getUserInput)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Save the uploaded file as "incoming.asc"
        file.save('incoming.asc')

        os.system("gpg --yes --quiet --status-file /dev/null --output decrypted.txt --decrypt incoming.asc > /dev/null 2>&1")

        # Read and print the contents of "decrypted.txt"
        with open("decrypted.txt", "r") as f:
            content = f.read()
            print("Message Received:", content)

        return 'File uploaded successfully'

if __name__ == '__main__':
    receiverThread.start()
    senderThread.start()

    # Wait for either thread to finish
    senderThread.join()
    receiverThread.join()
    print("done!")
