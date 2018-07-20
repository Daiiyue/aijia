function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$.get("/api/v1_0/user/auth",function (resp) {
    if (resp.errno == 0){
        real_name=resp.data.real_name;
        id_card=resp.data.id_card;
        $("#real-name").val(real_name).prop("disabled", true);
        $("#id-card").val(id_card).prop("disabled", true);
        $("#form-auth>input[type=submit]").hide();
    }
});

$("#form-auth").submit(function (e) {
    e.preventDefault();
    real_name=$("#real-name").val();
    id_card=$("#id-card").val();

    if (!real_name){
        alert("请输入真实姓名");
        return
    }

    if (!id_card){
        alert("请输入身份证号");
        return
    }

    var req_data = {
        real_name:real_name,
        id_card:id_card
    };

    req_json = JSON.stringify(req_data);

    $.ajax({
        url:"/api/v1_0/user/auth",
        type:"post",
        contentType:"application/json",
        data:req_json,
        dataType:"json",
        headers:{
            "X-CSRFToken": getCookie("csrf_token")
        },success:function (resp) {
            if (resp.errno == 0) {
            $(".error-msg").hide();
            showSuccessMsg();
            $("#real-name").prop("disabled", true);
            $("#id-card").prop("disabled", true);
            $("#form-auth>input[type=submit]").hide();
            }
        }
    });

})

