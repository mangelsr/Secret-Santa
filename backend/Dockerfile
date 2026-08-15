FROM public.ecr.aws/lambda/python:3.14

# Copy requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app ${LAMBDA_TASK_ROOT}/app

# Set CMD to Mangum ASGI handler
CMD [ "app.main.handler" ]
