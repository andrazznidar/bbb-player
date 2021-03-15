FROM python:3.7-alpine 
WORKDIR /app 
COPY requirements.txt /app
RUN pip3 install -r requirements.txt 
COPY . /app 
ENTRYPOINT ["python"] 
CMD ["bbb-player.py", "--server"]
