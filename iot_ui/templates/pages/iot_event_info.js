var eventid = "{{ eventid }}";
var device = "{{ device }}";
var error_type = "{{ error_type }}";
var error_key = "{{ error_key }}";
var error_level = "{{ error_level }}";
var error_info = "{{ error_info }}";
var hasread = {{ hasread }};
console.log(eventid);
console.log(hasread);

function mark_iot_event_read(id){
//----------------------------------------------------------------------------
    var url = "/api/method/iot_ui.ui_api.mark_iot_event_read";
    var mmm = {
        "errid": [id]
    };
    $.ajax({
        type: 'POST',
        url: url,
        contentType: "application/json", //必须有
        data: JSON.stringify(mmm),
        dataType: "json",
        success: function(r) {
            console.log(r.message.result);
          },
         error: function() {
            console.log("异常!");
          }
    });

//----------------------------------------------------------------------------
}


if(!hasread){
    var t=setTimeout("mark_iot_event_read(eventid)",5000);
}



