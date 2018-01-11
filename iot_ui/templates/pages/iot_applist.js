function isNull(arg1)
{
 return !arg1 && arg1!==0 && typeof arg1!=="boolean"?true:false;
}

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
        if(data.owner){
            isowner = data.owner.localeCompare(user);
        }
        else{
            isowner = 1
        }
        // console.log(data.cloud_ver>data.iot_ver && isowner==0);
        if(isNull(data.cloud_ver) && isNull(data.owner)){
            return '<div class="btn btn-white btn-warning btn-bold">'
            +'<i class="ace-icon fa  fa-leaf  bigger-120 orange"></i>'
            +'本地应用'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-del">'
            +'<i class="ace-icon fa fa-trash  bigger-120 green"></i>'
            +'删除'
            +'</div>'
        }
        else if(data.cloud_ver>data.iot_ver && isowner==0){
            return '<div class="btn btn-white btn-warning btn-bold" id="app-update">'
            +'<i class="ace-icon fa fa-cloud-upload  bigger-120 orange"></i>'
            +'升级最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-editor">'
            +'<i class="ace-icon fa fa-edit bigger-120 green"></i>'
            +'编辑'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-del">'
            +'<i class="ace-icon fa fa-trash  bigger-120 green"></i>'
            +'删除'
            +'</div>'
        }
        else if((data.cloud_ver>data.iot_ver && isowner!==0)){
            return '<div class="btn btn-white btn-warning btn-bold" id="app-update">'
            +'<i class="ace-icon fa fa-cloud-upload  bigger-120 orange"></i>'
            +'升级最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-fork">'
            +'<i class="ace-icon fa fa-clone  bigger-120 green"></i>'
            +'复刻'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-del">'
            +'<i class="ace-icon fa fa-trash  bigger-120 green"></i>'
            +'删除'
            +'</div>'
        }
        else if((data.cloud_ver<=data.iot_ver && isowner==0)){
            return '<div class="btn btn-white btn-bold">'
            +'<i class="ace-icon fa fa-thumbs-up bigger-120"></i>'
            +'已是最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-editor">'
            +'<i class="ace-icon fa fa-edit bigger-120 green"></i>'
            +'编辑'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-del">'
            +'<i class="ace-icon fa fa-trash  bigger-120 green"></i>'
            +'删除'
            +'</div>'
        }

        else{
            return '<div class="btn btn-white btn-bold">'
            +'<i class="ace-icon fa fa-thumbs-up bigger-120"></i>'
            +'已是最新'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-fork">'
            +'<i class="ace-icon fa fa-clone  bigger-120 green"></i>'
            +'复刻'
            +'</div>'
            +'<div class="btn btn-white btn-warning btn-bold" id="app-del">'
            +'<i class="ace-icon fa fa-trash  bigger-120 green"></i>'
            +'删除'
            +'</div>'
        }
    }
}]

});

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

var appstoreurl = "/api/method/iot_ui.ui_api.appstore_applist";
var appstore_table = jQuery('#appstore_table').DataTable({
    "dom": 'lfrtp',
    //"bInfo" : false,
    //"pagingType": "full_numbers" ,
    "bStateSave": true,
    "sPaginationType": "full_numbers",
    "iDisplayLength" : 25,
    "ajax": {
        "url": appstoreurl,
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
        {"data": "app_name"},
        {"data": "protocol"},
        {"data": "device_supplier"},
        {"data": "category"},
        {"data": "name"},
        {"data": "modified"},
        {"data": "star"},
        {"data": null},
    ],
    columnDefs: [{
    //   指定第最后一列
    targets: 7,
    render: function(data, type, row, meta) {
        return '<div class="btn btn-white btn-bold" id="install-to-box">'
            + '<i class="ace-icon fa fa-cloud-download bigger-120"></i>'
            + '安装'
            + '</div>'

        // var boxdata = table.data();
        // var installed_apps = new Array()
        // for (var i = 0; i < boxdata.length; i++) {
        //     installed_apps.push(boxdata[i].cloudname)
        // }
        // console.log(data.name);
        // console.log(installed_apps);
        // console.log($.inArray(data.name, installed_apps))
        // if ($.inArray(data.name, installed_apps) != -1) {
        //     return '<div class="btn btn-white btn-bold">'
        //         + '<i class="ace-icon fa fa-thumbs-up bigger-120"></i>'
        //         + '已安装'
        //         + '</div>'
        // }
        // else{
        //     return '<div class="btn btn-white btn-bold" id="install-to-box">'
        //         + '<i class="ace-icon fa fa-cloud-download bigger-120"></i>'
        //         + '安装'
        //         + '</div>'
        // }

    }
}]

});


function check_reslut() {
    
}

$(document.body).css({"overflow-y":"scroll" });
    
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


    $('#example tbody').on( 'click', 'div#app-fork', function () {
        $(this).attr("disabled", true);
        var data = table.row($(this).parents('tr')).data();
        if(data){
            console.log(data.name,data.cloudname, data.cloud_ver);
            var fork_app = {
                    "app": data.cloudname,
                    "version": data.cloud_ver
                };

            $.ajax({
                type: 'POST',
                url: "/api/method/app_center.appmgr.fork",
                contentType: "application/x-www-form-urlencoded;charset=utf-8",
                data: for_app,
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

    $('#example tbody').on( 'click', 'div#app-del', function () {
        var data = table.row($(this).parents('tr')).data();
        if(data){

            var del_app = {
                    "device": iotsn,
                    "id": iotsn+"-app_del",
                    "data": {
                        "inst": data.name,
                        }
                };

            $.ajax({
                type: 'POST',
                url: "/api/method/iot.device_api.app_uninstall",
                Accept: "application/json",
                contentType: "application/json",
                data: JSON.stringify(del_app),
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



    $('#iot-add-newapp-btn').click(function(){
        console.log("show add-app");
        $('#iot-add-newapp').removeClass("hide");
        $('#iot-app-list').addClass("hide");
    } );


    $('#iot-add-newapp-close-btn').click(function(){
        console.log("show app-list");
        $('#iot-app-list').removeClass("hide");
        $('#iot-add-newapp').addClass("hide");
    } );



    $('#mytest-btn').click(function(){
        var data=table.data();
        var installed_apps = new Array()
        for(var i = 0; i < data.length; i++){
            installed_apps.push(data[i].cloudname)
       }
       console.log(installed_apps);

    } );


    $('#switch-mode').click(function(){
            var url = "/iot_devinfo/" + iotsn;
            window.location.href=url;
    } );


    $('#appstore_table tbody').on( 'click', 'div#install-to-box', function () {
        $(this).attr("disabled", true);
        var data = appstore_table.row($(this).parents('tr')).data();
        if(data){
            var update_app = {
                    "device": iotsn,
                    "id": iotsn+"-app_install",
                    "data": {
                        "inst": makeid(),
                        "name": data.name,
                        "version": "latest",
                        }
                };

            $.ajax({
                type: 'POST',
                url: "/api/method/iot.device_api.app_install",
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




});