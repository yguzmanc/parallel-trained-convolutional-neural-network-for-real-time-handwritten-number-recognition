# parallel-trained-convolutional-neural-network-for-real-time-handwritten-number-recognition
A convolutional neural network trained in parallel (optimizing this process), a web page that allows us to write the numbers from 0 to 9 and an output of the network prediction are presented. This is a first step in creating a network that recognizes mathematical symbols and handwritten formulas and returns them in latex format.

Download the files from the web page in a single folder

### Start a server in the folder
This project uses a Tensorflow.js model, which requires access via http/https to load.
You can use any server for that, but here's a way to do it:
- Download Python
- Open a command line or terminal
- Navigate to the folder where the repository was downloaded
- Run the command 'python -m http.server 8000'
- Open a browser and go to http://localhost:8000

### Use
Draw with the mouse or your finger on the square canvas a number from 0 to 9, and click on "Predict". To clear the canvas, click "Clear".
