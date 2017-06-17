$(document).ready(function(e) {
	$('#dropdown1').keyup(function(e) {
	     if (e.keyCode == 13) {
	    	 e.preventDefault()
	    	 addToBox(1);
	    }
	});
	$('#dropdown2').keyup(function(e) {
	     if (e.keyCode == 13) {
	    	 e.preventDefault()
	    	 addToBox(2);
	    }
	});
	
	var onSubmitFunc = function(event){
		event.preventDefault(); //The form wouln't be submitted Yet.
		$('#prepareAnalysisForm').off('submit', onSubmitFunc); //It will remove this handle and will submit the form again if it's all ok.
		def = selectAll();
	    def.then(function(){
			$('#prepareAnalysisForm').submit();
		});
	};
	$('#prepareAnalysisForm').on('submit', onSubmitFunc);
	
});


function addToBox(boxNumber){
	selectedID = $('#dropdown'+boxNumber+' :selected').val();
	selectedName = $('#dropdown'+boxNumber+' :selected').html();
	var newListItem = $("<option class='chosenVar' id='chosenVarOption_box"+boxNumber+"_"+selectedID+"'></option>");
	newListItem.attr("value",selectedID);
	newListItem.html(selectedName);
	$('#chooseAnalVarSelect'+boxNumber).append(newListItem);
	refreshOptions();
}

function addAllToBox(boxNumber){
	$('.hiddenVar').each(function(){
		varid = $(this).attr('id');
		name = $(this).html();
		if( !$('#chosenVarOption_box1_'+varid).length && !$('#chosenVarOption_box2_'+varid).length ){
			//Now we're sure the element is not in any of the two big boxes;
			var newListItem = $("<option class='chosenVar' id='chosenVarOption_box"+boxNumber+"_"+varid+"'></option>");
			newListItem.val(varid);
			newListItem.html(name);
			$('#chooseAnalVarSelect'+boxNumber).append(newListItem);
		}
	});
	refreshOptions();
}

function removeFromBox(boxNumber){
	$('#chooseAnalVarSelect'+boxNumber).find(":selected").remove();
	refreshOptions();
}

function refreshOptions(){
	$('#dropdown1').empty();
	$('#dropdown2').empty();
	$('.hiddenVar').each(function(){
		varid = $(this).attr('id');
		name = $(this).html();
		if( !$('#chosenVarOption_box1_'+varid).length && !$('#chosenVarOption_box2_'+varid).length ){
			//Now we're sure the element is not in any of the two big boxes;
			var newListItem = $("<option id='option_1_"+varid+"'></option>");
			newListItem.val(varid);
			newListItem.html(name);
			newListItem2 = newListItem.clone();
			newListItem2.attr('id',"option_2_"+varid);
			$('#dropdown1').append(newListItem);
			$('#dropdown2').append(newListItem2);
		}
	});
}

function selectAll(){
	def = $.Deferred();
	$('.chosenVar').each(function(){
		$(this).attr('selected','selected');
	});
	return def.resolve();
}






