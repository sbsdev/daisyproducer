FROM debian:stretch

# enable contrib (for ttf-mscorefonts-installer)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	software-properties-common \
	&& add-apt-repository contrib

# Fetch build dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    default-jre \
    gettext \
    hyphen-de \
    jing \
    latexmk \
    libsaxonhe-java \
    lmodern \
    mysql-client \
    python \
    python-django \
    python-docutils \
    python-httplib2 \
    python-libxml2 \
    python-libxslt1 \
    python-louis \
    python-lxml \
    python-mysqldb \
    python-pypdf2 \
    python-requests \
    python-stdnum \
    texlive-lang-german \
    texlive-latex-extra \
    texlive-latex-recommended \
    texlive-xetex \
    ttf-mscorefonts-installer \
    ttf-tiresias \
    unzip \
   && rm -rf /var/lib/apt/lists/*

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
