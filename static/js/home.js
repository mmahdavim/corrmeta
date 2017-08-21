$(document).ready(function(e) {

	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
	
	$('#darkLayer').hide();
	$('#importBox').hide();
	
	$(document).on('submit', '#addProjForm', function(event){
		event.preventDefault();
		$.ajax({
	        url : "../addproj/",
	        type : "POST", // http method
	        data : $('#addProjForm').serialize(), 
	        success : function(message) {
				if(message!="Done"){
					alert("The project could not be added. Please make sure yout input is valid.");
				}
				else{
					refreshProjsList();
				}
	        },
	        error : function(xhr,errmsg,err) {
	        	alert("The project could not be added. Please make sure yout input is valid.");
	        }
	    });
	});
	
	$(document).on('submit', '#importForm', function(event){
		event.preventDefault();
		var formData = new FormData($('#importForm')[0]);
		dfr = $.ajax({
	        url : "../importfromfile/",
	        type : "POST", // http method
	        data : formData, 
	        processData: false,
	        contentType: false,
	        success : function(message) {
				alert(message);
	        },
	        error : function(xhr,errmsg,err) {
	            alert("ERROR: "+errmsg)
	        }
	    });
		dfr.then(function(){
			$('#importBox').fadeOut('fast');
			$('#darkLayer').hide();
			refreshProjsList();
		});
	});
	
	refreshProjsList();

	$("#waitingImage").css("visibility", 'hidden');
	$(document).ajaxStart(function(){
		console.log("ajax started");
	    $("#waitingImage").show();
	});

	$(document).ajaxComplete(function(){
		console.log("ajax complete");
		$("#waitingImage").hide();
	});

	
});


function refreshProjsList(){
	$.ajax({
        url : "../projslist/",
        type : "POST", // http method
        data : "", 
        success : function(newCode) {
			$('#projsTableContainer').empty();
        	$('#projsTableContainer').html(newCode);
        },
        error : function(xhr,errmsg,err) {
            alert("ERROR: "+errmsg)
        }
    });
}

function deleteProj(projid){
	var confirmed = confirm("Are you sure you want to delete this project? All data will be lost!");
	if (confirmed == false){
		return;
	}
	var confirmed = confirm("All data for this project will be lost! Please make sure you have a backup. Do you still want to proceed?");
	if (confirmed == false){
		return;
	}
	$.ajax({
        url : "../deleteproj/"+projid+'/',
        type : "POST", // http method
        data : "", 
        success : function(message) {
			if (message==="Error"){
				alert("Something went wrong.")
			}
			else{
				refreshProjsList();
			}
        },
        error : function(xhr,errmsg,err) {
            alert("Something went wrong.")
        }
    });
}

function openImportBox(){
	$('#darkLayer').show();
	$.when($('#importBox').fadeIn('fast')).then(function(){
		$(document).click( function(){
			if( $(event.target).closest('#importBox').length == 0 ){
				$('#importBox').fadeOut('fast');
				$('#darkLayer').hide();
				$(document).unbind();
			} 
		});
	});
	
	$(document).keyup(function(e) {
	     if (e.keyCode == 27) { 
	    	 $('#importBox').fadeOut('fast');
	    	 $('#darkLayer').hide();
	    	 $(document).unbind();
	    }
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