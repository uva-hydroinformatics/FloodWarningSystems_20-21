# AWS Lambda Quick Tutorial

## Why AWS Lambda?
AWS Lambda allows us to run modular, standalone pieces of code without having to deploy something like an EC2 instance or reserving a computer to run our code. This means that we can run a function with minimal resources deployed, saving on both time and cost. When we are talking about "serverless architecture", we are referring to this. Another thing about Lambda is that if the function has already been called but is still running while another request comes in, another instance of the function is deployed concurrently. At the moment, we can have up to 1000 concurrent instances. This can be useful in the future once the system expands to accomodate future devices added.

## Getting to Lambda
On the AWS console, go to Services > Lambda (under Compute). You should now see the dashboard with existing Lambda functions and the option to create new ones.

## Creating a Function
1. On the Functions dashboard, click "Create function"
2. Choose "Author from scratch"
3. Enter a function name and choose your runtime environment (our current choice is Python 3.8)
4. Leave the rest of the options default for now and click "Create function"
5. You are now brought to the configuration page for your function. At the top is the "Designer" section, which is a graphical representation of how your Lambda interacts with other AWS elements. Here you can view or add triggers (to invoke the function) or destinations (to store the output). Right below that we have the "Function code" section where you can upload and edit code and files, similar to how you would normally program on your own device. 
6. Create 2 new files, "http_get.py" and "payload_parser.py"
7. You should now have 3 files, including "lambda_funiction.py". Copy the code from the GitHub repo into their respective files in Lambda, Save, and click "Deploy". 
8. lambda_function.py: This file contains the main function "lambda_handler()" when invoked (similar to combine.py). From this file, you can call functions from the other files just like normal. The function returns a status code and a body that contains a message if you so choose. This is useful if you want to monitor the invocations and outputs of your Lambda function in Cloudwatch. Before returning the function, you can do things like sending a message to one of the devices, transform incoming data, or uploading data to S3 or a database.

## Testing a Function
1. Click "Test" > "Create new test event"
2. For our purposes, "Event template" can be left as-is and put anything in "Event name" like "test"
3. Since our current code is requesting data from the sensor and not taking in a json file as a parameter, for now we can just basically ignore the data being passed to our Lambda function and click "Create"
4. Now click "Test" and your Lambda should be invoked
5. You should return an error in the output window below. This is because for Lambda, we sometimes have to provide the libraries we want to use on our own. In this case, we need to provide the "requests" library. To do this, we use "Lambda Layers".

## Lambda Layers and Uploading Libraries
1. You don't need to do this right now, but to create the library needed, I followed this guide and replaced "pandas" with "requests": https://medium.com/brlink/how-to-create-a-python-layer-in-aws-lambda-287235215b79
2. On the Lambda dashboard, click "Layers" from the left-hand side
3. Click "Create layer"
4. Give the layer a name and description and upload the zip file (the one provided is located in ["Lambda Layer/python.zip"](https://github.com/uva-hydroinformatics/FloodWarningSystems_20-21/blob/main/AWS%20Lambda/Lambda%20Layer/python.zip))
5. Select at least Python 3.8 for runtime and click "Create"
6. Go back to the Lambda function created earlier
7. In the "Designer" section, click on "Layers" > "Add a layer"
8. Select "Custom layers" > the layer you just created > "Add"
9. Test your function again and now it should work
10. View the log outputs of your function in "CloudWatch" > "CloudWatch Logs" > "Log groups" > your Lambda function and choose a Log stream (refers to an invocation of your function)