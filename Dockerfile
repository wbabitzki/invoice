# AWS Lambda container image for invoice rendering
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies required by WeasyPrint
RUN yum install -y \
    cairo \
    pango \
    gdk-pixbuf2 \
    libffi-devel \
    fontconfig \
    freetype \
  && yum clean all \
  && rm -rf /var/cache/yum

# Install Python dependencies
COPY requirements.txt  .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Set the Lambda handler
CMD ["lambda_handler.handler"]
