  $("div .infobox-data").each(function() {
      $(this).click(function () {
          var dataid = $(this).attr("data-id");
          console.log(dataid);
          window.location.href="/gateways_list?filter="+dataid;
      });
  });


    $('#devices_reload').click(function() {

        $.get("/api/method/iot_ui.ui_api.devices_list_array?filter=devices_amount", function (r) {
        if(r.message) {
            console.log(r.message);
            $('#devices_total').text(r.message.all);
            $('#devices_online').text(r.message.online);
            $('#devices_offline').text(r.message.offline);
            $('#devices_offline_7d').text(r.message.offline_7d);

        }
        });

    });