$(function() {

  $("#toggle_yearFilter").change(function () {
    $('#startYear').prop('disabled', !$(this).prop('checked') );
    $('#endYear').prop('disabled', !$(this).prop('checked') );
  });


  $("#toggleYearFilter").change(function () {
    $('#yearStart').prop('disabled', !$(this).prop('checked') );
    $('#yearEnd').prop('disabled', !$(this).prop('checked') );
  });


  $("#perspective-option").change(function () {


      if($("#perspective-option").val() == 1){
        window.location.href = "/?perspective=basic";
      }else if($("#perspective-option").val() == 2){
        window.location.href = "/?perspective=tables";
      }
  });

  $("#addConstraint").click(function () {
      var input_box = '<div style="margin-top:5px;" ><input type="text" name="constraint" class="form-control" placeholder="Write constraint list"></div>';
      $(input_box).insertBefore("#addConstraint");
  });

  //initialize page as tables perspective or leave as basic perspective
  if(getUrlParameter("perspective") == "tables"){
    $(".perspective-class").css("display","none");
    $("#perpective-2").css("display","inline");
    $("#perspective-option").val(2);
  }
  $("#gender_box").change(function(){
    add_human_gender_terms(this,gender_terms);
  });
  $("#human_box").change(function(){
    add_human_gender_terms(this,human_terms);
  });
  $("#asym_box").change(function(){
    add_asymmetry_terms(this,asymmetry_terms);
  });
});

var gender_terms=["female","male","woman","man"];
var asymmetry_terms=["left","right"];
var human_terms = ["human","nonhuman"];

function add_asymmetry_terms(element, related_terms){
  var last_value = $("input[name='preceding']").val();
  var preceding_list = last_value.split(",");
  if(preceding_list[preceding_list.length-1] ==""){
    preceding_list.pop();
  }
  if($(element).prop("checked")){
    preceding_list = preceding_list.concat(related_terms);

    preceding_list = preceding_list.filter(function(itm, i, a) {
      return i == a.indexOf(itm);
    });
  }
  else{
    preceding_list = preceding_list.filter(x => related_terms.indexOf(x) < 0 );
  }

  $("input[name='preceding']").focus().val(preceding_list.join(","));

}

function add_human_gender_terms(element, related_terms){
  var element_existing = "null"; // this value is set to the constraint input element, if it consists the related terms in it
  var terms_as_string = related_terms.join(",");
  $("input[name='constraint']").each(function(){
    var temp_terms = $(this).val();
    if (temp_terms == related_terms.join(",")){
      element_existing = this;
    }
  });

  if($(element).prop("checked")){
    if(element_existing == "null"){
      var input_box = '<div style="margin-top:5px;" ><input type="text" name="constraint" value="'+ terms_as_string+'" class="form-control" placeholder="Write constraint list"></div>';
      $(input_box).insertBefore("#addConstraint");
    }
  }
  else{
    if(element_existing != "null"){
      $(element_existing).remove();
    }
  }
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
