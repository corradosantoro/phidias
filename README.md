<a name="readme-top"></a>

<br />
<div align="center">
  <a href="https://github.com/corradosantoro/phidias">
    <img src=".github/images/arslogo.png" alt="arslogo">
  </a>
<h3 align="center">PHIDIAS</h3>

  <p align="center">
    <b>P</b>yt<b>H</b>on <b>I</b>nteractive <b>D</b>eclarative <b>O</b>ntelligent <b>A</b>gent <b>S</b>ystem<br/>by <a href="https://github.com/corradosantoro">Prof. Santoro Corrado</a></p>
</div>

-------

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#install">Install</a>
      <ul>
        <li><a href="#pythonic-way-for-linux-windows-macos">Pythonic Way for Linux-Windows-macOS</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
    </li>
  </ol>
</details>

<br/>

## Install

First of all, you need to download this repository on your machine. You can download this repository as a zip file or use __git clone__ command:

      git clone https://github.com/corradosantoro/phidias

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Pythonic Way for Linux-Windows-macOS

We are going to create a __virtual environment__ to contains all the dependencies.

1. Install [Python 3](https://www.python.org/) on your system, at the time of writing it is recommended Python 3.9 or newer:

   - _Linux (Debian-based)_:
     ```bash
     sudo apt install python3 python3-pip
     ```
   - _Linux (RHEL-based)_:
     ```bash
     sudo dnf install python3 python3-pip
     ```
   - _Windows and macOS_:

         Use the proper installer provided on the official Python website
2. Create a virtual environment, open a terminal inside the `RoboticSystems` folder and execute the following command:

        python -m venv ./venv
3. Activate the virtual environment:

   - _Linux (bash shell) or macOS_:
     ```bash
     source ./venv/bin/activate
     ```
   - _Windows_ (cmd.exe):
     ```batch
     ./venv/Scripts/activate.bat
     ```
4. Install the library and the related dependencies using:

       python setup.py install

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Usage

Before running any script you need to activate the virtual environment containing the required dependencies:

- _Linux (bash shell) or macOS_:
  ```bash
  source ./venv/bin/activate
  ```
- _Windows_ (cmd.exe):
  ```batch
  ./venv/Scripts/activate.bat
  ```

You can now run any provided sample, example:

```bash
python ./samples/factorial.py
```

The PHIDIAS shell will be displayed, you can type the following command:

```
eShell: main > fact(10)
```

The program will compute the factorial of 10 and will show:

```
the resuilting factorial is 3628800
```