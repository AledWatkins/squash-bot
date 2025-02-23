# Lambda base image for Docker from AWS
FROM public.ecr.aws/lambda/python:latest

# Copy common package
COPY common ./common
# Copy squash_bot package
COPY squash_bot ./squash_bot
COPY requirements.txt ./

# Install packages
RUN python3 -m pip install -r requirements.txt

# Run lambda handler
CMD ["squash_bot.core.lambda_function.lambda_handler"]