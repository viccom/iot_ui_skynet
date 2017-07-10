$(document).ready(function() {
    var $curdevsn = "";
    var filter = '{{ filter }}';
    console.log(filter);
    var $doc = $(document);
    var $tips = $('#J_tips');
    if (!$tips.length) {
      $tips = $('<div id="J_tips" class="tips hide"><ul id="menu" class="ui-menu ui-widget ui-widget-content" role="menu" tabindex="0" aria-activedescendant="ui-id-4"><li class="ui-menu-item" id="ui-id-1" tabindex="-1" role="menuitem" aria-disabled="true">数据浏览</li><li class="ui-menu-item" id="ui-id-2" tabindex="-1" role="menuitem">远程维护</li></ul></div>');
      $('body').append($tips);
    }


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
            {"data": "device_name"},
            {"data": "device_desc"},
            {"data": "device_status"},
            {"data": "last_updated"},
            {"data": "device_sn"},
            {"data": "device_company"},


        ]
    });

    $doc.on('click', function(e) {

    });

    $('#example tbody').on('click', 'tr', function (e) {
        var pageX = e.pageX, pageY = e.pageY;
        var data = table.row( this ).data();
        console.log(data);
        if(data){
          $tips.css({
            top: pageY,
            left: pageX
          });
          $tips.removeClass("hide");

            $curdevsn = data['device_sn']
            //window.location.href="/S_Station_infox/"+data['name'];
            //alert( 'You clicked on '+data[0]+'\'s row' );
        }
    } );

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

    $('#ui-id-1').click(function(){
        console.log(this, $curdevsn);
        var url = "/iot_devinfo/" + $curdevsn;
        window.location.href=url;
    } );
    $('#ui-id-2').click(function(){
        console.log(this, $curdevsn);
        var url = "/iot_devinfo/" + $curdevsn;
        window.location.href=url;
    } );



    $("body").click(function(event){
        var $this = $(event.target);
        var stra =  $this[0].nodeName;
        var strb =  $this[0].id;
        console.log(stra,strb);
        if(stra!="TD" && strb!="J_tips"){
            $tips.addClass("hide");
        }
    });

});