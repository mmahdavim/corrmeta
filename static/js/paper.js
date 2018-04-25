$(document).ready(function(e) {
	
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
	
	var paperID = $('#paperID').html();
	
	$(document).on('submit', '#paperForm', function(event){
		event.preventDefault();
		
	});
	
	$(document).on('submit', '#newVarForm', function(event){
		event.preventDefault();
		addVariableClicked();
	});
	
	refreshCorTable();
	
	
	$("#waitingImage").css("visibility", 'hidden');
	$(document).ajaxStart(function(){
	    $("#waitingImage").css("visibility", 'visible');
	});

	$(document).ajaxComplete(function(){
		$("#waitingImage").css("visibility", 'hidden');
	});
	
});

/////////////////////////////////////

function removeVariableClicked(varRowpos){
	var confirmed = confirm("Are you sure you want to remove this variable from this paper?");
	if (confirmed == false){
		return;
	}
	varid = $('#var_'+varRowpos).html();
	$.ajax({
        url : "../detatchVariable/"+paperID+"/",
        type : "POST", // http method
        data : {"varid":varid}, 
        success : function(message) {
			if(message==="Error"){
				alert("Somethign went wrong. The variable was not removed from the paper.")
			}
			else{
				refreshHiddenDivs();
				refreshCorTable();
			}
        },
        error : function(xhr,errmsg,err) {
            alert("Somethign went wrong. The variable was not removed from the paper.")
        }
    });
}

function moveRow(varRowpos,offset){
	otherVarRowpos = parseInt(varRowpos)+parseInt(offset);
	thisID = $('#var_'+varRowpos).html();
	otherID = $('#var_'+otherVarRowpos).html();
	request = $.ajax({
        url : "../moverow/"+paperID+"/",
        type : "POST", // http method
        data : {"thisid":thisID, "otherid":otherID}, 
        success : function(message) {
			if(message==="Error"){
				alert("Something went wrong. The order of the rows was not changed.");
			}
			else{
				$.when({}).then(function(){
					refreshHiddenDivs();
					return def;
				}).then(function(){
					fillCorTable();
					$('#id_variable-name').hide();
					$('#saveNewVarButton').prop("disabled",true);
				})
			}
        },
        error : function(xhr,errmsg,err) {
            alert("Something went wrong. The order of the rows was not changed.");
        }
    });
}

function addVariableClicked(){
	selected = $('#dropdown :selected').val();
	paperID = $('#paperID').html();
	if(selected === "createnew"){
		userInput = $('#id_variable-name').val();
		if(userInput.length<1){
			alert('Please enter a name for the new variable!')
			return;
		}
		//This is where we add a brand new variable to the DB
		addVariableAjax(userInput,paperID,"New");
	}
	else{
		if(selected === "_blank_"){
			alert('Something went wrong. No new variable was added.')
			return;
		}
		//This is where we add an existing variable to the paper.
		addVariableAjax(selected,paperID,"Existing");
	}
	
}

function addVariableAjax(userInput,paperID,newOrExisting){
	theData = {"thevar":userInput};
	if(newOrExisting==="New"){
		theData = $('#newVarForm').serialize();
	}
	$.ajax({
        url : "../add"+newOrExisting+"Variable/"+paperID+'/',
        type : "POST", // http method
        data : theData, 
        success : function(message) {
			if(message==="Error"){
				alert("Something went wrong. Please make sure you entered a valid variable name.")
				return;
			}
			$('#hiddenCode').html(message);
			refreshCorTable();
        },
        error : function(xhr,errmsg,err) {
            alert("ERROR: "+errmsg)
        }
    });
}

function dropdownChanged(){
	selected = $('#dropdown :selected').val();
	if(selected === "createnew"){
		$('#id_variable-name').show();
	}
	else{
		$('#id_variable-name').hide();
	}
	if(selected === "_blank_"){
		$('#saveNewVarButton').prop("disabled",true);
	}
	else{
		$('#saveNewVarButton').prop("disabled",false);
	}
	$('#saveNewVarButton').focus();
}

function refreshHiddenDivs(){
	paperID = $('#paperID').html();
	def = $.ajax({
        url : "../gethiddendivs/"+paperID+"/",
        type : "POST", // http method
        data : {}, 
        success : function(message) {
			$('#hiddenCode').html(message);
        },
        error : function(xhr,errmsg,err) {
            alert("ERROR: "+errmsg)
        }
    });
	return def;
}

function buildCorTable(){
	paperID = $('#paperID').html();
	def = $.ajax({
        url : "../corTable/"+paperID+"/",
        type : "POST", // http method
        data : {}, 
        success : function(message) {
			$('#corTable').html(message);
        },
        error : function(xhr,errmsg,err) {
            alert("ERROR: "+errmsg)
        }
    });
	return def;		//def is the Deferred object that is used for asynchronous execution
}


function fillCorTable(){
	//We get the values from the hidden elements and inject them into the correlation table
	varCount = parseInt($('#var_count').html());
	//The first row and first column
	for(var i=0; i<varCount; i++){
		ii = i+1;
		title = $('#var_'+ii).attr('data-name');
		$('#firstRow_'+ii).html(title);
		$('#firstCol_'+ii).html("<span style='color:gray'>"+ii+". </span>"+title);
	}
	//The body of the table
	for(var i=0; i<varCount; i++){
		ii = i+1;
		firstVar = $('#var_'+ii).html();
		for(var j=0; j<varCount; j++){
			jj = j+1;
			if(i>j){
				secondVar = $('#var_'+jj).html();
				hashName1 = firstVar+"____"+secondVar;
				hashName2 = secondVar+"____"+firstVar;
				value = ""
				if($('#'+hashName1).length == 0){
					if($('#'+hashName2).length != 0){
						value = $('#'+hashName2).html();
					}
				}
				else{
					value = $('#'+hashName1).html();
				}
				$('#cell_'+ii+'_'+jj).html("<input class='corInput' id='corInput_"+ii+"_"+jj+"' type='textfield' value='"+value+"' data-initial='"+value+"'></input>");
			}
			else if(i==j){
				$('#cell_'+ii+'_'+jj).html(1);
			}
			else{
				$('#cell_'+ii+'_'+jj).html("<span style='color:#999'>.</span>");
			}
		}
	}
	
	//The first special columns (mean, SD, etc.)
	for(var i=0; i<varCount; i++){
		ii = i+1;
		theVar = $('#var_'+ii).html();
		mean = $('#'+theVar+"____mean").html();
		sd = $('#'+theVar+"____sd").html();
		alpha = $('#'+theVar+"____alpha").html();
		
		$('#mean_'+ii).html("<input class='corLikeInput' style='border: 1px solid #eee;' id='corLikeInputmean_"+ii+"' type='textfield' value='"+mean+"' data-initial='"+mean+"'></input>");
		$('#SD_'+ii).html("<input class='corLikeInput' style='border: 1px solid #eee;' id='corLikeInputsd_"+ii+"' type='textfield' value='"+sd+"' data-initial='"+sd+"'></input>");
		$('#alpha_'+ii).html("<input class='corLikeInput' style='border: 1px solid #eee;' id='corLikeInputalpha_"+ii+"' type='textfield' value='"+alpha+"' data-initial='"+alpha+"'></input>");
	}
}



function refreshCorTable(){
	buildCorTable().then(function(){
		fillCorTable();
		$('#id_variable-name').hide();
		$('#saveNewVarButton').prop("disabled",true);
	});
}


function saveEverything(){
	feedback = "";
	
	//The general paper info part (Paper Information)
	def = $.ajax({
        url : "../editpaper/"+paperID+'/',
        type : "POST", // http method
        data : $('#editPaperForm').serialize(), 
        success : function(message) {
			if(message==="Done"){
				feedback = "";
			}
			else if(message==="nochange"){
				feedback = message;
			}
			else{
				$('#paperForm').html(message);
				alert("The changes could not be saved. Please enter valid input values for all fields.");
				return;
			}
        },
        error : function(xhr,errmsg,err) {
        	alert("The changes could not be saved. Please enter valid input values for all fields.");
        	return;
        }
    });
	
	//The moderator variables part
	def.then(function(){
		def2 = $.ajax({
	        url : "../editanswers/"+paperID+'/',
	        type : "POST", // http method
	        data : $('#editAnswersForm').serialize(), 
	        success : function(message) {
				if(message==="Done"){
					feedback = "";
				}
				else if(message==="nochange"){
					if (feedback==="nochange"){
						//if the previous parts got "no change" too:
						feedback = "nochange";
					}
				}
				else{
					alert("The changes could not be saved. Please make sure yout input is valid.");
					return;
				}
	        },
	        error : function(xhr,errmsg,err) {
	            alert("The changes could not be saved. Please make sure yout input is valid.");
	            return;
	        }
	    });
		
		
		
		//The correlation table part:
		def2.then(function(){
			corData = {}
			$('.corInput').each(function(){
				//if the value for it had changed:
				if($(this).val()!=$(this).attr("data-initial")){
					//For this correlation, find the IDs of its variables.
					id = $(this).attr("id");
					row_col = id.substring(9);
					underscoreIndex = row_col.indexOf("_");
					row = row_col.substring(0,underscoreIndex);
					col = row_col.substring(underscoreIndex+1);
					id1 = $('#var_'+row).html();
					id2 = $('#var_'+col).html();
					cor = $(this).val();
					myKey = id1+"_"+id2;
					corData[myKey] = cor;
				}
			});
			$('.corLikeInput').each(function(){
				if($(this).val()!=$(this).attr("data-initial")){
					elementID = $(this).attr("id");
					underscoreIndex = elementID.indexOf("_");
					row = elementID.slice(underscoreIndex+1); //The part after the underscore
					id = $('#var_'+row).html();
					value = $(this).val();
					myKey = elementID.slice(12,underscoreIndex)+"_"+id; //e.g. sd_12, mean_3, etc. where the number is the variable id in the DB
					corData[myKey] = value;
				}
			});
			$.post("../savecorrelations/"+paperID+"/",corData,function(response,status){
				if(status==="success" && response != "Error" && response != "nochange"){
					alert("The values were successfully saved.");
				}
				else if(response === "nochange"){
					if (feedback==="nochange"){
						//if the previous parts got "no change" too:
						alert("No changes were detected.");
					}
					else{
						alert("The values were successfully saved.");
					}
				}
				else{
					alert("Something went wrong. Please make sure the values you have entered are valid.");
					return;
				}
			});
		});
	});
	

}


//////////////////////////////
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}