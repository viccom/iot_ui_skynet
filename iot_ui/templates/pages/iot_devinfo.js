var refflag = 0;
var symlinksn = '{{ doc.sn }}';
var devices = {{ vsn }};
var id = '';
var lastid = '';
var isvsn = false;
var current_vsn = '';
var rtvalueurl = '';

    $(document.body).css({"overflow-y":"scroll" });
	    //解析URL的函数
        function parseURL(url) {
             var a =  document.createElement('a');
             a.href = url;
             return {
             source: url,
             protocol: a.protocol.replace(':',''),
             host: a.hostname,
             port: a.port,
             query: a.search,
             params: (function(){
                 var ret = {},
                     seg = a.search.replace(/^\?/,'').split('&'),
                     len = seg.length, i = 0, s;
                 for (;i<len;i++) {
                     if (!seg[i]) { continue; }
                     s = seg[i].split('=');
                     ret[s[0]] = s[1];
                 }
                 return ret;
             })(),
             file: (a.pathname.match(/\/([^\/?#]+)$/i) || [,''])[1],
             hash: a.hash.replace('#',''),
             path: a.pathname.replace(/^([^\/])/,'/$1'),
             relative: (a.href.match(/tps?:\/\/[^\/]+(.+)/) || [,''])[1],
             segments: a.pathname.replace(/^\//,'').split('/')
             };
            }


$(document).ready(function() {
    //判断当前URL设置页面中的哪一个菜单被激活
    var myURL = parseURL(document.referrer);
    //var y = $("ul.breadcrumb").children().last().text();
    mypath = myURL.path.split("/");
    //console.log(mypath);
    if(mypath[1]=='Devices_List'){
        $("ul.breadcrumb").children().last().remove();
        $("ul.breadcrumb").append('<li><a href="/'+mypath[1]+'">{{_('Devices_List')}}</a></li>');
        $("ul.breadcrumb").append('<li class="active">{{ doc.dev_name }}</li>');
    }
    if(mypath[1]=="Devices_List"){
        console.log($("ul.nav-list li:eq(0) a").attr("href"));
        $("ul.nav-list li:eq(0)").addClass('active');
    }

    //判断当前URL设置页面中的哪一个菜单被激活

    var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn;
    var table = jQuery('#RTValue-Table').DataTable({
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
            {"data": "NAME"},
            {"data": "DESC"},
            {"data": "TM"},
            {"data": "PV"},
            {"data": "Q"},


        ]
    });

      refflag = setInterval( function () {table.ajax.reload( null, false ); }, 3000 );


      $("#auto_refresh").click(function(){
          console.log($(this).html());
          if($(this).html()=="已自动刷新"){
            refflag = window.clearInterval(refflag);
            $(this).html("已停止刷新")
          }
          else{
              refflag = setInterval( function () {table.ajax.reload( null, false ); }, 3000 );
              $(this).html("已自动刷新")
          }
      });

        $("#cloud-data").click(function(){
              $('#manual_query').addClass('hide');
              $('#auto_refresh').removeClass('hide');
      });

        $("#locale-data").click(function(){
              $('#manual_query').removeClass('hide');
              $('#auto_refresh').addClass('hide');
      });
        $("#symlink-log").click(function(){
              $('#manual_query').removeClass('hide');
              $('#auto_refresh').addClass('hide');
      });
        $("#dev-message").click(function(){
              $('#manual_query').removeClass('hide');
              $('#auto_refresh').addClass('hide');
      });
    //点击按钮
          $("div .btn-app").each(function(){
              $(this).click(function(){
                  var name = $(this).attr("devname");
                  id = $(this).attr("devid");
                  console.log(name, id);
                  if(id==symlinksn){
                      var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn;
                      isvsn = false;
                      current_vsn = '';
                      if(lastid!=symlinksn){
                      $('#cloud-data').addClass('active');
                      $('#cloud-data-tab').addClass('active');

                      $('#locale-data').removeClass('active');

                      $('#symlink-log').removeClass('active hide');
                      $('#log-tab').removeClass('active hide');


                      $('#dev-message').addClass('hide');
                      $('#message-tab').addClass('hide');
                      }
                      lastid = id;
                      $('#manual_query').addClass('hide');
                      $('#auto_refresh').removeClass('hide');

                  }
                  else if(lastid==symlinksn){
                      var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn + "&vsn=" + id;
                      isvsn = true;
                      current_vsn = id;
                      lastid = id;

                      $('#cloud-data').addClass('active');
                      $('#cloud-data-tab').addClass('active');

                      $('#locale-data').removeClass('active');
                      $('#locale-data-tab').removeClass('active');

                      $('#dev-message').removeClass('hide');
                      $('#message-tab').removeClass('hide');

                      $('#symlink-log').removeClass('active');
                      $('#symlink-log').addClass('hide');
                      $('#log-tab').removeClass('active');
                      $('#log-tab').addClass('hide');

                      $('#manual_query').addClass('hide');
                      $('#auto_refresh').removeClass('hide');


                  }
                  else{
                      var rtvalueurl = "/api/method/iot.hdb.iot_device_data_array?sn=" + symlinksn + "&vsn=" + id;
                      isvsn = true;
                      current_vsn = id;
                      lastid = id;
                      $('#dev-message').removeClass('hide');
                      $('#message-tab').removeClass('hide');

                      $('#symlink-log').removeClass('active');
                      $('#symlink-log').addClass('hide');
                      $('#log-tab').removeClass('active');
                      $('#log-tab').addClass('hide');

                  }

                  console.log(rtvalueurl);
                  table.ajax.url(rtvalueurl).load();
                    $($(this).siblings()).removeClass('btn-yellow');
                    $(this).addClass('btn-yellow');
                    $('#devname').html("{{_('Name')}}"+":"+name);
                    $('#devsn').html("{{_('SN')}}"+":"+id);
                    $('#cur_devname').html("设备名称:"+name); //赋值
              });
          });
    //点击按钮

    //双击表格行
      $('#RTValue-Table tbody').on('dblclick', 'tr', function () {
        var data = table.row( this ).data();
        tnm = data['NAME'].toLowerCase();
        console.log(isvsn);
        console.log(current_vsn);
        console.log(tnm);
        //window.location.href="/S_Station_infox/"+data['name'];

          if(isvsn){

            hisdataurl = "/iot_tag_his?sn="+symlinksn+"&vsn="+ current_vsn +"&tag="+tnm;
          }
          else{
            hisdataurl = "/iot_tag_his?sn="+symlinksn+"&tag="+tnm;
                  }
              console.log(hisdataurl);
              window.open(hisdataurl);

    } );
    //双击表格行tooltip({html : true }
    //$(function () { $('table .tooltip-show').tooltip('show');});
    $(function () { $("table.tooltip-options").tooltip({html : true });});

});