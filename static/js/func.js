function showIm(pathIm){
    document.getElementById('Image').src='static/data/'+pathIm;
}

function postServer(prop, event){
    var xhttp = new XMLHttpRequest();
    var grade = {'1':'grade A', '2':'grade B', '3':'grade C', '0':'N', '-1':'_'}
    text = "?index="+prop.index+"&code="+event.key+"&path="+prop.path;
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var message = JSON.parse(this.responseText);
            if(Boolean(message.finish)){
                console.log("finish")
                window.location.assign("/finish")
            }
            oldIndex = prop.index;
            oldLen = prop.len;
            prop.index = message.index;
            prop.rank = message.rank;
            prop.path = message.path;
            prop.len = message.len;
            showIm(prop.path)
            var labelText1="<div class='column side1'>"+oldIndex+"/"+oldLen+"</br>"+grade[message.oldRank]+"</div>"
            var labelText2="<div class='column side2'>"+prop.index+"/"+message.len+"</br>"+grade[prop.rank]+"</div>"
            document.getElementById('label').innerHTML=labelText1+labelText2;
            console.log(message)
        }
    };
    xhttp.open("GET", "/get"+text, true);
    xhttp.send();
}

function save(){
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/work/save", true);
    xhttp.send();
}

function autoSave(time){
    setInterval(save, time);
}
