$(function() {
  $("#search_submit").click(
    function(e){
        search_submit();
    }
  );
  $(".remove_filter").click(function(){
    remove_filter(this);
  });

  $("#search").on("keypress",function(e){
    if(e.which == 13){
      $("#search_submit").trigger("click");
    }
  });

  $(".filter-update").on("keypress",function(e){
    if(e.which == 13){
      update_filter();
    }
  });
  $('.years-input').on('keypress', function(e){
      return e.metaKey || // cmd/ctrl
        e.which <= 0 || // arrow keys
        e.which == 8 || // delete key
        /[0-9]/.test(String.fromCharCode(e.which)); // numbers

    });


  $(".or-row:last").remove();

  $('.mouseover_class').on({
    mouseenter: function() {
        $(this).children('td').children('button').css("opacity", "1.0");
    },
    mouseleave: function() {
        $(this).children('td').children('button').css("opacity","0.0");
    }
  });
  $("#newquery_button").on("click",function(){
    var new_filter_input='<tr class="mouseover_class"><td><input type="text" class="form-control filter-update filter-input" autocomplete=off style="width:auto; resize:vertical; padding-right:1%; " /></td><td><button type="button" class="remove_filter btn btn-warning btn-circle" style="opacity:0.0; margin-left:-400%; margin-top:7px;"><i class="glyphicon glyphicon-remove"></i></button></td><td></td><td></td></tr>';
    $(new_filter_input).insertBefore( $(this).parent().parent());

  });
  filter_list = JSON.parse(filter_list.replace(/\'/ig,'\"'));

    init_header();

});

function init_header(){
  var search_terms = filter_list.join(", ");

  $("#search_header").text(search_terms);
}


function search_submit(){
    var search_input = $("#search").val();
    if(search_input ==""){
      return;
    }
    var current_query = getUrlParameter("query");
    var current_field = getUrlParameter("fields");
    var current_sYear = getUrlParameter("sYear");
    var current_eYear = getUrlParameter("eYear");
    var new_query = "";
    if (current_query){
        new_query = current_query + "!!"+search_input;
    }
    else{
      new_query = search_input;
    }

    console.log("new_query=" + new_query);
    redirect_with_params(current_field,current_sYear,current_eYear,new_query);
}

function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
}

function remove_filter(button){
  var type = $(button).parent().parent().prop("nodeName");
  var remove_index = $(button).parent().parent().index();
  remove_index = (remove_index-1)/2;


  filter_list.splice(remove_index,1);
  var query = filter_list.join("!!");

  redirect_with_params(getUrlParameter("fields"),getUrlParameter("sYear"),getUrlParameter("eYear"),query);
}

function update_filter(){
  var filters = [];
  var s_year =""; var e_year ="";
  $(".filter-input").each(function(){
    var temp = $(this).val().trim();
    if(temp != ""){
        filters.push(temp);
    }

  });
  s_year = $("#start_year").val().trim();
  e_year = $("#end_year").val().trim();

  var query = filters.join("!!");
  redirect_with_params($("#fields").val(),s_year,e_year,query);
}

function redirect_with_params(field,sYear, eYear, query, page){
  console.log(query);
  if(typeof(query)==='undefined' || query==""){
    window.location.href = "/";
    return;
  }

  if(typeof(page)==='undefined'){
    page = "";
  }
  else{
    page = "&page=" + page;
  }

  if(typeof(field)==='undefined'){
    field = "allfields";
  }


  if(typeof(sYear) === 'undefined'){
    sYear = "";
  }
  else{
      sYear = "&sYear=" + sYear;
  }
  if(typeof(eYear) === 'undefined'){
    eYear = "";
  }
  else {
    eYear = "&eYear=" + eYear;
  }

  window.location.href= "/results?fields="+field +sYear+eYear +"&query=" + query +page;
}

function exportBasic() {
    var temp1 = [];
    var s_year =""; var e_year ="";
    $(".filter-input").each(function(){
      var temp = $(this).val().trim();
      if(temp != ""){
          temp1.push(temp);
      }
    });
    var query = temp1.join("!!");
    var fields = $("#fields").val();
    var s_year = $("#start_year").val().trim();
    var e_year = $("#end_year").val().trim();

    var export_url = '/exportBasic?'+'fields='+fields+'&sYear='+s_year+'&eYear='+e_year+'&query='+query;
    window.location.href = export_url;
}

function exploreAbstract(clickedTD) {
   var theTable = $(clickedTD).find('table')[0];
   $(theTable).toggleClass('hide-abstract-sentences');
}
