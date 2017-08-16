    var filter="unread";
    var rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter=" + filter;
    var table = $('#example').DataTable({
        "ajax": {
            "url": rtvalueurl,
            //"url": "/api/method/tieta.tieta.doctype.cell_station.cell_station.list_station_map",
            "dataSrc": "message",
        },
        "dom": 'Blfrtip',
        // dom: 'Blfrtip',
        "buttons": [ 'copy'],
        //"bInfo" : false,
        //"pagingType": "full_numbers" ,
        "bStateSave": true,
        "sPaginationType": "full_numbers",
        "iDisplayLength" : 25,
      'columnDefs': [
          {
         'targets': 0,
         'searchable': false,
         'orderable': false,
         'width': '1%',
         'className': 'dt-body-center',
         'render': function (data, type, full, meta){
             return '<input type="checkbox">';
         },
          "createdCell": function (td, cellData, rowData, row, col) {
          if (!rowData.hasRead) {
            $(td).parent().addClass("text-primary");

          }
         }
          },
          {
             'targets': [1,2,3,4,5],
              'width': '10%'
          },
          {
             'targets': [6],
              'width': '50%'
          },
      ],
      'order': [[1, 'asc']],
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
            {"data": "device"},
            {"data": "error_type"},
            {"data": "error_key"},
            {"data": "error_level"},
            {"data": "time"},
            {"data": "brief"}
        ],
      'rowCallback': function(row, data, dataIndex){
         // Get row ID
         var rowId = data.name;

         // If row ID is in the list of selected row IDs
         if($.inArray(rowId, rows_selected) !== -1){
            $(row).find('input[type="checkbox"]').prop('checked', true);
            $(row).addClass('selected');
         }
      }
   });


//
// Updates "Select all" control in a data table
//
var rows_selected = [];
var rows_selected_data = [];


function updateDataTableSelectAllCtrl(table){
   var $table             = table.table().node();
   var $chkbox_all        = $('tbody input[type="checkbox"]', $table);
   var $chkbox_checked    = $('tbody input[type="checkbox"]:checked', $table);
   var chkbox_select_all  = $('thead input[name="select_all"]', $table).get(0);

   // If none of the checkboxes are checked
   if($chkbox_checked.length === 0){
      chkbox_select_all.checked = false;
      $(table.button()[0].node).addClass("disabled");
      if('indeterminate' in chkbox_select_all){
         chkbox_select_all.indeterminate = false;
      }

   // If all of the checkboxes are checked
   } else if ($chkbox_checked.length === $chkbox_all.length){
      chkbox_select_all.checked = true;
      $(table.button()[0].node).removeClass("disabled");
      if('indeterminate' in chkbox_select_all){
         chkbox_select_all.indeterminate = false;
      }

   // If some of the checkboxes are checked
   } else {
      chkbox_select_all.checked = true;
      $(table.button()[0].node).removeClass("disabled");
      //console.log(table.button()[0].node);
      if('indeterminate' in chkbox_select_all){
         chkbox_select_all.indeterminate = true;
      }
   }
}

$(document).ready(function() {
    $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=len_"+filter, function (r) {
        //console.log(r.message);
        if(r.message){
            console.log(filter);
             $('#no_data').addClass("hide");
             $('#table_area').removeClass("hide");
            var rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter="+filter;
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }

    });


/*    var table = jQuery('#example').DataTable({
        'columnDefs': [
              {
                 'targets': 0,
                 'checkboxes': {
                    'selectRow': true
                 }
              }
           ],
           'select': {
              'style': 'multi'
           },
           'order': [[1, 'asc']],
         "dom": 'Blfrtip',
        // dom: 'Blfrtip',
        "buttons": [ 'copy'],
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
            {"data": "name"},
            {"data": "device"},
            {"data": "error_type"},
            {"data": "error_key"},
            {"data": "error_level"},
            {"data": "brief"}
        ],
    });*/



       // Handle click on checkbox
   $('#example tbody').on('click', 'input[type="checkbox"]', function(e){
      var $row = $(this).closest('tr');

      // Get row data
      var data = table.row($row).data();
      //console.log(data.name);

      // Get row ID
      var rowId = data.name;
      //console.log("rowId:",rowId);

      // Determine whether row ID is in the list of selected row IDs
      var index = $.inArray(rowId, rows_selected);
      var index_1 = $.inArray(data, rows_selected_data);
      //console.log("index:",index);

      // If checkbox is checked and row ID is not in list of selected row IDs
      if(this.checked && index === -1){
        rows_selected.push(rowId);
        rows_selected_data.push(data);

      // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
      } else if (!this.checked && index !== -1){
         rows_selected.splice(index, 1);
         rows_selected_data.splice(index_1, 1);
      }

      if(this.checked){
         $row.addClass('selected');
      } else {
         $row.removeClass('selected');
      }

      // Update state of "Select all" control
      updateDataTableSelectAllCtrl(table);

      // Prevent click event from propagating to parent
      e.stopPropagation();
   });

   // Handle click on table cells with checkboxes
   $('#example').on('click', 'tr td:nth-child(n+3)', function(e){
      //$(this).parent().find('input[type="checkbox"]').trigger('click');
        var data = table.row( this ).data();
        var errid = data['name'];
        var hasRead = data['hasRead'];
        //console.log(errid);
        if(errid){
           var url = "/iot_event_info?eventid=" + errid;
            window.location.href=url;
        }

   });

   // Handle click on "Select all" control
   $('thead input[name="select_all"]', table.table().container()).on('click', function(e){
      if(this.checked){
         $('#example tbody input[type="checkbox"]:not(:checked)').trigger('click');
      } else {
         $('#example tbody input[type="checkbox"]:checked').trigger('click');
      }

      // Prevent click event from propagating to parent
      e.stopPropagation();
   });

   // Handle table draw event
   table.on('draw', function(){
      // Update state of "Select all" control
      //updateDataTableSelectAllCtrl(table);
   });

    new $.fn.dataTable.Buttons( table, {
    buttons: [
        {
            text: '标记已读',
            enabled: false,
            action: function ( e, dt, node, conf ) {
                //var s_selected = table.column(0).checkboxes.selected();
                //console.log(rows_selected);
                var post_data = [];
                    for(var i = 0;i < rows_selected_data.length; i++) {
                        if(!rows_selected_data[i].hasRead){
                            post_data.push(rows_selected_data[i].name);
                        }
                    }
                //console.log(post_data);
                    if(post_data){
//----------------------------------------------------------------------------
            var url = "/api/method/iot_ui.ui_api.mark_iot_event_read";
            var mmm = {
                "errid": post_data
            };
            $.ajax({
                type: 'POST',
                url: url,
                contentType: "application/json", //必须有
                data: JSON.stringify(mmm),
                dataType: "json",
                success: function(r) {
                    //console.log(r);
                    if(r.message.result == "sucessful" ){
                                $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=len_"+filter, function (r) {
                                    if(r.message) {
                                        $('#no_data').addClass("hide");
                                        $('#table_area').removeClass("hide");
                                        rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter="+filter;
                                        table.ajax.url(rtvalueurl).load();
                                    }
                                    else{
                                        $('#no_data').removeClass("hide");
                                        $('#table_area').addClass("hide");
                                    }
                                });
                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

//----------------------------------------------------------------------------


                    }
            }
        },
                    {
            text: '全部已读',
            action: function ( e, dt, node, conf ) {
                //var _selected = table.column(0).data();
                var _selected = table.data();
                //console.log(_selected);
                var post_data = [];
                    for(var i = 0;i < _selected.length; i++) {
                        if(!_selected[i].hasRead){
                            post_data.push(_selected[i].name);
                        }
                    }
                //console.log(post_data);
                    if(post_data){
 //----------------------------------------------------------------------------
            var url = "/api/method/iot_ui.ui_api.mark_iot_event_read";
            var mmm = {
                "errid": post_data
            };
            $.ajax({
                type: 'POST',
                url: url,
                contentType: "application/json", //必须有
                data: JSON.stringify(mmm),
                dataType: "json",
                success: function(r) {
                    if(r.message.result == "sucessful" ){
                                $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=len_"+filter, function (r) {
                                    if(r.message) {
                                        $('#no_data').addClass("hide");
                                        $('#table_area').removeClass("hide");
                                        rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter="+filter;
                                        table.ajax.url(rtvalueurl).load();
                                    }
                                    else{
                                        $('#no_data').removeClass("hide");
                                        $('#table_area').addClass("hide");
                                    }
                                });
                     }
                  },
                 error: function() {
                      console.log("异常!");
                  }
            });

//----------------------------------------------------------------------------


                    }
            }
        },
    ]
} );

    table.buttons( 1, null ).container().appendTo(
        table.table().container()
    );


    $('#table-refresh').click(function() {
        table.ajax.url(rtvalueurl).load();
    });
    $('#event-all').click(function() {
        $('#event-all').addClass("btn-success");
        $('#event-unread').removeClass("btn-success");
        $('#event-hasread').removeClass("btn-success");
        $(table.button()[0].node).removeClass("hide");
        $(table.button()[0].node).next().removeClass("hide");
        filter = "all";
        $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=len_"+filter, function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter="+filter;
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });
    $('#event-unread').click(function() {
        $('#event-all').removeClass("btn-success");
        $('#event-unread').addClass("btn-success");
        $('#event-hasread').removeClass("btn-success");
        $(table.button()[0].node).removeClass("hide");
        $(table.button()[0].node).next().removeClass("hide");
        filter = "unread";
        $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=len_"+filter, function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter="+filter;
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });
    $('#event-hasread').click(function() {
        $('#event-all').removeClass("btn-success");
        $('#event-unread').removeClass("btn-success");
        $('#event-hasread').addClass("btn-success");
        $(table.button()[0].node).addClass("hide");
        $(table.button()[0].node).next().addClass("hide");

        filter = "hasread";
        $.get("/api/method/iot_ui.ui_api.query_iot_event?filter=len_" + filter, function (r) {
        if(r.message) {
            $('#no_data').addClass("hide");
            $('#table_area').removeClass("hide");
            rtvalueurl = "/api/method/iot_ui.ui_api.query_iot_event?filter="+filter;
            table.ajax.url(rtvalueurl).load();
        }
        else{
            $('#no_data').removeClass("hide");
            $('#table_area').addClass("hide");
        }
        });
    });





});