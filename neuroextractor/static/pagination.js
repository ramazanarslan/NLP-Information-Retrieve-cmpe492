$(function() {
  $("#pagination_submit").click(
    function(e){
        pagination_submit();
    }
  );
  $("#pagination").on("keypress",function(e){
    if(e.which == 13){
      $("#pagination_submit").trigger("click");
    }
  });
});


function pagination_submit(){
    var pagination_number = $("#pagination").val();

    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    var pageVariableExists=false;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === "page") {

            sURLVariables[i]= "page="+pagination_number
            pageVariableExists=true;
            break;
        }
    }

    var new_url = sURLVariables.join("&");
    if(!pageVariableExists){
        new_url += "&page="+pagination_number;
    }

    console.log("new_url=" + new_url);
    window.location.href = "results?"+new_url;
}
