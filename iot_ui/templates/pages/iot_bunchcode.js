    console.log($('meta[name="csrf-token"]').attr('content'));

//设置AJAX的全局默认选项
$.ajaxSetup( {

    headers: { // 默认添加请求头
        //"X-Frappe-CSRF-Token": $('meta[name="csrf-token"]').attr('content'),
        "X-Frappe-CSRF-Token": "{{csrf_token}}",
        "Powered-By": "CodePlayer"
    }
} );


$(document).ready(function() {

    $('#add_bunch_code').click(function(){

        $.post("/api/method/iot_ui.ui_api.add_own_bunch_code", {}, function(data) {
          console.log(data);
          if(data.message.result == "sucessful"){
                 $("#own-bunchcode").append('<div class="col-xs-6 col-sm-6 profile-info-value">'
                + data.message.code
                + '</div>'
                + '<div class="col-xs-6 col-sm-6 profile-info-value">'
                    + '<div class="btn btn-white btn-warning btn-bold bunchcode"  data-bunchcode="'+ data.message.code +'">'
                        + '<i class="ace-icon fa fa-trash-o smaller-90"></i>Delete'
                    + '</div>'
                + '</div>');
          }


        }, 'json');

        console.log("Post Completely");

    } );

        $("body").on("click", "div .add_group-bunch_code", function(){

            groupid = $(this).parent().parent().attr("data-groupid");

        $.post("/api/method/iot_ui.ui_api.add_group_bunch_code?groupid="+groupid, {}, function(data) {
          console.log(data);
          if(data.message.result == "sucessful"){
                 $("#"+groupid).append('<div class="col-xs-6 col-sm-6 profile-info-value">'
                + data.message.code
                + '</div>'
                + '<div class="col-xs-6 col-sm-6 profile-info-value">'
                    + '<div class="btn btn-white btn-warning btn-bold bunchcode"  data-bunchcode="'+ data.message.code +'">'
                        + '<i class="ace-icon fa fa-trash-o smaller-90"></i>Delete'
                    + '</div>'
                + '</div>');
          }


        }, 'json');

        console.log("Post Completely");

    } );

/*    $("div .bunchcode").on("click", function() {
        console.log("%^&YUH");
    var bunchcode = $(this).attr("data-bunchcode");
    var selectdiv = $(this).parent();
    var selectdivbrother = $(this).parent().prev();
        $.post("/api/method/iot_ui.ui_api.del_own_bunch_code?bunch_code="+bunchcode, {}, function(r) {
            console.log(r.message);
          if(r.message.result == "sucessful"){
              console.log(selectdiv);
            selectdivbrother.remove();
            selectdiv.remove();
          }
        }, 'json');
 });*/

    $("body").on("click", "div .bunchcode", function() {
        var bunchcode = $(this).attr("data-bunchcode");
        var selectdiv = $(this).parent();
        var selectdivbrother = $(this).parent().prev();
            //console.log(selectdivbrother);
            $.post("/api/method/iot_ui.ui_api.del_bunch_code?bunch_code="+bunchcode, {}, function(r) {
              console.log(r.message);
              if(r.message.result == "sucessful"){
                selectdivbrother.remove();
                selectdiv.remove();
              }
              else{
                  $.gritter.add({
						title: '删除绑定码错误',
						text: r.message.reason,
						class_name: 'gritter-error gritter-light'
					});
              }
            }, 'json');
     });


});