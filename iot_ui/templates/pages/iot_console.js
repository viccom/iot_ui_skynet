  $("div .infobox-data").each(function() {
      $(this).click(function () {
          var dataid = $(this).attr("data-id");
          console.log(dataid);
          window.location.href="/gateways_list?filter="+dataid;
      });
  });