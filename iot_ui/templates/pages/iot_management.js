var symlinksn = '{{ doc.sn }}';

$(document.body).css({"overflow-y":"scroll" });
$(document).ready(function() {

    $.ajax({
        type: 'POST',
        url: "/api/method/iot.device_api.app_list",
        Accept: "application/json",
        contentType: "application/json",
        data: JSON.stringify({ "device": iotsn}),
        dataType: "json",
        success: function(r) {
          },
         error: function() {
              console.log("异常!");
          }
    });



    $('#switch-mode').click(function(){
            var url = "/iot_devinfo/" + symlinksn;
            window.location.href=url;
    } );
});