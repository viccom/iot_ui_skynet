var symlinksn = '{{ doc.sn }}';

$(document.body).css({"overflow-y":"scroll" });
$(document).ready(function() {

    $.ajax({
        type: 'POST',
        url: "/api/method/iot.device_api.app_list",
        Accept: "application/json",
        contentType: "application/json",
        data: JSON.stringify({ "device": symlinksn}),
        dataType: "json",
        success: function(r) {
            console.log(r);
          },
         error: function() {
              console.log("异常!");
          }
    });

    $('#iot-update').click(function(){
        console.log("iot-update");
        $.ajax({
            type: 'POST',
            url: "/api/method/iot.device_api.sys_upgrade",
            Accept: "application/json",
            contentType: "application/json",
            data: JSON.stringify({ "device": symlinksn, "data": {"no_ack": 1, "version": "latest"}}),
            dataType: "json",
            success: function(r) {
                console.log(r);
              },
             error: function(r) {
                  console.log(r);
          }
    });

    } );

    $('#switch-mode').click(function(){
            var url = "/iot_devinfo/" + symlinksn;
            window.location.href=url;
    } );
});