var iotsn = '{{ iotsn }}';
var user = '{{user}}';
var appurl = "/api/method/iot_ui.ui_api.iot_applist?sn="+iotsn;
var table = jQuery('#example').DataTable({
    "dom": 'lfrtp',
    //"bInfo" : false,
    //"pagingType": "full_numbers" ,
    "bStateSave": true,
    "sPaginationType": "full_numbers",
    "iDisplayLength" : 25,
    "ajax": {
        "url": appurl,
        "dataSrc": "message",
    },
    "oLanguage": {
        "sLengthMenu": "每页显示 _MENU_",
        "sSearch": "搜索:",
         "sZeroRecords": "没有匹配结果",
        "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
        "sInfoEmpty": "没有数据",
        "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
        "oPaginate": {
                    "sFirst": "|<<",
                    "sPrevious": "<",
                    "sNext": ">",
                    "sLast": ">>|"
                    },
        "sZeroRecords": "没有检索到数据",
        },
    "columns": [
        {"data": "name"},
        {"data": "cloudname"},
        {"data": "iot_ver"},
        {"data": "cloud_ver"},
        {"data": "owner"},
        {"data": null},
    ],
    columnDefs: [{
    //   指定第最后一列
    targets: 5,
    render: function(data, type, row, meta) {
        isowner = data.owner.localeCompare(user);
        // console.log(data.cloud_ver>data.iot_ver && isowner==0);
        if(data.cloud_ver>data.iot_ver && isowner==0){
            return '<div class="btn btn-white btn-warning btn-bold" id="app-update">'
            +'<i class="ace-icon fa fa-line-chart bigger-120 orange"></i>'
            +'更新到最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-editor">'
            +'<i class="ace-icon fa fa-line-chart bigger-120 green"></i>'
            +'编辑'
            +'</div>'
        }
        else if((data.cloud_ver>data.iot_ver && isowner!==0)){
            return '<div class="btn btn-white btn-warning btn-bold" id="app-update">'
            +'<i class="ace-icon fa fa-line-chart bigger-120 orange"></i>'
            +'更新到最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-fork">'
            +'<i class="ace-icon fa fa-line-chart bigger-120 green"></i>'
            +'复刻'
            +'</div>'
        }
        else if((data.cloud_ver<=data.iot_ver && isowner==0)){
            return '<div class="btn btn-white btn-bold">'
            +'<i class="ace-icon fa fa-line-chart bigger-120"></i>'
            +'已经是最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-editor">'
            +'<i class="ace-icon fa fa-line-chart bigger-120 green"></i>'
            +'编辑'
            +'</div>'
        }

        else{
            return '<div class="btn btn-white btn-bold">'
            +'<i class="ace-icon fa fa-line-chart bigger-120"></i>'
            +'已经是最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-fork">'
            +'<i class="ace-icon fa fa-line-chart bigger-120 green"></i>'
            +'复刻'
            +'</div>'
        }
    }
}]

});


function check_reslut() {
    
}


    
$(document).ready(function() {

    $.get("/api/method/iot_ui.ui_api.iot_applist?sn="+iotsn, function (r) {
        //console.log(r.message);
        if(r.message){
            //console.log(filter);
             $('#no_data').addClass("hide");
             $('#table_area').removeClass("hide");
            table.ajax.url(appurl).load();
        }
        else{
             $('#no_data').removeClass("hide");
             $('#table_area').addClass("hide");
        }

    });

    $('#table-refresh').click(function() {
        console.log(appurl);
        table.ajax.url(appurl).load();
    });


    $('#example tbody').on( 'click', 'div#app-update', function () {
        $(this).attr("disabled", true);
        var data = table.row($(this).parents('tr')).data();
        if(data){
            console.log(data.name,data.cloudname, data.cloud_ver);
            var update_app = {
                    "device": iotsn,
                    "id": iotsn+"-app_update",
                    "data": {
                        "inst": data.name,
                        "fork": 1,
                        "name": data.cloudname,
                        "version": data.cloud_ver,
                        }
                };

            $.ajax({
                type: 'POST',
                url: "/api/method/iot.device_api.app_upgrade",
                Accept: "application/json",
                contentType: "application/json",
                data: JSON.stringify(update_app),
                dataType: "json",
                success: function(r) {
                    if(r.message){
                        console.log(r);
                        table.ajax.url(appurl).load();
                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });


        }

    } );


        $('#example tbody').on( 'click', 'div#app-editor', function () {
        var data = table.row($(this).parents('tr')).data();
        if(data){
            var url = "/app_editor?app=" + data.cloudname + "&device=" + iotsn + "&app_inst=" + data.name + "&version=" + data.iot_ver;
            window.open(url);

        }

    } );
});