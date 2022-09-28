FROM public.ecr.aws/lambda/python:3.9

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["app.lambda_handler"]
