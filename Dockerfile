FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /auth
WORKDIR /auth
COPY Requirements.txt /auth/
RUN pip install -r Requirements.txt
COPY . /auth/
EXPOSE 8081
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8081