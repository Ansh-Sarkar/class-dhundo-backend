# Class Dhundo (Backend)

**Class Dhundo** was made with the intention of making it easier for you to generate your timetables in a hassle free, quick and efficient manner without requiring to parse through the long excel sheets provided to you by the university. This repository holds the code for the backend of the routine generation application. Here are some useful links that you may want to refer to.

- [x] [Pycco Documentation](https://github.com/Ansh-Sarkar/class-dhundo-backend/tree/main/docs)
- [x] [Link to Frontend Code](https://github.com/Ansh-Sarkar/class-dhundo-frontend)

## Requirements

- [x] Flask
- [x] Python >= 3.9
- [x] Developed on Ubuntu 22.04


## Setting up Virtual Environment

<br>

**Venv** is a tool that creates an isolated environment separate from other projects. Creating a virtual environment allows us to work on a Python project without affecting other projects that also use Python and their dependencies.

<br>

Install **pip** first
```bash
sudo apt-get install python3-pip
```

Then install **venv**
```bash
sudo apt install python3-venv
```

Now create a virtual environment 
```bash
python3 -m venv {name_of_virtual_environment}
```
  
Activate your virtual environment:    
```bash
source {name_of_virtual_environment}/bin/activate
```

Install all dependencies from ```requirements.txt```
```bash
pip3 install -r requirements.txt
```

To deactivate:
```bash
deactivate
```

Run the project using ```uvicorn``` by executing the following command
```bash
uvicorn main:app --reload
```

Run ```Flask``` project within the virtual environment by executing the following command
```bash
flask run
```

<br>