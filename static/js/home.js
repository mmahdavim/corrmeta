$(document).ready(function(e) {

	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
	
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
	
	refreshProjsList();

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
	var confirmed = confirm("Please make sure you have a backup! Do you still want to proceed?");
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