function format(source, params) {
    $.each(params,function (i, n) {
        source = source.replace(new RegExp("\\{" + i + "\\}", "g"), n);
    })
    return source;
}

function showIm(mess){
    var text = "<h4><b>Image {0}:&nbsp&nbsp  id: {1} &nbsp&nbsp label: {2} &nbsp&nbsp input: {3}</b></h4>"
    document.getElementById('Image').src='static/data/'+mess.path;
    document.getElementById('caption').innerHTML = format(text,[mess.path, mess.id, mess.label, mess.key]);
}

function my_alert(id, text){
    $(id).html(text).removeClass("hide").hide().fadeIn("slow").delay(3000).queue(function(){
        $(this).addClass("hide").dequeue();
    })
}


function postToServer(event){
    $.ajax({
           type: "POST",
           url: Flask.url_for("workspace")+"/control_"+event.key,
           success: function (resp, status, xhr) {
               if(resp.last) {
                   my_alert("#image_alert","This is the last image!");
               }
               showIm(resp);
           }
    });
}

function autoSave(time){
    setInterval(save, time);
}

function download(btn, url){
    $(document).ready(function(){
        $(btn).click(function(){
            $.ajax({
                   type: "POST",
                   url: url,
                   success: function (resp, status, xhr) {
                       window.location.href = url;
                   }
            });
        })
    })

}

function image_init(){
    $.ajax({
           type: "POST",
           url: Flask.url_for("workspace")+"/control_init",
           success: function (resp, status, xhr) {
               showIm(resp);
           }
    });
}

function btncallfilter(btn, url){
    $(document).ready(function(){
        $(btn).click(function(){
            $.ajax({
                   type: "POST",
                   url: url,
                   success: function (resp, status, xhr) {
                       $('#filter-name').html($(btn).html());
                       image_init();
                       if(resp.message) {
                           my_alert("#image_alert2", resp.message);
                       }
                   }
            });
        })
    })
}

function update_progress(){
    $.ajax({
           type: "POST",
           url: Flask.url_for("workspace")+"/progress",
           success: function (resp, status, xhr) {
               $('#p-bar').attr('aria-valuenow',resp.frac).attr('style',"width:"+resp.frac+"%").html(resp.frac+"% Completed");
           }
    });
}

