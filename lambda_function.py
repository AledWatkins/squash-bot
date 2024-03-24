from squash_bot.core import lambda_function as core_lambda_function

# This is the entry point for the AWS Lambda function
# Shadows the lambda_handler function in `/core/`
lambda_handler = core_lambda_function.lambda_handler
