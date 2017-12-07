var refflag = 0;
var symlinksn = '{{ doc.sn }}';
var devices = '{{ vsn }}';
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

    var rtvalueurl = "/api/method/iot_ui.ui_api.iot_device_data_array?sn=" + symlinksn;
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
            {"data": "NAME"},
            {"data": "DESC"},
            {"data": "PV"},
            {"data": "Q"},
            {"data": "TM"},

        ],
        'rowCallback': function(row, data, dataIndex){
         // Get row ID
         if(data.Q=="0"){
             $(row).addClass('green');
         }
         else if(data.Q=="255"){
             $(row).addClass('grey');
         }
         else if(data.Q=="1"){
             $(row).addClass('red');
         }
      }
    });

      if($('#gritter-light').get(0).checked){
          refflag = setInterval( function () {table.ajax.reload( null, false ); }, 3000 );
          console.log("开始自动刷新");

      }

      $("#auto_refresh").change(function(){
          if($('#gritter-light').get(0).checked){
              refflag = setInterval( function () {table.ajax.reload( null, false ); }, 3000 );
              console.log("开始自动刷新");

          }
          else{
            refflag = window.clearInterval(refflag);
            console.log("停止刷新");

          }

      });

        $("#cloud-data").click(function(){
              $('#manual_query').addClass('hide');
              $('#stop_query').addClass('hide');
      });
/*
        $("#locale-data").click(function(){
              $('#manual_query').removeClass('hide');
              $('#stop_query').removeClass('hide');
      });
        */
        $("#symlink-log").click(function(){
              $('#manual_query').removeClass('hide');
              $('#stop_query').removeClass('hide');
      });
        $("#dev-message").click(function(){
              $('#manual_query').removeClass('hide');
              $('#stop_query').removeClass('hide');
      });
    //点击按钮
          $("div .btn-app").each(function(){
              $(this).click(function(){
                  var name = $(this).attr("devname");
                  id = $(this).attr("devid");
                  console.log(name, id, lastid, symlinksn);
                  if(id==symlinksn){
                      var rtvalueurl = "/api/method/iot_ui.ui_api.iot_device_data_array?sn=" + symlinksn;
                      isvsn = false;
                      current_vsn = '';
                      if(lastid!=symlinksn){
                      $('#cloud-data').addClass('active');
                      $('#cloud-data-tab').addClass('active');

                      // $('#locale-data').removeClass('active');

                      $('#symlink-log').removeClass('active hide');
                      $('#log-tab').removeClass('active hide');


                      $('#dev-message').addClass('hide');
                      $('#message-tab').addClass('hide');
                      }
                      lastid = id;
                      $('#manual_query').addClass('hide');
                        $('#stop_query').addClass('hide');

                  }
                  else if(lastid==symlinksn){
                      var rtvalueurl = "/api/method/iot_ui.ui_api.iot_device_data_array?sn=" + symlinksn + "&vsn=" + id;
                      isvsn = true;
                      current_vsn = id;
                      lastid = id;
                        console.log("hide message");
                      $('#cloud-data').addClass('active');
                      $('#cloud-data-tab').addClass('active');

                      // $('#locale-data').removeClass('active');
                      // $('#locale-data-tab').removeClass('active');

                      $('#dev-message').removeClass('hide');
                      $('#dev-message').removeClass('active');
                      $('#message-tab').removeClass('hide');

                      $('#symlink-log').removeClass('active');
                      $('#symlink-log').addClass('hide');
                      $('#log-tab').removeClass('active');
                      $('#log-tab').addClass('hide');

                      $('#manual_query').addClass('hide');
                       $('#stop_query').addClass('hide');

                  }
                  else{
                      var rtvalueurl = "/api/method/iot_ui.ui_api.iot_device_data_array?sn=" + symlinksn + "&vsn=" + id;
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

    $('#manual_query').click(function(){

        if(client){
            client.unsubscribe(symlinksn+'/comm', {
                 onSuccess: unsubscribeSuccess,
                 onFailure: unsubscribeFailure
             });
            client.unsubscribe(symlinksn+'/log', {
                 onSuccess: unsubscribeSuccess,
                 onFailure: unsubscribeFailure
             });
        disconnect();
        client=null;
        }
        var cuser_id = $.cookie('user_id');
        var csid = $.cookie('sid');
        console.log(current_vsn, cuser_id, csid);
        if(current_vsn){
            console.log("查询报文");
            clearHistory();
            //----------------------------------------------------------------------------
                var url = "/api/method/iot.device_api.sys_enable_comm";
                var mmm = {
                            "device": symlinksn,
                            "data": "120",
                            "id": current_vsn,
                        };
                $.ajax({
                    type: 'POST',
                    url: url,
                    contentType: "application/json", //必须有
                    data: JSON.stringify(mmm),
                    dataType: "json",
                    headers: {
                                "HDB-AuthorizationCode" : "12312313aaa"
                            },
                    success: function(r) {
                        console.log(r);
                    //---------------------------------------------------------------------------------

                    var hostname = "192.168.174.133";
                    var port = "8083";
                    var clientId = 'js-mqtt-' + makeid();

                    var path = "/mqtt";
                    var user = cuser_id;
                    var pass = csid;
                    var keepAlive = 60;
                    var timeout = 6;
                    var tls = false;
                    var cleanSession = true;
                    var lastWillTopic = null;
                    var lastWillQos = 0;
                    var lastWillRetain = false;
                    var lastWillMessage = null;


                    if(path){
                      client = new Paho.MQTT.Client(hostname, Number(port), path, clientId);
                    } else {
                      client = new Paho.MQTT.Client(hostname, Number(port), clientId);
                    }
                    console.info('Connecting to Server: Hostname: ', hostname, '. Port: ', port, '. Path: ', client.path, '. Client ID: ', clientId);

                    // set callback handlers
                    client.onConnectionLost = onConnectionLost;
                    client.onMessageArrived = onMessageArrived;


                    var options = {
                      invocationContext: {host : hostname, port: port, path: client.path, clientId: clientId},
                      timeout: timeout,
                      keepAliveInterval:keepAlive,
                      cleanSession: cleanSession,
                      useSSL: tls,
                      onSuccess: onConnect,
                      onFailure: onFail
                    };



                    if(user){
                      options.userName = user;
                    }

                    if(pass){
                      options.password = pass;
                    }

                    if(lastWillTopic){
                      var lastWillMessage = new Paho.MQTT.Message(lastWillMessage);
                      lastWillMessage.destinationName = lastWillTopic;
                      lastWillMessage.qos = lastWillQos;
                      lastWillMessage.retained = lastWillRetain;
                      options.willMessage = lastWillMessage;
                    }

                    // connect the client
                    client.connect(options);
                    console.log(user,pass);

                    var  t=setTimeout("client.subscribe(symlinksn+'/comm', {qos: 0})",100);

                    //---------------------------------------------------------------------------------
                      },
                     error: function() {
                          console.log("异常!");
                      }
                });

    //----------------------------------------------------------------------------
        }
        else{
            console.log("查询日志");
            clearDevLog();
            //----------------------------------------------------------------------------
                var url = "/api/method/iot.device_api.sys_enable_log";
                var mmm = {
                            "device": symlinksn,
                            "data": "120",
                            "id": symlinksn,
                        };
                $.ajax({
                    type: 'POST',
                    url: url,
                    contentType: "application/json", //必须有
                    data: JSON.stringify(mmm),
                    dataType: "json",
                    headers: {
                                "HDB-AuthorizationCode" : "12312313aaa"
                            },
                    success: function(r) {
                        console.log(r);
                                            //---------------------------------------------------------------------------------

                    var hostname = "192.168.174.133";
                    var port = "8083";
                    var clientId = 'js-mqtt-' + makeid();

                    var path = "/mqtt";
                    var user = cuser_id;
                    var pass = csid;
                    var keepAlive = 60;
                    var timeout = 6;
                    var tls = false;
                    var cleanSession = true;
                    var lastWillTopic = null;
                    var lastWillQos = 0;
                    var lastWillRetain = false;
                    var lastWillMessage = null;


                    if(path){
                      client = new Paho.MQTT.Client(hostname, Number(port), path, clientId);
                    } else {
                      client = new Paho.MQTT.Client(hostname, Number(port), clientId);
                    }
                    console.info('Connecting to Server: Hostname: ', hostname, '. Port: ', port, '. Path: ', client.path, '. Client ID: ', clientId);

                    // set callback handlers
                    client.onConnectionLost = onConnectionLost;
                    client.onMessageArrived = onLogArrived;


                    var options = {
                      invocationContext: {host : hostname, port: port, path: client.path, clientId: clientId},
                      timeout: timeout,
                      keepAliveInterval:keepAlive,
                      cleanSession: cleanSession,
                      useSSL: tls,
                      onSuccess: onConnect,
                      onFailure: onFail
                    };



                    if(user){
                      options.userName = user;
                    }

                    if(pass){
                      options.password = pass;
                    }

                    if(lastWillTopic){
                      var lastWillMessage = new Paho.MQTT.Message(lastWillMessage);
                      lastWillMessage.destinationName = lastWillTopic;
                      lastWillMessage.qos = lastWillQos;
                      lastWillMessage.retained = lastWillRetain;
                      options.willMessage = lastWillMessage;
                    }
                    console.log(user,pass);
                    // connect the client
                    client.connect(options);

                    var  t=setTimeout("client.subscribe(symlinksn+'/log', {qos: 0})",100);

                    //---------------------------------------------------------------------------------
                      },
                     error: function() {
                          console.log("异常!");
                      }
                });

    //----------------------------------------------------------------------------
        }
    });

    $('#stop_query').click(function(){
        if(client){

            if(current_vsn){
                console.log("停止查询报文");

                //----------------------------------------------------------------------------
                    var url = "/api/method/iot.device_api.sys_enable_comm";
                    var mmm = {
                                "device": symlinksn,
                                "data": "0",
                                "id": current_vsn,
                            };
                    $.ajax({
                        type: 'POST',
                        url: url,
                        contentType: "application/json", //必须有
                        data: JSON.stringify(mmm),
                        dataType: "json",
                        headers: {
                                    "HDB-AuthorizationCode" : "12312313aaa"
                                },
                        success: function(r) {
                            console.log(r);
                            client.unsubscribe(symlinksn+'/comm', {
                                 onSuccess: unsubscribeSuccess,
                                 onFailure: unsubscribeFailure
                             });
                            disconnect();
                            client=null;



                          },
                         error: function() {
                              console.log("异常!");
                          }
                    });

        //----------------------------------------------------------------------------
            }
            else{
                console.log("停止查询日志");

                //----------------------------------------------------------------------------
                    var url = "/api/method/iot.device_api.sys_enable_log";
                    var mmm = {
                                "device": symlinksn,
                                "data": "0",
                                "id": symlinksn,
                            };
                    $.ajax({
                        type: 'POST',
                        url: url,
                        contentType: "application/json", //必须有
                        data: JSON.stringify(mmm),
                        dataType: "json",
                        headers: {
                                    "HDB-AuthorizationCode" : "12312313aaa"
                                },
                        success: function(r) {
                            console.log(r);
                            client.unsubscribe(symlinksn+'/log', {
                                 onSuccess: unsubscribeSuccess,
                                 onFailure: unsubscribeFailure
                             });
                            disconnect();
                            client=null;
                          },
                         error: function() {
                              console.log("异常!");
                          }
                    });

        //----------------------------------------------------------------------------
            }

     }
    });

    //点击表格第2列
      $('#RTValue-Table tbody').on('click', 'tr td:nth-child(n+2)', function () {
        var data = table.row( this ).data();
        tnm = data['NAME'];
        console.log(isvsn);
        console.log(current_vsn);
        console.log(tnm);
        //window.location.href="/S_Station_infox/"+data['name'];

          if(isvsn){

            hisdataurl = "/new_tag_his?sn="+symlinksn+"&vsn="+ current_vsn +"&tag="+tnm;
          }
          else{
            hisdataurl = "/new_tag_his?sn="+symlinksn+"&tag="+tnm;
                  }
              console.log(hisdataurl);
              window.open(hisdataurl);

    } );
    //双击表格行tooltip({html : true }
    //$(function () { $('table .tooltip-show').tooltip('show');});
    // $(function () { $("table.tooltip-options").tooltip({html : true });});

    $('#switch-mode').click(function(){
            var url = "/iot_management/" + symlinksn;
            window.location.href=url;
    } );
});