# syntax=docker/dockerfile:1.7
FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y \
        cairo \
        cairo-devel \
        gdk-pixbuf2 \
        gdk-pixbuf2-modules \
        libffi \
        libffi-devel \
        pango \
        pango-devel \
    && dnf clean all \
    && rm -rf /var/cache/dnf

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/task/output
RUN mkdir -p /tmp/.cache/fontconfig

COPY config.py ./
COPY invoice.py ./
COPY lambda_function.py ./
COPY referenznummer.py ./
COPY swiss_bill_generator.py ./
COPY static ./static
COPY styles ./styles
COPY templates ./templates

ENV HOME=/tmp
ENV XDG_CACHE_HOME=/tmp/.cache

CMD ["lambda_function.lambda_handler"]