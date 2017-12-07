var symlinksn = '{{ doc.sn }}';

$(document.body).css({"overflow-y":"scroll" });
$(document).ready(function() {


    $('#switch-mode').click(function(){
            var url = "/iot_devinfo/" + symlinksn;
            window.location.href=url;
    } );
});