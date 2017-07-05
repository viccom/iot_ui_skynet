$(document).ready(function() {
    $('[data-rel=tooltip]').tooltip();
    var $curdevsn = ""
    var rtvalueurl = "/api/method/iot_ui.ui_api.devices_list_array";
    var table = jQuery('#example').DataTable({
        "dom": 'lfrtp',
        //"bInfo" : false,
        //"pagingType": "full_numbers" ,
        "bStateSave": true,
        "sPaginationType": "full_numbers",
        "iDisplayLength" : 25,
        "ajax": {
            "url": "",
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
            {"data": "device_sn"},
            {"data": "device_company"},


        ]
    });

    $('#headquarters').click(function(){
        $('#structure-list').addClass("hide");
        $('#member-list').addClass("hide");
        $('#add-group').removeClass("hide");
        $('#add-member').addClass("hide");

        $('#btn-confirm').removeClass("hide");
        $('#btn-reset').removeClass("hide");
        $('#btn-modify').addClass("hide");

        $('#add-group-head').text("新增组");
        $('#add-group-title').text("定义组名");

    } );

     $('#btn-confirm').click(function(){
        var newgroupname =  $('#new-group-name').val();
        if(newgroupname){
            console.log(newgroupname, newgroupname.length);
        }
    } );

     $('#btn-modify').click(function(){
        var newgroupname =  $('#new-group-name').val();
        if(newgroupname){
            console.log(newgroupname, newgroupname.length);
        }
    } );

    $('#add-group-close').click(function(){
        $('#add-group').addClass("hide");
        $('#structure-list').removeClass("hide");
        $('#member-list').removeClass("hide");
        $('#add-member').addClass("hide");
    } );

    $('#add-members-to-company').click(function(){
        $('#structure-list').addClass("hide");
        $('#add-group').addClass("hide");
        $('#member-list').addClass("hide");
        $('#add-member').removeClass("hide");

        $('#add-member-head').text("新增成员");
    } );

    $('#del-members-to-company').click(function(){
        $('#structure-list').addClass("hide");
        $('#add-group').addClass("hide");
        $('#member-list').addClass("hide");
        $('#add-member').removeClass("hide");

        $('#add-member-head').text("删除成员");
    } );

    $('#add-member-close').click(function(){
        $('#add-group').addClass("hide");
        $('#structure-list').removeClass("hide");
        $('#member-list').removeClass("hide");
        $('#add-member').addClass("hide");
    } );

    $.widget("ui.dialog", $.extend({}, $.ui.dialog.prototype, {
        _title: function(title) {
            var $title = this.options.title || '&nbsp;'
            if( ("title_html" in this.options) && this.options.title_html == true )
                title.html($title);
            else title.text($title);
        }
    }));

    $("body").on("click", "div .branch-desc", function() {
            var dataid = $(this).attr("data-id");
            console.log(dataid);

        });

    $("body").on("click", "div .branch-del", function() {
        var dataid = $(this).attr("data-id");
        var selectdiv = $(this).parent();
        var selectdivbrother = $(this).parent().prev();
        console.log(dataid);

            $( "#dialog-confirm" ).removeClass('hide').dialog({
                resizable: false,
                width: '320',
                modal: true,
                title: "<div class='widget-header'><h4 class='smaller'><i class='ace-icon fa fa-exclamation-triangle red'></i> Delete the group?</h4></div>",
                title_html: true,
                buttons: [
                    {
                        html: "<i class='ace-icon fa fa-trash-o bigger-110'></i>&nbsp; Delete",
                        "class" : "btn btn-danger btn-minier",
                        click: function() {
                            $( this ).dialog( "close" );
                        }
                    }
                    ,
                    {
                        html: "<i class='ace-icon fa fa-times bigger-110'></i>&nbsp; Cancel",
                        "class" : "btn btn-minier",
                        click: function() {
                            $( this ).dialog( "close" );
                        }
                    }
                ]
            });

     });


        $("body").on("click", "div .branch-edit", function() {
            var dataid = $(this).attr("data-id");
            var selectdiv = $(this).parent();
            var selectdivbrother = $(this).parent().prev();
            console.log(dataid);
            $('#structure-list').addClass("hide");
            $('#member-list').addClass("hide");
            $('#add-group').removeClass("hide");
            $('#add-member').addClass("hide");

            $('#btn-confirm').addClass("hide");
            $('#btn-reset').addClass("hide");
            $('#btn-modify').removeClass("hide");

            $('#add-group-head').text("修改组名");
            $('#add-group-title').text("定义新组名");
        });

    var demo1 = $('select[name="duallistbox_demo1[]"]').bootstrapDualListbox({infoTextFiltered: '<span class="label label-purple label-lg">Filtered</span>'});
    var container1 = demo1.bootstrapDualListbox('getContainer');
    container1.find('.btn').addClass('btn-white btn-info btn-bold');

    $("#btn-add-members").click(function () {
        var memberlists = $('[name="duallistbox_demo1[]"]').val();
        if(memberlists){
            console.log(memberlists, memberlists.length);
        }
   });

    $("#btn-cancel").click(function () {
        $('#add-group').addClass("hide");
        $('#structure-list').removeClass("hide");
        $('#member-list').removeClass("hide");
        $('#add-member').addClass("hide");
   });
});