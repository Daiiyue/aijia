function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 向后端获取城区请求
    $.get("/api/v1_0/areas",function (resp) {
        if (resp.errno == 0) {
            //     var areas = resp.data.areas;
            //     for (i=0; i < areas.length; i++){
            //         var area = areas[i];
            //         $("#area-id").append('<option value="'+area.aid+'">'+area.aname+'</option>')
            //     };
            // 使用前段模板渲染页面
            area_html = template('area-tmpl', {areas: resp.data.areas});
            $("#area-id").html(area_html);

        } else {
            alert(resp.errmsg)
        }
    });

    $("#form-house-info").submit(function (e) {
        e.preventDefault();
        var house_data = {};
        $("#form-house-info").serializeArray().map(function(x){house_data[x.name] = x.value});
        var facilities = [];
        $(":checked[name=facility]").each(function (index, x) { facilities[index] = $(x).val()});
        house_data.facility = facilities;

        $.ajax({
            url:"/api/v1_0/houses/info",
            type:"post",
            data:JSON.stringify(house_data),
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X_CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == 4101){
                    location.href="/login.html"
                } else if (resp.errno == 0){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.data.house_id);
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    })

    $("#form-house-image").submit(function (e) {
        e.preventDefault();
        $("#form-house-image").ajaxSubmit({
            url:"/api/v1_0/houses/image",
            type:"post",
            dataType:"json",
            headers:{
                "X_CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == 0){
                    // 保存图片成功
                    $(".house-image-cons").append('<img src="'+resp.data.image_url+'">')
                } else if (resp.errno == 4101) {
                    location.href = "/login.html"
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    })

})