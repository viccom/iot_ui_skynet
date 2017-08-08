    var filter = '{{ filter }}';
    var rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter="+filter;
    var table = jQuery('#example').DataTable({
        "dom": 'lfrtp',
        //"bInfo" : false,
        //"pagingType": "full_numbers" ,
        "bStateSave": true,
        "sPaginationType": "full_numbers",
        "iDisplayLength" : 25,
        "ajax": {
            "url": rtvalueurl,
            //"url": "/api/method/tieta.tieta.doctype.cell_station.cell_station.list_station_map",
            "dataSrc": "message",
        },
        "oLanguage": {
            "sLengthMenu": "每页显示 _MENU_",
             "sZeroRecords": "抱歉， 没有找到",
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
            {"data": "device_name"},
            {"data": "device_desc"},
            {"data": "device_status"},
            {"data": "last_updated"},
            {"data": "device_sn"},
            {"data": "device_company"},
        ],
        'rowCallback': function(row, data, dataIndex){
         // Get row ID
         if(data.device_status=="ONLINE"){
             $(row).addClass('green');
         }
         else if(data.device_status=="OFFLINE"){
             $(row).addClass('red');
         }
      }
    });

$(document).ready(function() {

    $('#table-'+filter).addClass("btn-primary");
    var $curdevsn = "";

    $.get("/api/method/iot_ui.ui_api.devices_list_array?filter=len_"+filter, function (r) {
        //console.log(r.message);
        if(r.message){
            //console.log(filter);
             $('#no_data').addClass("hide");
             $('#table_area').removeClass("hide");
            var rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter="+filter;
            table.ajax.url(rtvalueurl).load();
        }
        else{
             $('#no_data').removeClass("hide");
             $('#table_area').addClass("hide");
        }

    });


    $('#example tbody').on('click', 'tr td:nth-child(n+2)', function (e) {
        var data = table.row( this ).data();
        if(data){

            $curdevsn = data['device_sn'];
            console.log($curdevsn);
            var url = "/iot_devinfo/" + $curdevsn;
            window.location.href=url;

        }
    } );

    $('#table-refresh').click(function() {
        table.ajax.url(rtvalueurl).load();
    });
    $('#table-all').click(function() {
        $('#table-all').addClass("btn-primary");
        $('#table-all').siblings().removeClass("btn-primary");
        $.get("/api/method/iot_ui.ui_api.devices_list_array?filter=len_all", function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=all";
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });
    $('#table-online').click(function() {
        $('#table-online').addClass("btn-primary");
        $('#table-online').siblings().removeClass("btn-primary");
        $.get("/api/method/iot_ui.ui_api.devices_list_array?filter=len_online", function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=online";
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });
    $('#table-offline').click(function() {
        $('#table-offline').addClass("btn-primary");
        $('#table-offline').siblings().removeClass("btn-primary");
        $.get("/api/method/iot_ui.ui_api.devices_list_array?filter=len_offline", function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=offline";
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });
    $('#table-offline_7d').click(function() {
        $('#table-offline_7d').addClass("btn-primary");
        $('#table-offline_7d').siblings().removeClass("btn-primary");
        $.get("/api/method/iot_ui.ui_api.devices_list_array?filter=len_offline_7d", function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=offline_7d";
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });

});