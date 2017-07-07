//设置AJAX的全局默认选项
$.ajaxSetup( {

    headers: { // 默认添加请求头
        //"X-Frappe-CSRF-Token": $('meta[name="csrf-token"]').attr('content'),
        "X-Frappe-CSRF-Token": "{{csrf_token}}",
        "Powered-By": "CodePlayer"
    }
} );
    var selectnode = "root";
    var memberopflag = 1;
$(document).ready(function() {
    $('[data-rel=tooltip]').tooltip();
    var company = "{{company}}";
    var memberurl = '';

    ///console.log(company);

    var memberurl = "/api/method/iot_ui.ui_api.list_company_member?company="+company;
    var table = jQuery('#example').DataTable({
        "dom": 'lfrtp',
        //"bInfo" : false,
        //"pagingType": "full_numbers" ,
        "bStateSave": true,
        "sPaginationType": "full_numbers",
        "iDisplayLength" : 25,
        "ajax": {
            "url": memberurl,
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
            {"data": "member_name"},
            {"data": "member_id"},
            {"data": null},
        ],
        columnDefs: [{
        //   指定第最后一列
        targets: 2,
        render: function(data, type, row, meta) {
            return '<div class="btn btn-white btn-warning btn-bold" id="member-del">'
                +'<i class="ace-icon fa fa-trash-o bigger-120 orange"></i>'
                +'删除'
                +'</div>';
        }
    }]
    });

    $('#structure-refresh').click(function(){

            $.ajax({
                type: 'get',
                url: "/api/method/iot_ui.ui_api.list_company_group?company="+company,
                dataType: "json",
                success: function(data) {
                    if(data.message){
                        $('#group-list').empty();
                        var groups = data.message;
                        for(g in groups){
                            //console.log(groups[g].name,groups[g].group_name);
                            var newli = '<li class="dd-item dd2-item" data-id="'+groups[g].name+'">'
                            + '<div class="dd-handle dd2-handle">'
                            +    '<i class="normal-icon ace-icon fa  fa-joomla bigger-130"></i>'
                            +    '<i class="drag-icon ace-icon fa fa-arrows bigger-125"></i>'
                            +   '</div>'
                            +   '<div class="dd2-content group_name">'
                            +    '<div class="col-xs-6 branch-desc" data-id="' + groups[g].name + '" id="gp_'+groups[g].name+'">' + groups[g].group_name + '</div>'
                            +    '<div class="btn-sm pull-right branch-del" data-id="'+groups[g].name+'">'
                            +       '<i class="ace-icon fa fa-trash-o"></i>'
                            +    '</div>'
                            +    '<div class="btn-sm pull-right branch-edit" data-id="'+groups[g].name+'">'
                            +        '<i class="ace-icon fa fa-edit"></i>'
                            +    '</div>'
                            +'</div>'
                            +'</li>';
                        $('#group-list').append(newli);
                        }

                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

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
            var group = {
                "group_name": newgroupname,
                "company": company
            };

            $.ajax({
                type: 'POST',
                url: "/api/method/iot_ui.ui_api.add_company_group",
                contentType: "application/json", //必须有
                data: JSON.stringify(group),
                dataType: "json",
                success: function(data) {
                    if(data.message.result == "sucessful" ){
                        console.log("提交成功！");
                        //console.log(data.message.groups);
                        $('#add-group').addClass("hide");
                        $('#structure-list').removeClass("hide");
                        $('#member-list').removeClass("hide");
                        $('#add-member').addClass("hide");

                        $('#group-list').empty();
                        var groups = data.message.groups;
                        for(g in groups){
                            //console.log(groups[g].name,groups[g].group_name);
                            var newli = '<li class="dd-item dd2-item" data-id="'+groups[g].name+'">'
                            + '<div class="dd-handle dd2-handle">'
                            +    '<i class="normal-icon ace-icon fa  fa-joomla bigger-130"></i>'
                            +    '<i class="drag-icon ace-icon fa fa-arrows bigger-125"></i>'
                            +   '</div>'
                            +   '<div class="dd2-content group_name">'
                            +    '<div class="col-xs-6 branch-desc" data-id="' + groups[g].name + '" id="gp_'+groups[g].name+'">' + groups[g].group_name + '</div>'
                            +    '<div class="btn-sm pull-right branch-del" data-id="'+groups[g].name+'">'
                            +       '<i class="ace-icon fa fa-trash-o"></i>'
                            +    '</div>'
                            +    '<div class="btn-sm pull-right branch-edit" data-id="'+groups[g].name+'">'
                            +        '<i class="ace-icon fa fa-edit"></i>'
                            +    '</div>'
                            +'</div>'
                            +'</li>';
                        $('#group-list').append(newli);
                        }

                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

        }
    } );

     $('#btn-modify').click(function(){
        var newgroupname =  $('#new-group-name').val();

        if(newgroupname){
            //console.log(newgroupname, newgroupname.length);
            //$("#new-group-name").attr("data-options", "yyyyy");
            console.log($("#new-group-name").attr("data-options"));
            var group = {
                "group_name": newgroupname,
                "name": $("#new-group-name").attr("data-options"),
                "company": company
            };
            console.log(group);
            $.ajax({
                type: 'POST',
                url: "/api/method/iot_ui.ui_api.mod_company_group",
                contentType: "application/json", //必须有
                data: JSON.stringify(group),
                dataType: "json",
                success: function(data) {
                    if(data.message ==true ){
                        console.log("提交成功！");
                        $('#add-group').addClass("hide");
                        $('#structure-list').removeClass("hide");
                        $('#member-list').removeClass("hide");
                        $('#add-member').addClass("hide");
                        divid = "#gp_" +$("#new-group-name").attr("data-options")
                        $(divid).text(newgroupname);
                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

        }
    } );

    $('#add-group-close').click(function(){
        $('#add-group').addClass("hide");
        $('#structure-list').removeClass("hide");
        $('#member-list').removeClass("hide");
        $('#add-member').addClass("hide");
    } );


var demo1 = $('select[name="duallistbox_demo1[]"]').bootstrapDualListbox({
            infoTextFiltered: '<span class="label label-purple label-lg">过滤</span>',
            nonSelectedListLabel: '未选择的',
            selectedListLabel: '选择的',
            infoTextEmpty:'空列表',
            infoText:'一共 {0} 个',
            });
var container1 = demo1.bootstrapDualListbox('getContainer');
container1.find('.btn').addClass('btn-white btn-info btn-bold');

    $('#add-members-to-company').click(function(){
        $('#structure-list').addClass("hide");
        $('#add-group').addClass("hide");
        $('#member-list').addClass("hide");
        $('#add-member').removeClass("hide");

        $('#add-member-head').text("新增成员");
        memberopflag = 1
        if(selectnode=="root"){
              $.get("/api/method/iot_ui.ui_api.list_possible_users?company="+company, function(r){
                //$("div").html(result);
                  console.log(r.message);
                  users = r.message;
                  $("#duallist").empty();
                  for(n in users){
                      var context = '<option value="'+users[n]+'">'+users[n]+'</option>';
                      $('#duallist').append(context);
                  }
                    demo1.bootstrapDualListbox('refresh');


              });
        }
        else{
              $.get("/api/method/iot_ui.ui_api.list_company_user?company="+company, function(r){
                //$("div").html(result);
                  console.log(r.message);
                  $("#duallist").empty();

                      users = r.message;

                      $.get("/api/method/iot_ui.ui_api.list_group_user?groupid="+selectnode, function(r){
                          groupusers = r.message;

                          for(n in users){
                              if($.inArray(users[n], groupusers)==-1){
                                  var context = '<option value="'+users[n]+'">'+users[n]+'</option>';
                                  $('#duallist').append(context);
                              }

                          }
                          demo1.bootstrapDualListbox('refresh');
                      });


              });
        }

    } );

    $('#del-members-to-company').click(function(){
        $('#structure-list').addClass("hide");
        $('#add-group').addClass("hide");
        $('#member-list').addClass("hide");
        $('#add-member').removeClass("hide");

        $('#add-member-head').text("删除成员");
        memberopflag = 0

        if(selectnode=="root"){
              $.get("/api/method/iot_ui.ui_api.list_company_user?company="+company, function(r){
                //$("div").html(result);
                  console.log(r.message);
                  users = r.message;
                  $("#duallist").empty();
                  for(n in users){
                      var context = '<option value="'+users[n]+'">'+users[n]+'</option>';
                      $('#duallist').append(context);
                  }
                    demo1.bootstrapDualListbox('refresh');


              });
        }
        else{
              $.get("/api/method/iot_ui.ui_api.list_group_user?groupid="+selectnode, function(r){
                //$("div").html(result);
                  console.log(r.message);
                  users = r.message;
                  $("#duallist").empty();
                  for(n in users){
                      var context = '<option value="'+users[n]+'">'+users[n]+'</option>';
                      $('#duallist').append(context);
                  }

                demo1.bootstrapDualListbox('refresh');
              });
        }

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
    /*点击组织架构文字*/
    $("body").on("click", "div .branch-desc", function() {
            var dataid = $(this).attr("data-id");
            memberurl = "/api/method/iot_ui.ui_api.list_group_member?groupid="+dataid;
            table.ajax.url(memberurl).load();
            $(".dd2-content.group_name").removeClass("btn-info");
            $("#headquarters").parent().removeClass("btn-info");
            $(this).parent().addClass("btn-info");
            selectnode = dataid;

        });

    $('#companyheadquarters').click(function() {
        memberurl = "/api/method/iot_ui.ui_api.list_company_member?company="+company;
        table.ajax.url(memberurl).load();
        $(this).parent().addClass("btn-info");
        $(".dd2-content.group_name").removeClass("btn-info");
        selectnode = "root";

    });
    /*点击组织架构文字*/
    $("body").on("click", "div .branch-del", function() {
        var dataid = $(this).attr("data-id");
        $("#new-group-name").attr("data-options", dataid);
        var selectli = $(this).parent().parent();
        //var selectdivbrother = $(this).parent().prev();
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

                            $.post("/api/method/iot_ui.ui_api.del_company_group?groupid="+dataid, {}, function(r) {
                                console.log(r);
                                if(r.message == true ) {
                                    selectli.remove();
                                }
                                else{
                                      $.gritter.add({
                                            title: '删除组错误',
                                            text: r.message.reason,
                                            class_name: 'gritter-error gritter-light'
                                        });
                                }
                            }, 'json');

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
        var selectdiv = $(this).prev().prev();
        var selectdivbrother = $(this).parent().prev();
        $("#new-group-name").attr("data-options", dataid);
        $('#structure-list').addClass("hide");
        $('#member-list').addClass("hide");
        $('#add-group').removeClass("hide");
        $('#add-member').addClass("hide");

        $('#btn-confirm').addClass("hide");
        $('#btn-reset').addClass("hide");
        $('#btn-modify').removeClass("hide");

        $('#add-group-head').text("修改组名");
        $('#add-group-title').text("为" + selectdiv.text() + "定义新的组名");
    });



    $("#btn-add-members").click(function () {
        var memberlists = $('[name="duallistbox_demo1[]"]').val();
        if(selectnode=="root"){
            if(memberopflag==1){
                var url = "/api/method/iot_ui.ui_api.add_company_member";
            }
            else if(memberopflag==0){
                var url = "/api/method/iot_ui.ui_api.del_company_member";
            }

        if(memberlists){
            console.log(memberlists, memberlists.length);
            var mmm = {
                "members": memberlists,
                "company": company
	        };
            $.ajax({
                type: 'POST',
                url: url,
                contentType: "application/json", //必须有
                data: JSON.stringify(mmm),
                dataType: "json",
                success: function(data) {
                    if(data.message.result == "sucessful" ){
                        console.log("提交成功！");
                        if(data.message.remained.length){
                            $.gritter.add({
                            title: '删除成员失败',
                            text: data.message.remained,
                            class_name: 'gritter-error gritter-light'
					        });
                        }
                        $('#add-group').addClass("hide");
                        $('#structure-list').removeClass("hide");
                        $('#member-list').removeClass("hide");
                        $('#add-member').addClass("hide");
                        table.ajax.url(memberurl).load();
                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

        }


        }
        else{
            if(memberopflag==1){
                var url = "/api/method/iot_ui.ui_api.add_group_members";
            }
            else if(memberopflag==0){
                var url = "/api/method/iot_ui.ui_api.delete_group_members";
            }

            if(memberlists){
                console.log(memberlists, memberlists.length);
                var mmm = {
                    "members": memberlists,
                    "group": selectnode
                };
                $.ajax({
                    type: 'POST',
                    url: url,
                    contentType: "application/json", //必须有
                    data: JSON.stringify(mmm),
                    dataType: "json",
                    success: function(data) {
                        if(data.message.result == "sucessful" ){
                            console.log("提交成功！");
                            $('#add-group').addClass("hide");
                            $('#structure-list').removeClass("hide");
                            $('#member-list').removeClass("hide");
                            $('#add-member').addClass("hide");
                            table.ajax.url(memberurl).load();
                         }
                      },
                     error: function() {
                          console.log("异常!");
                      }
                });

            }



        }

    });

    $("#btn-cancel").click(function () {
        $('#add-group').addClass("hide");
        $('#structure-list').removeClass("hide");
        $('#member-list').removeClass("hide");
        $('#add-member').addClass("hide");
   });

    $('#table-refresh').click(function() {
        table.ajax.url(memberurl).load();
    });

    $('#example tbody').on( 'click', 'div#member-del', function () {
        var data = table.row($(this).parents('tr')).data();
        //var data = table.row( this ).data();
        //var data = $('#example').DataTable().row($(this).parents('tr')).data();
        if(selectnode=="root"){
            var url = "/api/method/iot_ui.ui_api.del_company_single_member";
            var mmm = {
                "member": data.member_id,
                "company": company
	        };
            $.ajax({
                type: 'POST',
                url: url,
                contentType: "application/json", //必须有
                data: JSON.stringify(mmm),
                dataType: "json",
                success: function(r) {
                    if(r.message.result == "sucessful" ){
                        table.ajax.url(memberurl).load();
                     }
                     else{
                        $.gritter.add({
						    title: '删除成员失败',
						    text: r.message.reason,
						    class_name: 'gritter-error gritter-light'
					});
                    }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

            }
        else{
            var url = "/api/method/iot_ui.ui_api.delete_group_members";
            var mmm = {
                "members": [data.member_id],
                "group": selectnode
            };
            $.ajax({
                type: 'POST',
                url: url,
                contentType: "application/json", //必须有
                data: JSON.stringify(mmm),
                dataType: "json",
                success: function(r) {
                    if(r.message.result == "sucessful" ){
                        table.ajax.url(memberurl).load();
                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

        }
    } );
});