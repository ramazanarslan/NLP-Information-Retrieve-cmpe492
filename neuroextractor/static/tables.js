/**
 * Created by sahin on 4/11/17.
 */
$(function() {


    // SORTTABLE LIBRARY - MULTI TABLE FIX
    $(".th-customize1").click(function () {
        $("th").filter("[data-tableno!="+this.getAttribute("data-tableno")+"]").each(function () {
            if(this.classList.contains("sorttable_sorted")){
                this.classList.remove("sorttable_sorted");
            }else if(this.classList.contains("sorttable_sorted_reverse")){
                this.classList.remove("sorttable_sorted_reverse");
            }
        });
    });

    // RESET BUTTON FUNCTION
    $("button[data-function='reset']").click(function () {
        var $table=$(this).parent().parent().parent().parent();

        var rows = $table.find('tr').get();
        rows = rows.slice(1,rows.length);
        rows.sort(function(a, b) {
            var keyA = $(a).attr('data-index');
            var keyB = $(b).attr('data-index');
            if (keyA < keyB) return 1;
            if (keyA > keyB) return -1;
            return 0;
        });
        rows.reverse();
        $.each(rows, function(index, row) {
            $table.children('tbody').append(row);
        });


        var resetTableno= this.getAttribute("data-tableno");
        $(".columnPercentageCheckbox").filter("[data-tableno="+resetTableno+"]").each(function () {
            this.getElementsByTagName("span")[0].style.opacity = "0";
        });
        this.setAttribute("data-colList",""); // RESET THE COLLIST IN THE RESET BUTTON
        $(".rowPercentageCheckbox").filter("[data-tableno="+resetTableno+"]").each(function () {
            this.getElementsByTagName("span")[0].style.opacity = "0"
        });
        this.setAttribute("data-rowList",""); // RESET THE ROWLIST IN THE RESET BUTTON
        $("th").filter("[data-tableno="+resetTableno+"]").each(function () {
            if(this.classList.contains("sorttable_sorted")){
                this.classList.remove("sorttable_sorted");
                $("#sorttable_sortfwdind").remove();
            }else if(this.classList.contains("sorttable_sorted_reverse")){
                this.classList.remove("sorttable_sorted_reverse");
                $("#sorttable_sortrevind").remove();
            }
        });

        // TODO REMOVE PERCENTAGES
        $("span").filter("[data-celltableno="+resetTableno+"]").each(function () {
           this.innerHTML = "";
        });
    });


    // COLUMN CHECKBOX CLICK
    $(".columnPercentageCheckbox").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var opacity1 = this.getElementsByTagName("span")[0].style.opacity;
        this.getElementsByTagName("span")[0].style.opacity = ""+(1-opacity1);
        var oldopacity1 = opacity1;

        var checkboxColno = this.getAttribute("data-colno");
        var checkboxTableno = this.getAttribute("data-tableno");

        // TODO REMOVE PERCENTAGES
        $("span").filter("[data-celltableno="+checkboxTableno+"]").each(function () {this.innerHTML = "";});
        // TODO REMOVE ROW CHECKBOXES
        $(".rowPercentageCheckbox").filter("[data-tableno="+checkboxTableno+"]").each(function () {
            this.getElementsByTagName("span")[0].style.opacity = "0"
        });
        $("button[data-function='reset']").filter("[data-tableno="+checkboxTableno+"]").get(0).setAttribute("data-rowList",""); // RESET THE ROWLIST IN THE RESET BUTTON


        var tempColList;
        var colPercentageCheckboxList = [];
        tempColList = $("button[data-function='reset']").filter("[data-tableno="+checkboxTableno+"]").get(0).getAttribute("data-colList");
        if(tempColList.length != 0){colPercentageCheckboxList = tempColList.split(",");}
        tempColList = "";

        if(oldopacity1 == 1){
            colPercentageCheckboxList = colPercentageCheckboxList.filter(function (tempi) { return tempi != checkboxColno;});
            if(colPercentageCheckboxList.length == 1){
                tempColList =  $("th").filter("[data-colno="+colPercentageCheckboxList[0]+"]").filter("[data-tableno="+checkboxTableno+"]").get(0).getAttribute("data-relatedCols").split(",");
                // RELATED COLS ARE OBTAINED
                // TODO PRINT PERCENTAGES
                var numberOfRows = $("tr").filter("[data-tableno="+checkboxTableno+"]").length;
                for(theRowIndex = 0;theRowIndex < numberOfRows; theRowIndex++){
                    var theDivider = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+colPercentageCheckboxList[0]+"]").get(0).getAttribute("sorttable_customkey");

                    $.each(tempColList, function( ignore1, theColumnIndex ) {
                        var theDivident = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");
                        $("span").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).innerHTML = ""+(((parseFloat(theDivident))/parseFloat(theDivider))*100).toFixed(2)+" %";
                    });
                }
            }else if (colPercentageCheckboxList.length == 0){}
        }else if (oldopacity1 == 0) {
            if (colPercentageCheckboxList.length == 2) {
                // TODO LIMIT MAXIMUM SELECTED BOX NUMBER TO 2
                deleteCheckboxColno = colPercentageCheckboxList[colPercentageCheckboxList.length - 1];
                colPercentageCheckboxList = colPercentageCheckboxList.filter(function (tempi) {
                    return tempi != deleteCheckboxColno;
                });
                $(".columnPercentageCheckbox").filter("[data-tableno=" + checkboxTableno + "]").filter("[data-colno=" + deleteCheckboxColno + "]").get(0).getElementsByTagName("span")[0].style.opacity = "0";
            }
            colPercentageCheckboxList.push(checkboxColno);
            if (colPercentageCheckboxList.length == 1) {
                tempColList = $("th").filter("[data-colno=" + colPercentageCheckboxList[0] + "]").filter("[data-tableno=" + checkboxTableno + "]").get(0).getAttribute("data-relatedCols").split(",");
                // RELATED COLS ARE OBTAINED
                // TODO PRINT PERCENTAGES
                var numberOfRows = $("tr").filter("[data-tableno=" + checkboxTableno + "]").length;
                for (theRowIndex = 0; theRowIndex < numberOfRows; theRowIndex++) {
                    var theDivider = $("td").filter("[data-celltableno=" + checkboxTableno + "]").filter("[data-cellrowno=" + theRowIndex + "]").filter("[data-cellcolno=" + colPercentageCheckboxList[0] + "]").get(0).getAttribute("sorttable_customkey");

                    $.each(tempColList, function (ignore1, theColumnIndex) {
                        var theDivident = $("td").filter("[data-celltableno=" + checkboxTableno + "]").filter("[data-cellrowno=" + theRowIndex + "]").filter("[data-cellcolno=" + theColumnIndex + "]").get(0).getAttribute("sorttable_customkey");
                        $("span").filter("[data-celltableno=" + checkboxTableno + "]").filter("[data-cellrowno=" + theRowIndex + "]").filter("[data-cellcolno=" + theColumnIndex + "]").get(0).innerHTML = "" + (((parseFloat(theDivident)) / parseFloat(theDivider)) * 100).toFixed(2) + " %";
                    });
                }
            } else if (colPercentageCheckboxList.length == 2) {
                // TODO FIND PERCENTAGE BTW TWO
                var theDividerIndex = colPercentageCheckboxList[0];
                var theDividentIndex = colPercentageCheckboxList[colPercentageCheckboxList.length - 1];
                var numberOfRows = $("tr").filter("[data-tableno=" + checkboxTableno + "]").length;
                for (theRowIndex = 0; theRowIndex < numberOfRows; theRowIndex++) {
                    var theDivider = $("td").filter("[data-celltableno=" + checkboxTableno + "]").filter("[data-cellcolno=" + theDividerIndex + "]").filter("[data-cellrowno=" + theRowIndex + "]").get(0).getAttribute("sorttable_customkey");
                    var theDivident = $("td").filter("[data-celltableno=" + checkboxTableno + "]").filter("[data-cellcolno=" + theDividentIndex + "]").filter("[data-cellrowno=" + theRowIndex + "]").get(0).getAttribute("sorttable_customkey");
                    $("span").filter("[data-celltableno=" + checkboxTableno + "]").filter("[data-cellcolno=" + theDividentIndex + "]").filter("[data-cellrowno=" + theRowIndex + "]").get(0).innerHTML = "" + (((parseFloat(theDivident)) / parseFloat(theDivider)) * 100).toFixed(2) + " %";
                }
            }
        }


        $("button[data-function='reset']").filter("[data-tableno="+checkboxTableno+"]").each(function () {
            tempString = colPercentageCheckboxList.join(",");
            if(tempString.substr(0,1)==','){tempString=tempString.substr(1,tempString.length);}
            this.setAttribute("data-colList",tempString);
        });
    });


    // ROW CHECKBOX CLICK
    $(".rowPercentageCheckbox").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var opacity1 = this.getElementsByTagName("span")[0].style.opacity;
        this.getElementsByTagName("span")[0].style.opacity = ""+(1-opacity1);
        var oldopacity1 = opacity1;

        var checkboxRowno = this.getAttribute("data-rowno");
        var checkboxTableno = this.getAttribute("data-tableno");

        // TODO REMOVE PERCENTAGES
        $("span").filter("[data-celltableno="+checkboxTableno+"]").each(function () {this.innerHTML = "";});
        // TODO REMOVE COLUMN CHECKBOXES
        $(".columnPercentageCheckbox").filter("[data-tableno="+checkboxTableno+"]").each(function () {
            this.getElementsByTagName("span")[0].style.opacity = "0"
        });
        $("button[data-function='reset']").filter("[data-tableno="+checkboxTableno+"]").get(0).setAttribute("data-colList",""); // RESET THE COLLIST IN THE RESET BUTTON


        var tempRowList;
        var rowPercentageCheckboxList = [];
        tempRowList = $("button[data-function='reset']").filter("[data-tableno="+checkboxTableno+"]").get(0).getAttribute("data-rowList");
        if(tempRowList.length != 0){rowPercentageCheckboxList = tempRowList.split(",");}
        tempRowList = "";

        if(oldopacity1 == 1){
            rowPercentageCheckboxList = rowPercentageCheckboxList.filter(function (tempi) { return tempi != checkboxRowno;});
            if(rowPercentageCheckboxList.length == 1){
                tempRowList =  $("tr").filter("[data-index="+rowPercentageCheckboxList[0]+"]").filter("[data-tableno="+checkboxTableno+"]").get(0).getAttribute("data-relatedRows").split(",");
                // RELATED ROWS ARE OBTAINED
                // TODO PRINT PERCENTAGES
                var numberOfColumns = $("th").filter("[data-tableno="+checkboxTableno+"]").length;
                for(theColumnIndex = 0;theColumnIndex < numberOfColumns; theColumnIndex++){
                    var theDivider = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+rowPercentageCheckboxList[0]+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");

                    $.each(tempRowList, function( ignore1, theRowIndex ) {
                        var theDivident = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");
                        $("span").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).innerHTML = ""+(((parseFloat(theDivident))/parseFloat(theDivider))*100).toFixed(2)+" %";
                    });
                }
            }else if (rowPercentageCheckboxList.length == 0){}
        }else if (oldopacity1 == 0){
            if(rowPercentageCheckboxList.length == 2){
                // TODO LIMIT MAXIMUM SELECTED BOX NUMBER TO 2
                deleteCheckboxRowno = rowPercentageCheckboxList[rowPercentageCheckboxList.length-1];
                rowPercentageCheckboxList = rowPercentageCheckboxList.filter(function (tempi) { return tempi != deleteCheckboxRowno;});
                $(".rowPercentageCheckbox").filter("[data-tableno="+checkboxTableno+"]").filter("[data-rowno="+deleteCheckboxRowno+"]").get(0).getElementsByTagName("span")[0].style.opacity = "0";
            }
            rowPercentageCheckboxList.push(checkboxRowno);
            if(rowPercentageCheckboxList.length == 1){
                tempRowList = $("tr").filter("[data-index="+rowPercentageCheckboxList[0]+"]").filter("[data-tableno="+checkboxTableno+"]").get(0).getAttribute("data-relatedRows").split(",");

                // RELATED ROWS ARE OBTAINED
                // TODO PRINT PERCENTAGES
                var numberOfColumns = $("th").filter("[data-tableno="+checkboxTableno+"]").length;
                for(theColumnIndex = 0;theColumnIndex < numberOfColumns; theColumnIndex++){
                    var theDivider = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+rowPercentageCheckboxList[0]+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");

                    $.each(tempRowList, function( ignore1, theRowIndex ) {
                        var theDivident = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");
                        $("span").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theRowIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).innerHTML = ""+(((parseFloat(theDivident))/parseFloat(theDivider))*100).toFixed(2)+" %";
                    });
                }
            }else if(rowPercentageCheckboxList.length == 2){
                // TODO FIND PERCENTAGE BTW TWO
                var theDividerIndex = rowPercentageCheckboxList[0];
                var theDividentIndex = rowPercentageCheckboxList[rowPercentageCheckboxList.length-1];
                var numberOfColumns = $("th").filter("[data-tableno="+checkboxTableno+"]").length;
                for(theColumnIndex = 0;theColumnIndex < numberOfColumns; theColumnIndex++){
                    var theDivider = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theDividerIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");
                    var theDivident = $("td").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theDividentIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).getAttribute("sorttable_customkey");
                    $("span").filter("[data-celltableno="+checkboxTableno+"]").filter("[data-cellrowno="+theDividentIndex+"]").filter("[data-cellcolno="+theColumnIndex+"]").get(0).innerHTML = ""+(((parseFloat(theDivident))/parseFloat(theDivider))*100).toFixed(2)+" %";
                }
            }
        }


        $("button[data-function='reset']").filter("[data-tableno="+checkboxTableno+"]").each(function () {
            tempString = rowPercentageCheckboxList.join(",");
            if(tempString.substr(0,1)==','){tempString=tempString.substr(1,tempString.length);}
            this.setAttribute("data-rowList",tempString);
        });
    });
});




function exportTable(tableno,tablerequest) {
    // var tableno = exportButton.getAttribute("data-tableno");
    // var $table = $("table").filter("[data-tableno="+tableno+"]").get(0);
    //
    // var csv = "";
    // $.each(($table).rows,function () {
    //     var tempText = this.textContent;
    //     tempText = tempText.replace("Export","");
    //     tempText = tempText.replace("Reset","Table");
    //     tempText = tempText.trim();
    //     tempText = tempText.replace(/(\S)\s(\S)/g,"$1-$2");
    //     //tempText = tempText.replace(/[,]/g,"-");
    //     tempText = tempText.replace(/[\s]+/g,"\t"); //tempText.replace(/[\s]+/g,",");
    //     csv += tempText;
    //     csv += "\n";
    //      // csv += this.textContent.trim().replace(/[\s]+/g,"\t\t"); // /[.*+?^${}()|[\]\\]/g, "\\$&"
    //      // csv += "\n";
    // });

    tablerequest = tablerequest.replace(/.+\?(.*)/,"$1");
    part1 = tablerequest.match(/.*main=/g);
    part2 = tablerequest.replace(/.*main=/g,"").replace(/&succeeding=.*/,"").split(/%2C|,/)[parseInt(tableno)];
    part3 = tablerequest.match(/&succeeding=.*/g)

    tablerequest = part1+part2+part3;

    var export_url = '/exportTable?'+tablerequest;
    window.location.href = export_url;


}
