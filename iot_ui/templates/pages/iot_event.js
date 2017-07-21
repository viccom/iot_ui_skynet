$(document).ready(function() {
    var rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter=all";
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
            "sLengthMenu": "每页显示 _MENU_ 条记录",
             "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": "没有数据",
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "oPaginate": {
                        "sFirst": "首页",
                        "sPrevious": "前一页",
                        "sNext": "后一页",
                        "sLast": "尾页"
                        },
            "sZeroRecords": "没有检索到数据",
            },
        "columns": [
            {"data": "device"},
            {"data": "error_type"},
            {"data": "error_key"},
            {"data": "error_level"},
            {"data": "brief"}


        ]
    });





    $('#table-refresh').click(function() {
        table.ajax.url(rtvalueurl).load();
    });
    $('#table-all').click(function() {
        rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=all";
        table.ajax.url(rtvalueurl).load();
    });
    $('#table-online').click(function() {
        rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=online";
        table.ajax.url(rtvalueurl).load();
    });
    $('#table-offline').click(function() {
        rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=offline";
        table.ajax.url(rtvalueurl).load();
    });
    $('#table-offline_7d').click(function() {
        rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array?filter=offline_7d";
        table.ajax.url(rtvalueurl).load();
    });




});