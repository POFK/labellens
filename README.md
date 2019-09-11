### install
```
git clone https://github.com/POFK/labellens.git
cd labellens
pip install -r requirements.txt
```

### usage
This script is used to label png files. When use it, you should put the png data in `static/` directory and run the script by
```
python main.py
```
Then open http://127.0.0.1:5000/ in your browser.

### configuration

#### init database
flask db init
flask db migrate -m "init"
flask db upgrade

#### key map
| key          |  result            |
| ------------ | -------------------|
| `1`          | label as 1 (grade A)|
| `2`          | label as 2 (grade B)|
| `3`          | label as 3 (grade C)|
| `0`          | label as 0 (nonlens)|
| `j`          | show next image    |
| `k`          | show previous image|

Note that, when you press `j` or `k`, if the image has not been labelled, is will be labelled as `0`, otherwise the original value will be reserved.

### add label
After configuration, you can label image in http://127.0.0.1:5000/workspace
<img  border="0" src="./exam/1.png" style="text-align:center;">
