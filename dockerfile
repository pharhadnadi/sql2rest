# load python 3.8 dependencies using slim debian 10 image.
FROM python:3.8-slim-buster

# build variables.
ENV DEBIAN_FRONTEND noninteractive

# install Microsoft SQL Server requirements.
ENV ACCEPT_EULA=Y
RUN apt-get update -y && apt-get update \
  && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev

# Add SQL Server ODBC Driver 17 for Ubuntu 18.04
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
  && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# upgrade pip and install requirements.
COPY /requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# clean the install.
RUN apt-get -y clean

#to ignore ssl problem that cause aproblem
RUN sed -i 's/DEFAULT@SECLEVEL=2/@SECLEVEL=1/g' /etc/ssl/openssl.cnf
RUN sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf

# copy all files to /app directory and move into directory.
COPY MSSQL2REST/. /app
WORKDIR /app

#ENTRYPOINT ["python ", "python", "command"]

LABEL maintainer="Farhad Nadi <farhad.nadi@gmail.com>"

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"] 

