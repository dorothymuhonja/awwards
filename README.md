# awwards

### By Dorothy Muhonja

### Description 
A web app where a user can rate different websites

### Set Up Instruction
* Python 3.6 and above
* Editor
* Virtual environment (optional)
*  Django
* djangorestframework
* SQLAlchemy (Postgres)

## Technologies used
* Python3
* Django
* css3
* html5
* Bootstrap4


## Installation and setup
 Clone this repo
 ```
 git clone https://github.com/dorothymuhonja/awwards.git
 ```

 ### Create and activate a virtual environment
 
    virtualenv venv --python=python3

    source venv/bin/activate

### Install django
    pip install django (and other dependencies required)

### Copy environment variable
    cp env.sample .env

### Load/refresh .environment variables
    source .env

### Running the app
```
python3 manage.py runserver
```
## Behaviour Driven Development (BDD)
#### User
* Create and account and Login
* User can add a website to be rated
* User can rate projects based on the following criteria
    * Design
    * Usability
    * Content
* User can like and comment on the websites posted

#### Admin
* Can add, change or delete the websites
* Can delete a user


## Email Address
dorothymuhonja7@gmail.com

## License and Copyright

Copyright (c) 2021 Dorothy Muhonja

[MIT License](LICENSE)