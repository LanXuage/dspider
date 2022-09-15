FROM python:alpine3.16

ENV PYTHONPATH=/usr/src/app

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python", "./scheduler.py"]
