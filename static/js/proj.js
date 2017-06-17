var selectedVars = {};

$(document).ready(function(e) {
	
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
	
	//Get the content of the papersList box through ajax and add it.
	refreshQuestionsList();
	refreshPapersList();
	
	//Since the button itself is added dynamically, there's a different syntax for capturing its events!!!
	//WRONG: $('#addPaperForm').on('submit', function(event){
	$(document).on('submit', '#addPaperForm', function(event){
		event.preventDefault();
		$.ajax({
	        url : "../addpaper/"+$('#proj_id_div').html()+'/',
	        type : "POST", // http method
	        data : $('#addPaperForm').serialize(), 
	        success : function(newCode) {
			$('#papersListBox').html(newCode);
	        },
	        error : function(xhr,errmsg,err) {
	            alert("ERROR: "+errmsg)
	        }
	    });
	});
	$(document).on('submit', '#addQuestionForm', function(event){
		event.preventDefault();		
		$.ajax({
	        url : "../addquestion/"+$('#proj_id_div').html()+'/',
	        type : "POST", // http method
	        data : $('#addQuestionForm').serialize(), 
	        success : function(newCode) {
			$('#questionsListBox').html(newCode);
	        },
	        error : function(xhr,errmsg,err) {
	            alert("ERROR: "+errmsg)
	        }
	    });
	});
	
	$(document).on('submit', '#projEditForm', function(event){
		event.preventDefault();		
		$.ajax({
	        url : "../editprojtitle/"+$('#proj_id_div').html()+'/',
	        type : "POST", // http method
	        data : $('#projEditForm').serialize(), 
	        success : function(message) {
				if(message==="Done"){
					disableProjTitle();
				}
				else{
					alert('The operation could not be performed. Please make sure you have entered a valid project title.')
				}
	        },
	        error : function(xhr,errmsg,err) {
	            alert("Something went wrong. The change was not performed.")
	        }
	    });
	});
	
	disableProjTitle();
	$('#darkLayer').hide();
	
	fixVarLabelSizes();
	
	$("#waitingImage").css("visibility", 'hidden');
	$(document).ajaxStart(function(){
	    $("#waitingImage").css("visibility", 'visible');
	});

	$(document).ajaxComplete(function(){
		$("#waitingImage").css("visibility", 'hidden');
	});
	
});


function deletePaper(id){
	var confirmed = confirm("Are you sure you want to delete this paper?");
	if (confirmed == false){
		return;
	}
	$.ajax({
        url : "../deletepaper/"+id+'/',
        type : "POST", // http method
        data : "", 
        success : function(message) {
			if (message==="Error"){
				alert("Something went wrong.")
			}
        },
        error : function(xhr,errmsg,err) {
            alert("Something went wrong.")
        }
    });
	refreshPapersList();
}

function refreshPapersList(){
	$.ajax({
        url : "../paperslist/no/"+$('#proj_id_div').html()+'/',
        type : "POST", // http method
        data : "", 
        success : function(newCode) {
        	$('#papersListBox').html(newCode);
        },
        error : function(xhr,errmsg,err) {
            alert("ERROR: "+errmsg)
        }
    });
}

function deleteQuestion(id){
	var confirmed = confirm("Are you sure you want to delete this question? Any answers associated to this question will be deleted too!");
	if (confirmed == false){
		return;
	}
	$.ajax({
        url : "../deletequestion/"+id+'/',
        type : "POST", // http method
        data : "", 
        success : function(message) {
			if (message==="Error"){
				alert("Something went wrong.")
			}
        },
        error : function(xhr,errmsg,err) {
            alert("Something went wrong.")
        }
    });
	refreshQuestionsList();
}

function refreshQuestionsList(){
	$.ajax({
        url : "../questionslist/no/"+$('#proj_id_div').html()+'/',
        type : "POST", // http method
        data : "", 
        success : function(newCode) {
        	$('#questionsListBox').html(newCode);
        },
        error : function(xhr,errmsg,err) {
            alert("ERROR: "+errmsg)
        }
    });
}

function enableProjTitle(){
	$("#id_proj-title").removeAttr('disabled');
	$("#id_proj-title").focus();
	$("#saveProjTitleChangeButton").show();
	$("#cancelProjTitleChangeButton").show();
}

function disableProjTitle(){
	$("#id_proj-title").attr("disabled", "disabled"); 
	$("#saveProjTitleChangeButton").hide();
	$("#cancelProjTitleChangeButton").hide();
}

function openPaperFrame(paperID){
	$('#darkLayer').show();
	$('#paperPopup').fadeIn('fast');
	dfrd = $.post("../paper/"+paperID+"/",function(response,status){
		if(status==="success" && response != "Error"){
			$('#paperPopup').html(response);
		}
		else{
			alert("Something went wrong. The page could not be loaded.");
		}
	});
	dfrd.then(function(){
		$(document).click( function(){
			if( $(event.target).closest('#paperPopup').length == 0 ){
				$('#paperPopup').fadeOut('fast');
				$('#darkLayer').hide();
				$(document).unbind();
			} 
		});
	});
	
	$(document).keyup(function(e) {
	     if (e.keyCode == 27) { 
	    	 $('#paperPopup').fadeOut('fast');
	    	 $('#darkLayer').hide();
	    	 $(document).unbind();
	    }
	});
}

function fixVarLabelSizes(){
	$('.varLabeltf').each(function(i, obj) {
		fixSize($(obj));
	});
}
function fixSize(obj){
	newLen = obj.val().length;
	if(newLen>20){
		newLen = newLen*0.83;
	}
	obj.attr('size', newLen);
	obj.attr("disabled", "disabled");
}

function selectVar(id){
	if(id in selectedVars){
		delete selectedVars[id];
		$('#varLabel_'+id).removeClass('selectedVarLabel');
		$('#varLabel_'+id).addClass('varLabel');
	}
	else{
		selectedVars[id]="";
		$('#varLabel_'+id).addClass('selectedVarLabel');
		$('#varLabel_'+id).removeClass('varLabel');
	}
}

function deleteSelectedVars(){
	$.post("../deletevars/"+$('#proj_id_div').html()+"/",selectedVars,function(response,status){
		if(status==="success" && response != "Error"){
			Object.keys(selectedVars).forEach(function(key) {
				$('#varLabel_'+key).remove();
			});
		}
		else{
			alert("Something went wrong. The variables could not be deleted.");
		}
	});
}

function editVarNameClicked(id){
	//This is to undo the unwanted click effect on the parent div with another dummy click:
	selectVar(id)
	//
	$('#varLabeltf_'+id).removeAttr('disabled');
	$('#varLabeltf_'+id).keyup(function(e) {
		//If the user presses Enter, do it
	     if (e.keyCode == 13) {
	    	 editVarName(id, $('#varLabeltf_'+id).val());
	    	 fixSize($('#varLabeltf_'+id));
	    }
	   //If the user presses Escape, cancel
	     else if (e.keyCode == 27) {
	    	 $('#varLabeltf_'+id).attr("disabled", "disabled");
	    	 initial = $(this).attr("data-initialVal"); 
	    	 $(this).val(initial);
	     }
	});
	//If the user clicks outside the box, cancel
	setTimeout(function(){
		$(document).click( function(event){
		if( $('#varLabeltf_'+id).attr("disabled") ){
			return;
		}
		if( $(event.target).closest('#varLabeltf_'+id).length == 0 ){
			$('#varLabeltf_'+id).attr("disabled", "disabled");
	    	 initial = $('#varLabeltf_'+id).attr("data-initialVal"); 
	    	 $('#varLabeltf_'+id).val(initial);
		} 
		});
	},800);
}

function editVarName(id, newVal){
	result = "";
	def = $.post("../editvarname/"+$('#proj_id_div').html()+"/",{"id":id,"name":newVal},function(response,status){
		if(status==="success" && response != "Error"){
			result = "Done";
		}
		else{
			console.log(status+"-----"+response)
			result = "Error";
		}
	});
	def.then(function(){
		if (result != "Done"){
			 initial = $(this).attr("data-initialVal");
			 $(this).val(initial);
		 }
		 $('#varLabeltf_'+id).attr("disabled", "disabled");
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

