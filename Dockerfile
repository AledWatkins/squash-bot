# Lambda base image for Docker from AWS
FROM public.ecr.aws/lambda/python:latest

# Copy all code and lambda handler
COPY squash_bot ./squash_bot
COPY lambda_function.py ./
COPY requirements.txt ./

# Install packages
RUN python3 -m pip install -r requirements.txt

# Run lambda handler
CMD ["lambda_function.lambda_handler"]