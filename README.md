# Documendous

## About

Documendous is a simple enterprise content management (ECM) application.

Wikipedia's entry on ECM (see: https://en.wikipedia.org/wiki/Enterprise_content_management)

Documendous is written in Python using Django. At the moment, Documendous only supports Postgresql for RDBMS and Search capabilities. There are plans to support other RDBMS databases and also use a search engine like Elastic Search in furture versions, however.

## Security

Security's a big deal and it SHOULD be a big deal to you and your organization. We try to make our code as safe as possible for you but ultimately it is your responsibility.

Eventually when you get around to installing Documendous in a production or otherwise userful environment, it is imperative that you change the following setting in docrepo/docrepo/settings.py file:

```
SECRET_KEY = "Documendous"
```

At last build, it was set to:

```
# SECRET_KEY = "django-insecure-rv0cn+9=nm@-+ov1h7+pgxyzvi)k@8bb3jl@+o0f2l&0+_)e)r"
```

Ensure that you change this to something else. It should a very long, boring and completely unguessable string. Thank you.

### Current Version: 2022.08.1

## Supported Components

* Python: 3.10.4 (but should work with Python 3.8+)
* Django: 3.2.14
* Database: Postgresql (tested with Postgresql 12 and 14.4 but should work with versions 10+).
* Nginx: tested with versions 1.14 up to 1.18 but should work with any 1.14+.
* Operating System: Tested on Ubuntu 20.04 (should work well on any modern distro/version of Linux and probably MacOSX)
* LibreOffice: Optional but highly recommended else transformations (document preview's and full text search) will not be available. Tested with version 6.4.7-0ubuntu0.20.04.4
* Additional software: For LibreOffice to work as needed, ensure you have the following packages installed:

```
fontconfig libice libsm libsm-dev libxrender libxrender-dev libxext libxext-dev libxinerama libxinerama-dev cups-filters-libs cups-filters-dev cups-libs freeglut cairo mesa-gl
```

Using Windows? You can probably get it to work but it's not recommended.

Docker (for testing purposes): Docker version 20.10.17, build 100c701

### How to Install Postgresl?

See: https://www.google.com/search?q=how+to+install+postgresql

### How to Install Python?

See: https://www.google.com/search?q=how+to+install+python

But ... I personally recommend using pyenv. If you're on Windows, know that pyenv likely will not work there.

For Pyenv see: https://github.com/pyenv/pyenv#installation

## Install Documendous

The way to get Documendous is:

1. Download: https://github.com/documendous/docrepo/archive/refs/heads/main.zip
2. Unzip resulting file documendous-main.zip
3. This will create a folder called documendous-main

### Running Documendous in a Development Environment

Inside the documendous-main folder, create a virtualenv:

1. Set the Python version:
```
# pyenv global 3.10.4
```

2. Create the virtualenv
```
# pyenv virtualenv documendous
# pyenv local documendous # Ensure you are in the documendous-main folder when you run this.
```

3. Install dependencies
```
# pip install -r requirements.txt
```

4. Set your database connection string inside documendous-main/docrepo/docrepo/settings.py at this setting:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "documendous",
        "USER": "admin",
        "PASSWORD": "admin",
        "HOST": "db",
        "PORT": "5432",
    }
}
```

Alternatively, you can make use of dj-database-url package to handle your database endpoint configurations. See https://pypi.org/project/dj-database-url/ for instructions.


Obviously, make changes at a minimum to USER and PASSWORD. HOST is set to "db" so that it works with Docker out of the box. But, to properly set HOST:

* Change to localhost, 127.0.0.1 or other ip address/fqdn of your database server.

or

* Add an entry in your server's host file:

```
127.0.0.1  db
```

5. Find your soffice executable by doing:

```
# which soffice
/usr/bin/soffice
```

Make a note of the location. In the case above, it's at /usr/bin/soffice.

6. Open docrepo/transformations/settings.py and set the SOFFICE_EXE variable:

```
SOFFICE_EXE = "/usr/bin/soffice"
```

Save this file.

7. Now, you should be ready to setup Documendous. Go to documendous-main/docrepo and run:

```
# ./reset.sh
```

This will start the Django server and the index_service.py. The log files are in docrepo/logs though you should see output as it starts up.

To Stop Documendous, hit control-C and run: ./kill_tracker.sh.

At this point, your server is set up and it is a good idea to either move the reset.sh/resetdb-no-track.sh to another folder so that it cannot run again and reset your database or you can remove executable: chmod -x reset.sh

If you would like to persist your data, you should instead run:

```
# ./start.sh # with indexing
or
# ./start-no-track.sh # without indexing
```

### Docker

The Docker install of Documendous is much simpler. Go to documendous-main/deployment/docker and run:

```
# ./build.sh
```

This will generate the following images:

```
Creating new migrations ...
CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS                  PORTS                                       NAMES
aa1f3a5ec5d8   docker_nginx            "nginx -g 'daemon of…"   2 seconds ago   Up Less than a second   0.0.0.0:80->80/tcp, :::80->80/tcp           docker_nginx_1
6be103488ec6   docker_web              "gunicorn docrepo.ws…"   2 seconds ago   Up 1 second             0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   docker_web_1
7933cbc0023d   postgres:12.11-alpine   "docker-entrypoint.s…"   3 seconds ago   Up 1 second             5432/tcp                                    docker_db_1
```

## Manual Installation

*Currently only Postgresql is supported for RDBMS and Search functionality!*

You will need to install Postgresql server.

The following are steps to installing Documendous in a production environment.

### Download Latest Version of Documendous

Currently the only available version is 2022.08.0.alpha. With "alpha" in the name, it should be understood that at the moment, you shouldn't use Documendous in a true production environment. But if you choose to, here are the steps.

Look in the distro folder and download the Documendous-V2022.08.0.alpha.tgz file. Download this to a directory of your choice. We recommend creating a directory on your server at: /app/documendous/docrepo. 

To decompress the installation folder, do the following:

```
# tar xvzf Documendous-V2022.08.0.alpha.tgz
```

This will create a folder and a subfolder called "docrepo". Copy the contents of the docrepo folder to the /app/documendous/docrepo directory.

We recommend not running Documendous as "root". You should create and designate a non-privileged user to run Documendous.

### Install Dependencies

On a Debian-based system run the following commands to ensure all dependent software has been install on your system:

```
# sudo apt update
# sudo apt upgrade # <- optional but usually a good idea to start with a fully upgraded syste
# sudo apt install build-essential git python3-dev libbz2-dev libreadline-dev libssl-dev libsqlite3-dev postgresql postgresql-contrib python3.9-full python3-pip python3-pipdeptree gunicorn3 nginx-full nmap fontconfig libice-dev libice6 libsm6 libsm-dev libxrender1 libxrender-dev libxext6 libxext-dev libxinerama1 libxinerama-dev cups-filters freeglut3 freeglut3-dev cairo-5c libgl1-mesa-glx default-jre libreoffice-java-common -y
```

With RedHat-based systems you will likely need to find the RHEL equivalents of the packages listed above. You will need to use an appropriate rpm (Redhat Package Manager) compatible installer that RHEL provides.

### Setting up Postgresql

The instructions below assume you will set up Postgresql on the same server with Documendous. For better performance, consider running your Postgresql server on another server.

You will need to copy the following configuration to your Postgresql configuration file (/etc/postgresql/VERSION_NUMBER/main/pg_hba.conf):

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            password
# IPv6 local connections:
host    all             all             ::1/128                 ident
```

Ensure that Postgresql Server is working:

*We're assuming the db name of 'documendous' with user called 'admin' and password called 'admin'. Be sure to change these to secure your environment and meet your organization's requirements.*

```
# sudo systemctl enable postgresql
# sudo systemctl start postgresql
# sudo su - postgres -c 'createuser -s admin'
# sudo -u postgres psql -c "ALTER USER admin PASSWORD 'admin';"
# sudo su - postgres -c 'createdb documendous -O admin'
```

### Set up Server

The following assumes your install directory will be at /app/documendous/docrepo and you are using a user called 'web' to run Documendous.

Create the install directory and set the ownership for the 'web' user:

```
# sudo mkdir -p /app/documendous
# sudo chown -R web:web /app/documendous
```

Add a symlink for python to point to python3. 

```
# sudo ln -s /usr/bin/python3 /usr/bin/python
```

Copy the "docrepo" install folder to /app/documendous/.

```
# cp -rf docrepo /app/documendous/.
```

Install all necessary Python packages:

```
# /usr/bin/pip install -r /app/documendous/docrepo/requirements.txt
```

Create a static subdirectory in the docrepo folder:

```
# cd /app/documendous/docrepo
# mkdir static
```

Run the reset.sh script:

```
# ./reset.sh
```

Be aware that you will not want to run the reset.sh script unless you understand that it will erase your database and contentfiles. Should you need to run again or blow the repo away, backup your database and contentfiles folder first.

### Setup Nginx

Remove the default Nginx configuration. For this kind of install, you won't need it:

```
# sudo rm /etc/nginx/conf.d/default.conf
```

Add the following content to a file at /etc/nginx/conf.d/nginx.conf:

```
upstream documendous {
    server web:8000;
}

server {

    listen 80;

    location / {
        proxy_pass http://documendous;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /app/documendous/docrepo/static/;
    }

}
```

Add the following content to a file at /etc/nginx/nginx.conf:

```

# user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
```

Start Gunicorn (a wsgi server):

This should be run in the directory of /app/documendous/docrepo:

```
# gunicorn3 docrepo.wsgi:application --bind 0.0.0.0:8000 &
```

Start Nginx:

```
# sudo systemctl start nginx
```

Documendous should now be started and working.

## Accessing Documendous

Point your browser to http://localhost:8000 or (on Docker) http://localhost.

Attempting to access any links on the front page will require you to login if you have not already done so.

The default admin username/password is:

* Username: admin
* Password: admin

## Using Documendous

### Ui

The default user interface is simply called "ui".

#### Start Page

On the start page, there are these links:

* Admin Page
* My Dashboard
* API

The admin page is a Django admin console that requires the user to be a superuser. Out of the box, the "admin" user is the only superuser. *Note: some demo's installed may include a superuser (i.e. the Phoenix Project includes a sample superuser called billpalmer).

My Dashboard will take you to a page that shows:

Favorites: favorited documents and favorited folders
Document Management Timeline: recent activities by users in the system
Recently Edited: recent documents edited by your user
Recently Viewed: recent documents viewed by your user

The API page will take you to the installed Django REST Framework frontend. By default, your user must be authenticated in order to access it.

Once logged in, additional navigation links will be available:

* My Home
* Repository
* Projects
* Admin Console
* Search
* Favorites
* Trashcan
* My Profile
* Login/Logout

My Home: Your user's home space or container in the logical repository. You can create folders and documents in this folder path.

Repository: This links to the logical repository path for Documendous. This repository path simulates a file system where users have different privileges and authorizations.

Projects: This will take you to a list of available projects in Documendous. A project is a grouping of folders and documents that can used for sharing and collaboration across a team. Any user can create a project and be its project owner. The project owner and manager can add or invite other system users into the project.

Admin Console: This links to the admin page listed above.

Search: Allows users to search for folders and documents in the system that the user has access to.

Favorites: Links to a page that shows your user's favorite documents and folders.

Trashcan: All documents and folders deleted will go into your user's trashcan folder. Documents and folders can only be permanently deleted by deleting them from your trashcan.

My Profile: Contains information about your user's profile. These can be updated by you.

Login/Logout: Users can use this link to login or out of the system.

#### Repository View

The repository view is a folder's view.

Inside a folder view, if your user has ownership for this container, the user can do the following:

* Create a new folder
* Create a new document
* Add multiple documents at once

##### Add New Folder

A popup window allows you to enter:

* Name (required)
* Title (optional)
* Description (optional)

When the folder is created the view will show name, title, description, its owner and modified time.

The following actions will show for each folder that you own/create:

* Delete folder (and contents)
* Favorite folder

Be aware that these actions will only show for your folder or folders in projects where you have owner or manager privileges.

##### Add New Document

This will take you to an add document page where you can enter the following:

* Name (required)
* Title (optional)
* Description (optional)
* Upload a file from your workstation

By default the name will auto-populate based on the uploaded file from your file system.

Below these four fields are optional Dublin Core fields that can be entered with information. For more information on Dublin Core, please see: https://en.wikipedia.org/wiki/Dublin_Core

When documents are created the view will show name, title, description, its owner and modified time.

The following actions will show for each document that you own/create:

* Delete document
* Favorite document

Be aware that these actions will only show for your document or documents in projects where you have owner or manager privileges.

##### Add Multiple Documents

On this page, you are able to upload multiple files into Documendous. As part of the functionality, the names of each document will be auto-generated based on the uploaded files.

The resulting page will show successful and failed uploads. To go back to your initial folder view, you can click on the folder in the breadcrumb path or hit Cancel.

##### Bulk Actions

When documents or folders are selected (All checkbox selects all), the following bulk actions become available:

* Copy 
* Move
* Recycle

Copy and move allows you to copy and move your selections to another folder in the repository where you have authorization to do so.
Recyle allows you to delete (to trashcan) your selected documents and folders.

Like a file system, a folder cannot contain multiple documents or subfolders with the same name. Thus, if a copy/move of a document/folder is performed into a destination folder with children of the same name, the names of the destination folders/documents will have their own id appended to the names so as to prevent naming collisions.

##### Document View

A user can view a document's details at its document view. By default, a document can have unlimited associated content file versions.

The following actions can potentially be performed on the document:

* Generate Preview (if preview hasn't been generated yet)
* View Preview (if preview has been generated)
* Download Document (download to your workstation)
* Upload New Version (only available to document owner or project managers and editors)


##### Folder Detail View

A user can view a folder's details. A user who owns the folder (or is a project editor or manager) can update the folder's properties.

#### Projects View

Projects are a logical grouping of folders and documents with the objective of sharing or collaborating.

Projects can be created with the following accesses:

* Open (any user in the system can access, but not change without permissions, any user can join the project as a member without permission)
* Public (any user can find this project but has limited access)
* Private (only the owner and superusers can see this project in the list -- other users must be added to the project membership in order to see it)

Any user can create its own projects. To do that, click on Create New Project. On this page, all fields (name, title, description and access are mandatory).

The Projects view shows the following sections:

* Projects I Own (project your user creates)
* Projects I Am A Member Of (project where you have been added as a member)
* All Other Public & Open Projects (listing of other activated public and open projects)

Owned projects will allow your user to access its settings shown in the actions column.

This will take you to an update page where the user can make changes to:

* Name
* Title
* Description
* Members
* Access
* Activation or deactivation

*Note: Within the UI, there is no way to "delete" a project. The closest action to this is to deactivate the project.

Other actions allow a user to join a project, request membership to a project or leave a project.

There are also links for additional project settings in the project update page:

* Membership Requests For This Project
* Manage Groups

##### Membership Requests

When a user requests membership for your project, you will see them in the list. You can approve them here.

##### Manage Groups

When a project is created the following groups are created:

* Managers
* Contributors
* Editors
* Consumers

Managers have full access to a project and its artifacts (documents/folders). Managers can also delete them.

Contributors are able to add artifacts to a project but cannot edit or delete them.

Editors are able only to read and edit artifacts but not add or delete.

Consumers are only able to view project artifacts.

#### Admin Console

The admin console allows a superuser the ability to create, modify or delete any object in the repository. It is advised that a superuser only perform these actions where absolutely necessary and where the ramifications of such an action are fully understood.

For general information on the Django admin console, see: https://docs.djangoproject.com/en/3.2/ref/contrib/admin/

#### Search

Any user in Documendous can use the search functionality.

Currently, search functionality includes:

* Full text search on documents
* Field search on documents and folders

By default, a user can only get results where the user has access to them. For example, a non-privileged user will not be able to find documents or folders created by admin in its own folder. A non-privileged user however, will be able to find documents and folders owned by others that exist in projects where the non-privileged user is a member.

#### Favorites

A user can favorite a document or folder. These will then show up in the user's favorites view. A user can also unfavorite a document or folder if it has been favorited previously by that user.

#### Trashcan

When a user clicks on the trashcan icon (delete folder/document) in the repository view, that folder/document is placed in the user's trashcan and renamed with a timestamp. In the trashcan view, the user can either permanently delete or restore the folder/document. When a document is permanently deleted from here, all metadata and the associated content file is permanently deleted with no chance of recovery.

#### My Profile

On the profile page, a user's profile info is available:

* Bio
* Location
* Position
* Slack 
* Skype
* LinkedIn URL

These can be updated in the linked update profile view.

Info like user id, username, email cannot be updated in this view and can only be done by a superuser in the admin console.

### System Maintenance

#### Backup and Restore

There are essentially two parts to a Documendous repository:

* Database (contains metadata and search data)
* Contentstore files (contains file and content)

Backing up the repository is a two part endeavor and must be done in the following order to keep integrity:

1. Backup database
2. Backup contentstore files (/app/documendous/docrepo/contentfiles)

For information regarding backup/restore of Postgresql, see: https://www.postgresql.org/docs/current/backup.html
For backing up contentstore files, you can use whichever file system backup tool you like. Just ensure that at the least /app/documendous/docrepo/contentfiles is backed up.

### Removing Phoenix Project Demo

Clean removal of Phoenix Project and related artifacts:

1. Log in as "admin" user into the admin console.

2. Locate project called Phoenix Project and delete it.

3. In the UI, recycle former project home folder (send to admin's trashcan folder).

4. In the admin trashcan folder, permanently delete the project home folder.

5. In the admin console, remove project users (billpalmer, brentgeller, chrisallers, dicklandry, johnpesche, maggielee, pattymckee, sarahmoulton, wesdavis)
6. Optional: In the admin console, look for Orphan Content File and delete all files there.

Note: Orphan content files are actual file system content files that are left over when all metadata and referenced models have been deleted. There are no scripts to fully delete content provided by Documendous. You will need to create a method that works for your organization to do this.
 