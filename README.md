# phidias

PytHon Interactive Declarative Intelligent Agent System
=======================================================

### 1. Installation

---------------
Go in the main dir:

```bash
$ cd phidias
```



#### 1.1 Unix

On unix systems it is possible to install the tool in two ways:

1. Use `setup.py`:

   ```bash
   $ sudo python3 setup.py install
   ```

    The following packages are also needed:

     * [readline](https://pypi.org/project/gnureadline/)
     * [parse](https://pypi.org/project/parse/)

2. Use `setup.cfg`:

   ```bash
   $ pip install -e .[unix]
   ```



#### 1.2 Windows

On Windows it is possible to install the tool using `setup.cfg`:

```bash
$ pip install -e .[win]
```

This command also works with [conda](https://docs.conda.io/en/latest/).



>  **Please note:**
>
> [readline](https://pypi.org/project/gnureadline/) doesn't work with Windows, so the alternative [pyreadline3](https://pypi.org/project/pyreadline3/) was used.




### 2. Testing

----------
You can enter the "sample" directory and run some tests.

"factorial.py" is a program which computes the factorial of a number using PHIDIAS plans. Run it using:

```bash
$ python3 factorial.py
```

The PHIDIAS shell will be displayed. Now enter

```tex
eShell: main > fact(10)
```

The program will compute the factorial of 10 and will show:

```tex
the resuilting factorial is  3628800
```

